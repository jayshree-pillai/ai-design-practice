"""Exercise 10: complete LangGraph supervisor solution.

INSTALL (inside your project environment):
    python -m pip install "langgraph>=1,<2"
RUN ALL PROVIDED EXAMPLES:
    python supervisor_langgraph_solution.py

Read the numbered sections 1-8 first. They implement the supervisor.
The original supplied mocks, contracts and fixtures are included in this file.
Only planning, coordination, one focused follow-up and finalization are needed.
Each node returns only the state fields it changes. Specialist calls are
sequential. Each request receives fresh state; no checkpointing is needed.

Flow:
    plan -> clarify -> END
    plan -> call_initial -> review -> finalize -> END
    review -> follow_up -> review (the shared budget allows this only once)

The review after a follow-up stops further calls. Finalize inspects the latest
results to compute answered/partial/failed and preserve supported evidence.
Mocks return structured errors, so exceptions are not part of their contract.

Expected scenarios and call counts appear in EXAMPLES near the end.
This is a worked practice solution, not a claim about interview starter code.
"""

from copy import deepcopy
from pprint import pprint
from typing import Literal, TypedDict

from langgraph.graph import StateGraph, START, END


# PROVIDED CONTRACTS — use these as ordinary Python dictionaries.
Source = Literal["document", "account"]


class Plan(TypedDict):
    required_sources: list[Source]
    clarification_question: str | None


class Task(TypedDict):
    customer_id: str
    question: str


class SpecialistResult(TypedDict):
    status: Literal["sufficient", "insufficient", "error"]
    findings: list[str]
    evidence_ids: list[str]
    error: str | None


class SupervisorResult(TypedDict):
    status: Literal["answered", "partial", "failed", "clarification"]
    answer: str
    evidence_ids: list[str]
    issues: dict[str, str]
    call_count: int


# 1. SUPERVISOR STATE — information shared by the graph's nodes.
class SupervisorState(TypedDict):
    customer_id: str
    question: str
    required_sources: list[Source]
    clarification_question: str | None
    results: dict[Source, SpecialistResult]
    call_count: int
    followup_used: bool
    followup_source: Source | None
    response: SupervisorResult | None


# 2. PLAN — use the supplied mock to identify required sources.
def plan_request(state: SupervisorState):
    plan = planning_mock(state["question"])
    return {
        "required_sources": plan["required_sources"],
        "clarification_question": plan["clarification_question"],
    }


def route_after_plan(state: SupervisorState) -> Literal["clarify", "call_initial"]:
    if state["clarification_question"] is not None:
        return "clarify"
    return "call_initial"


def clarify(state: SupervisorState):
    return {
        "response": {
            "status": "clarification",
            "answer": state["clarification_question"],
            "evidence_ids": [],
            "issues": {},
            "call_count": 0,
        }
    }


# 3. INITIAL CALLS — each required specialist runs once, sequentially.
def call_initial(state: SupervisorState):
    results = {}
    call_count = 0

    for source in state["required_sources"]:
        task: Task = {
            "customer_id": state["customer_id"],
            "question": state["question"],
        }
        if source == "document":
            results[source] = document_specialist(task)
        else:
            results[source] = account_specialist(task)
        call_count += 1

    return {"results": results, "call_count": call_count}


# 4. REVIEW — inspect results and choose the only permitted follow-up.
def review(state: SupervisorState):
    # Inspect the latest results every time this node runs.
    for source in ("document", "account"):
        if source in state["required_sources"]:
            result = state["results"][source]
            if result["status"] == "insufficient" and not state["followup_used"]:
                return {"followup_source": source}

    # Clear any previous selection when the budget is used or none qualify.
    return {"followup_source": None}


def route_after_review(state: SupervisorState) -> Literal["follow_up", "finalize"]:
    if state["followup_source"] is not None:
        return "follow_up"
    return "finalize"


# 5. FOLLOW-UP — replace one result while preserving the other source.
def follow_up(state: SupervisorState):
    source = state["followup_source"]
    if source is None or state["followup_used"]:
        raise ValueError("No follow-up is available")

    original_task: Task = {
        "customer_id": state["customer_id"],
        "question": state["question"],
    }
    focused_task = followup_mock(source, original_task)

    if source == "document":
        new_result = document_specialist(focused_task)
    else:
        new_result = account_specialist(focused_task)

    results = state["results"].copy()
    results[source] = new_result

    return {
        "results": results,
        "call_count": state["call_count"] + 1,
        "followup_used": True,
    }


# 6. FINALIZE — inspect the latest results and build the public response.
def finalize(state: SupervisorState):
    findings = []
    evidence_ids = []
    issues = {}
    successful_sources = 0

    for source in state["required_sources"]:
        result = state["results"][source]
        if result["status"] == "sufficient":
            successful_sources += 1
            findings.extend(result["findings"])
            evidence_ids.extend(result["evidence_ids"])
        elif result["status"] == "insufficient":
            issues[source] = "Insufficient evidence"
        else:
            issues[source] = result["error"] or "Specialist failed"

    if successful_sources == len(state["required_sources"]):
        status = "answered"
    elif successful_sources > 0:
        status = "partial"
    else:
        status = "failed"

    return {
        "response": {
            "status": status,
            "answer": " ".join(findings) if findings else "No supported findings.",
            "evidence_ids": evidence_ids,
            "issues": issues,
            "call_count": state["call_count"],
        }
    }


