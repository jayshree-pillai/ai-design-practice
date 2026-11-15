from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command, interrupt


def get_balance():
    return 500


def post_refund(amount):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return f"Refund of {amount} is posted"


TOOLS = {
    "get_balance": get_balance,
    "post_refund": post_refund,
}


class AgentState(TypedDict):
    request: str
    amount: float
    proposed_tool: str
    proposed_args: dict
    human_decision: str
    tool_result: dict


def proposed_tool(state):
    if state["request"] == "refund":
        return {
            "proposed_tool": "post_refund",
            "proposed_args": {"amount": state["amount"]},
        }

    return {
        "proposed_tool": "get_balance",
        "proposed_args": {},
    }


def route_after_propose(state):
    if state["proposed_tool"] == "get_balance":
        return "execute"
    return "approval"


def approval(state):
    decision = interrupt({
        "tool": state["proposed_tool"],
        "args": state["proposed_args"],
    })
    return {"human_decision": decision}


def route_after_decision(state):
    if state["human_decision"] == "approve":
        return "execute"
    return "reject"


def reject(state):
    return {
        "tool_result": {
            "success": False,
            "result": None,
            "error": "Human rejected tool call",
        }
    }


def execute(state):
    try:
        if state["proposed_tool"] == "get_balance":
            result = get_balance()
        elif state["proposed_tool"] == "post_refund":
            result = post_refund(state["proposed_args"]["amount"])
        else:
            raise ValueError("Unknown tool")

        return {
            "tool_result": {
                "success": True,
                "result": result,
                "error": None,
            }
        }

    except Exception as ex:
        return {
            "tool_result": {
                "success": False,
                "result": None,
                "error": str(ex),
            }
        }


def main():
    builder = StateGraph(AgentState)

    builder.add_node("propose", proposed_tool)
    builder.add_node("approval", approval)
    builder.add_node("reject", reject)
    builder.add_node("execute", execute)

    builder.add_edge(START, "propose")
    builder.add_conditional_edges("propose", route_after_propose)
    builder.add_conditional_edges("approval", route_after_decision)
    builder.add_edge("reject", END)
    builder.add_edge("execute", END)

    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "id#1"}}

    initial_state = {
        "request": "refund",
        "amount": 100.0,
        "proposed_tool": "",
        "proposed_args": {},
        "human_decision": "",
        "tool_result": {},
    }

    result = graph.invoke(initial_state, config=config)

    if result.get("__interrupt__"):
        proposal = result["__interrupt__"][0].value
        print("Proposed action:", proposal)

        decision = input("Type approve or reject: ").strip().lower()

        result = graph.invoke(
            Command(resume=decision),
            config=config,
        )

    print(result["tool_result"])


if __name__ == "__main__":
    main()
