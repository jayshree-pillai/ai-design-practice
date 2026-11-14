from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

# Uses the exercise's existing planning and specialist functions.
specialists = {
    "document": document_specialist,
    "account": account_specialist,
}


class AgentState(TypedDict):
    task: dict
    sources: list[str]
    results: dict
    followup_source: str | None
    call_count: int
    response: dict


def plan(state):
    decision = planning_mock(state["task"]["question"])

    if decision["clarification_question"] is not None:
        return Command(
            update={"response": {
                "status": "clarification",
                "answer": decision["clarification_question"],
                "evidence_ids": [],
                "issues": {},
                "call_count": 0,
            }},
            goto=END,
        )

    return Command(
        update={"sources": decision["required_sources"]},
        goto="delegate",
    )


def delegate(state):
    results = {}
    for source in state["sources"]:
        results[source] = specialists[source](state["task"])

    followup_source = None
    for source in ("document", "account"):
        if source in results and results[source]["status"] == "insufficient":
            followup_source = source
            break

    return Command(
        update={
            "results": results,
            "call_count": len(results),
            "followup_source": followup_source,
        },
        goto="follow_up" if followup_source else "finalize",
    )


def follow_up(state):
    source = state["followup_source"]
    task = followup_mock(source, state["task"])

    results = state["results"].copy()
    results[source] = specialists[source](task)

    return {
        "results": results,
        "call_count": state["call_count"] + 1,
    }


def finalize(state):
    findings, evidence_ids, issues = [], [], {}

    for source in state["sources"]:
        result = state["results"][source]

        if result["status"] == "sufficient":
            findings.extend(result["findings"])
            evidence_ids.extend(result["evidence_ids"])
        elif result["status"] == "insufficient":
            issues[source] = "Insufficient evidence"
        else:
            issues[source] = result["error"] or "Specialist failed"

    if not issues:
        status = "answered"
    elif len(issues) < len(state["sources"]):
        status = "partial"
    else:
        status = "failed"

    return {"response": {
        "status": status,
        "answer": " ".join(findings) or "No supported findings.",
        "evidence_ids": evidence_ids,
        "issues": issues,
        "call_count": state["call_count"],
    }}


builder = StateGraph(AgentState)
builder.add_node("plan", plan)
builder.add_node("delegate", delegate)
builder.add_node("follow_up", follow_up)
builder.add_node("finalize", finalize)

builder.add_edge(START, "plan")
builder.add_edge("follow_up", "finalize")
builder.add_edge("finalize", END)

graph = builder.compile()


def run_supervisor(customer_id, question):
    result = graph.invoke({
        "task": {"customer_id": customer_id, "question": question},
        "sources": [],
        "results": {},
        "followup_source": None,
        "call_count": 0,
        "response": {},
    })
    return result["response"]
