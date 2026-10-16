"""Exercise 05: LangGraph: Evidence Recovery Loop.

Not implemented yet. Complete design.md before writing the first solution.
Keep the implementation within the scope in problem.md.
"""
from langgraph.graph import StateGraph, START, END

MAX_RETRIES = 2


def retrieve(state):
    query = state["query"].lower()
    state["retrieved_docs"] = []

    # Mock search: both keywords are needed.
    if "refund" in query and "policy" in query:
        state["retrieved_docs"] = [
            {"id": "D1", "text": "Refunds are allowed within 30 days."}
        ]

    return state


def generate(state):
    if state["retrieved_docs"]:
        doc = state["retrieved_docs"][0]
        state["answer"] = f"{doc['text']} [{doc['id']}]"
    else:
        state["answer"] = "No supporting evidence found."

    return state


def validate(state):
    state["citation_status"] = "fail"

    # Check that the answer includes the source text and citation.
    if state["retrieved_docs"]:
        doc = state["retrieved_docs"][0]
        citation = f"[{doc['id']}]"

        if doc["text"] in state["answer"] and citation in state["answer"]:
            state["citation_status"] = "pass"

    return state


def route_after_validate(state):
    if state["citation_status"] == "pass":
        return END
    if state["retry_count"] >= MAX_RETRIES:
        return "escalate"
    return "recover"


def recover(state):
    state["retry_count"] += 1

    if state["retry_count"] == 1:
        state["query"] += " policy"
    else:
        state["query"] += " details"

    return state


def escalate(state):
    state["answer"] = "Escalating: could not find enough supporting evidence."
    return state


def main():
    builder = StateGraph(dict)

    builder.add_node("retrieve", retrieve)
    builder.add_node("generate", generate)
    builder.add_node("validate", validate)
    builder.add_node("recover", recover)
    builder.add_node("escalate", escalate)

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", "validate")

    builder.add_conditional_edges("validate", route_after_validate)

    builder.add_edge("recover", "retrieve")
    builder.add_edge("escalate", END)

    graph = builder.compile()

    questions = [
        "What is the refund policy?",
        "Can I get a refund?",
        "What are the parking rules?",
    ]

    for question in questions:
        result = graph.invoke({
            "question": question,
            "query": question,
            "retrieved_docs": [],
            "answer": "",
            "citation_status": "",
            "retry_count": 0,
        })
        print(result["answer"], "Retries:", result["retry_count"])


if __name__ == "__main__":
    main()