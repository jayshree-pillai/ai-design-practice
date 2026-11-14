"""Exercise 11: Customer Support Assistant Using LangGraph.

Not implemented yet. Complete design.md before writing the first solution.
Keep the implementation within the scope in problem.md.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

sources = {
    "help": search_help,
    "order": get_latest_order,
}


class AgentState(TypedDict):
    customer_id: str
    message: str
    source: str
    attempts: int
    response: dict


def classify(state):
    text = state["message"].lower()

    if any(word in text for word in ("policy", "return", "refund")):
        source = "help"
    elif "order" in text:
        source = "order"
    elif "shipping" in text:
        source = "help"
    else:
        return Command(
            update={"response": {
                "status": "clarification",
                "answer": "Are you asking about a policy or your latest order?",
            }},
            goto=END,
        )

    return Command(update={"source": source}, goto="lookup")


def lookup(state):
    attempts = state["attempts"] + 1

    try:
        info = sources[state["source"]](
            state["customer_id"], state["message"]
        )
        status = "answered" if info else "failed"
        answer = info or "I couldn't find information for that request."

    except TimeoutError:
        if attempts == 1:
            return Command(
                update={"attempts": attempts},
                goto="lookup",
            )

        status = "failed"
        answer = "The service is unavailable right now. Please try again later."

    return Command(
        update={
            "attempts": attempts,
            "response": {"status": status, "answer": answer},
        },
        goto=END,
    )


builder = StateGraph(AgentState)
builder.add_node("classify", classify)
builder.add_node("lookup", lookup)
builder.add_edge(START, "classify")

graph = builder.compile()


def run_support(customer_id, message):
    result = graph.invoke({
        "customer_id": customer_id,
        "message": message,
        "source": "",
        "attempts": 0,
        "response": {},
    })
    return result["response"]
