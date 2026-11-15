from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

MAX_RETRY = 2


class AgentState(TypedDict):
    question: str
    retrieved_docs: Annotated[list[str], add]
    answer: str
    citations: str
    retry_attempts: int
    validation_status: bool


def retrieval(state):
    docs = [
        f"Documents that have semantic relevance to {state['question']}"
    ]
    return {"retrieved_docs": docs}


def generate_answer(state):
    answer = "LLM thinks this is the answer"
    citations = "valid doc links"
    return {"answer": answer, "citations": citations}


def validate_answer(state):
    if "True" in state["citations"]:
        status = True
    else:
        status = False

    return {"validation_status": status}


def route_after_validate(state):
    if state["validation_status"]:
        return END
    else:
        if state["retry_attempts"] < MAX_RETRY:
            return "recover"
        else:
            return "escalate"


def recover(state):
    return {
        "retry_attempts": state["retry_attempts"] + 1,
        "question": f"{state['question']} additional supporting evidence",
    }


def escalate(state):
    return {
        "answer": "Max retries reached; answer could not be found."
    }


def main():
    builder = StateGraph(AgentState)

    builder.add_node("retrieval", retrieval)
    builder.add_node("generate_answer", generate_answer)
    builder.add_node("validate_answer", validate_answer)
    builder.add_node("recover", recover)
    builder.add_node("escalate", escalate)

    builder.add_edge(START, "retrieval")
    builder.add_edge("retrieval", "generate_answer")
    builder.add_edge("generate_answer", "validate_answer")

    builder.add_conditional_edges(
        "validate_answer", route_after_validate
    )

    builder.add_edge("recover", "retrieval")
    builder.add_edge("escalate", END)

    graph = builder.compile()

    result = graph.invoke({
        "question": "some question",
        "retrieved_docs": [],
        "answer": "",
        "citations": "",
        "retry_attempts": 0,
        "validation_status": False,
    })


if __name__ == "__main__":
    main()
