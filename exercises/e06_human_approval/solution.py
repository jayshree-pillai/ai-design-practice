"""Exercise 06: LangGraph: Human Approval Before Tool Execution.

Not implemented yet. Complete design.md before writing the first solution.
Keep the implementation within the scope in problem.md.
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


# Mock tools.
def get_balance():
    return 500


def refund(amount):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return f"Mock refund of {amount} completed"


TOOLS = {"get_balance": get_balance, "refund": refund}


def propose_tool(state):
    if state["request"] == "refund":
        state["proposed_tool"] = "refund"
        state["proposed_args"] = {"amount": state["amount"]}
    else:
        state["proposed_tool"] = "get_balance"
        state["proposed_args"] = {}
    return state


def route_after_propose(state):
    if state["proposed_tool"] == "get_balance":
        return "execute"
    return "approval"


def approval(state):
    state["human_decision"] = interrupt({
        "tool": state["proposed_tool"],
        "args": state["proposed_args"],
    })
    return state


def route_after_approval(state):
    if state["human_decision"] == "approve":
        return "execute"
    return "reject"


def execute_tool(state):
    try:
        tool = TOOLS[state["proposed_tool"]]
        result = tool(**state["proposed_args"])
        state["tool_result"] = {"success": True, "result": result, "error": None}
    except Exception as error:
        state["tool_result"] = {"success": False, "result": None, "error": str(error)}
    return state


def reject(state):
    state["tool_result"] = {
        "success": False,
        "result": None,
        "error": "Request not approved; tool was not executed",
    }
    return state


def main():
    builder = StateGraph(dict)

    builder.add_node("propose", propose_tool)
    builder.add_node("approval", approval)
    builder.add_node("execute", execute_tool)
    builder.add_node("reject", reject)

    builder.add_edge(START, "propose")
    builder.add_conditional_edges("propose", route_after_propose)
    builder.add_conditional_edges("approval", route_after_approval)
    builder.add_edge("execute", END)
    builder.add_edge("reject", END)

    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "request-1"}}

    # Use "balance" for a safe request.
    state = {"request": "refund", "amount": 100}
    result = graph.invoke(state, config)

    if "__interrupt__" in result:
        print("Approval needed:", result["__interrupt__"][0].value)

        decision = input("Type approve or reject: ").strip().lower()
        result = graph.invoke(Command(resume=decision), config)

    print(result["tool_result"])


if __name__ == "__main__":
    main()