# 7. GRAPH WIRING — routing functions are not registered as work nodes.
def build_graph():
    builder = StateGraph(SupervisorState)

    builder.add_node("plan", plan_request)
    builder.add_node("clarify", clarify)
    builder.add_node("call_initial", call_initial)
    builder.add_node("review", review)
    builder.add_node("follow_up", follow_up)
    builder.add_node("finalize", finalize)

    builder.add_edge(START, "plan")
    builder.add_conditional_edges("plan", route_after_plan)
    builder.add_edge("clarify", END)
    builder.add_edge("call_initial", "review")
    builder.add_conditional_edges("review", route_after_review)
    builder.add_edge("follow_up", "review")
    builder.add_edge("finalize", END)

    return builder.compile()


# 8. ENTRY POINT — called by the supplied example runner.
def run_supervisor(customer_id: str, question: str) -> SupervisorResult:
    graph = build_graph()
    final_state = graph.invoke({
        "customer_id": customer_id,
        "question": question,
        "required_sources": [],
        "clarification_question": None,
        "results": {},
        "call_count": 0,
        "followup_used": False,
        "followup_source": None,
        "response": None,
    })
    return final_state["response"]


# PROVIDED MOCKS — no implementation work required below this line.
def planning_mock(question: str) -> Plan:
    """Deterministic keyword planner; required_sources is authoritative."""
    sources: list[Source] = []
    text = question.lower()
    if "policy" in text or "document" in text:
        sources.append("document")
    if "account" in text:
        sources.append("account")
    if not sources:
        return {
            "required_sources": [],
            "clarification_question": "Do you mean your policy or your account?",
        }
    return {"required_sources": sources, "clarification_question": None}


_FOCUSED_QUESTIONS: dict[Source, str] = {
    "document": "Find the refund window in the signed policy document.",
    "account": "Look up the current account status by customer ID.",
}


def followup_mock(source: Source, previous_task: Task) -> Task:
    """Return a new focused task; source choice and call budget are YOUR job."""
    return {
        "customer_id": previous_task["customer_id"],
        "question": _FOCUSED_QUESTIONS[source],
    }


def document_specialist(task: Task) -> SpecialistResult:
    return _lookup("document", task)


def account_specialist(task: Task) -> SpecialistResult:
    return _lookup("account", task)


def _sufficient(finding: str, evidence_id: str) -> SpecialistResult:
    return {"status": "sufficient", "findings": [finding],
            "evidence_ids": [evidence_id], "error": None}


def _insufficient() -> SpecialistResult:
    return {"status": "insufficient", "findings": [],
            "evidence_ids": [], "error": None}


def _error(message: str) -> SpecialistResult:
    return {"status": "error", "findings": [],
            "evidence_ids": [], "error": message}


# For each source: [initial result, optional focused result].
# One result means the focused task returns the same outcome.
# IDs and facts are fictional. Lookups are scoped to the supplied customer ID.
_FIXTURES = {
    "C1": {
        "document": [_sufficient("Refund window: 30 days.", "C1-D1")],
        "account": [_sufficient("Account status: active.", "C1-A1")],
    },
    "C2": {
        "document": [_sufficient("Refund window: 21 days.", "C2-D1")],
        "account": [_error("Account service unavailable")],
    },
    "C3": {
        "document": [_sufficient("Refund window: 14 days.", "C3-D1")],
        "account": [_insufficient(),
                    _sufficient("Account status: active.", "C3-A1")],
    },
    "C4": {
        "document": [_insufficient()],
        "account": [_sufficient("Account status: suspended.", "C4-A1")],
    },
    "C5": {
        "document": [_insufficient(),
                     _sufficient("Refund window: 7 days.", "C5-D1")],
        "account": [_insufficient(),
                    _sufficient("Account status: active.", "C5-A1")],
    },
    "C6": {
        "document": [_sufficient("Refund window: 60 days.", "C6-D1")],
        "account": [_sufficient("Account status: closed.", "C6-A1")],
    },
}


def _lookup(source: Source, task: Task) -> SpecialistResult:
    customer = _FIXTURES.get(task["customer_id"])
    if customer is None:
        return _error("No fixture available for this customer")
    outcomes = customer[source]
    is_focused = task["question"] == _FOCUSED_QUESTIONS[source]
    index = 1 if is_focused and len(outcomes) > 1 else 0
    # Each call returns its own dict/lists. No global call counters or state.
    return deepcopy(outcomes[index])


# Examples are supplied; you do not need to design test cases.
# Columns: description, customer, question, expected status, expected calls.
EXAMPLES = [
    ("Document only", "C1", "What is my refund policy?", "answered", 1),
    ("Account only", "C1", "What is my account status?", "answered", 1),
    ("Both succeed", "C1", "Check my policy and account.", "answered", 2),
    ("Clarification", "C1", "Can you help me?", "clarification", 0),
    ("Account error", "C2", "Check my policy and account.", "partial", 2),
    ("Follow-up succeeds", "C3", "Check my policy and account.", "answered", 3),
    ("Still insufficient", "C4", "Check my policy and account.", "partial", 3),
    ("No usable evidence", "C4", "What is my refund policy?", "failed", 2),
    ("Both insufficient: document gets only follow-up", "C5",
     "Check my policy and account.", "partial", 3),
    ("New customer: only C6-D1 evidence, fresh count", "C6",
     "What is my refund policy?", "answered", 1),
]


def main() -> None:
    for label, customer_id, question, expected_status, expected_calls in EXAMPLES:
        print(f"\n{label} | {customer_id}")
        print(f"Expected: {expected_status}, {expected_calls} specialist call(s)")
        pprint(run_supervisor(customer_id, question))


if __name__ == "__main__":
    main()
