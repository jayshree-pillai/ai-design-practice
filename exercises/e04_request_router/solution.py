"""Exercise 04: LangGraph: Simple Request Router.

Not implemented yet. Complete design.md before writing the first solution.
Keep the implementation within the scope in problem.md.
"""
from langgraph.graph import StateGraph, START, END


def route_request(state):
    curr_route = None
    question = state["question"].lower()
    if "document" in question or "pdf" in question or "upload" in question:
        curr_route = "document"
    elif "account" in question or "database" in question or "sql" in question:
        curr_route = "sql"
    else:
        curr_route = "general"

    return curr_route




def document_handler(state):
    state["route"] = "document"
    state["answer"] = "Mock document answer: returns are allowed within 30 days."
    return state


def sql_handler(state):
    state["route"] = "sql"
    state["answer"] = "Mock SQL answer: your account is active."
    return state


def general_handler(state):
    state["route"] = "general"
    state["answer"] = "Mock general answer: an AI agent uses tools to complete tasks."
    return state


def main():
    builder = StateGraph(dict)

    # 1. Register nodes.
    builder.add_node("document", document_handler)
    builder.add_node("sql", sql_handler)
    builder.add_node("general", general_handler)

    # 2. Connect nodes.
    builder.add_conditional_edges(START, route_request)

    builder.add_edge("document", END)
    builder.add_edge("sql", END)
    builder.add_edge("general", END)

    # 3. Compile.
    graph = builder.compile()

    # 4. Run.
    questions = [
        "Summarize the uploaded document",
        "What is my account status?",
        "What is an AI agent?",
    ]

    for question in questions:
        result = graph.invoke({
            "question": question,
            "route": "",
            "answer": "",
        })
        print(result)


if __name__ == "__main__":
    main()
