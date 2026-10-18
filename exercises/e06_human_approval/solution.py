"""Acceptance tests for exercise 04; not implemented yet.

Translate the requirements and verification cases in problem.md into tests.
No placeholder passing tests are supplied.
"""

from typing import TypedDict
from langgraph.types import interrupt,Command
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver

# Mock tools.
def get_balance():
    return 500


def refund(amount):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return f"Mock refund of {amount} completed"

TOOLS = {"get_balance": get_balance, "refund": refund}

class AgentState(TypedDict):
    request:str
    amount:float
    proposed_tool: str
    proposed_args: dict
    human_decision:str
    tool_result : dict

def proposed_tool(state:AgentState):
    if state["request"]=="refund":
        return {
            "proposed_tool":"refund",
            "proposed_args":{"amount":state["amount"]}
        }
    return{
        "proposed_tool":"get_balance",
        "proposed_args":{}
    }

def route_after_propose(state:AgentState):
    if state["proposed_tool"]=="get_balance":
        return "execute"
    return "approval"

def approval(state: AgentState):
    # Proposed action set for HITL and stop
    decision = interrupt(
        {
            "tool": state["proposed_tool"],
            "args":state["proposed_args"],
                        
        }
    )
    #after resume record human response
    return {"human_decision": decision}

def route_after_decision(state:AgentState):
    if state["human_decision"] == "approve":
        return "execute"
    return "reject"

def reject(state:AgentState):
    return {
        "tool_result":{
            "success":False,
            "result":None,
            "error":"Human approval not granted"

        }
    }    

def execute_tool(state: AgentState):
    try:
        if state["proposed_tool"] == "get_balance":
            result = get_balance()

        elif state["proposed_tool"] == "refund":
            amount = state["proposed_args"]["amount"]
            result = refund(amount)

        else:
            raise ValueError("Unknown tool")

        return {
            "tool_result": {
                "success": True,
                "result": result,
                "error": None,
            }
        }

    except Exception as error:
        return {
            "tool_result": {
                "success": False,
                "result": None,
                "error": str(error),
            }
        }

def main():
    builder = StateGraph(AgentState)

    builder.add_node("proposed_tool", proposed_tool)
    builder.add_node("approval", approval)
    builder.add_node("reject", reject)
    builder.add_node("execute", execute_tool)

    builder.add_edge(START, "propose_tool")
    builder.add_conditional_edge("proposed_tool",route_after_propose)
    builder.add_conditional_edge("approval",route_after_decision)
    builder.add_edge("reject",END)
    builder.add_edge("execute",END)

    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "request-1"}}

    # 2. Prepare the initial state.
    initial_state = {
        "request": "refund",
        "amount": 100,
        "proposed_tool": "",
        "proposed_args": {},
        "human_decision": "",
        "tool_result": {},
    }
    # 3. Run until completion or an interrupt.
    result = graph.invoke(initial_state, config=config)

    if result.get("__interrupt__"):
        proposal = result["__interrupt__"][0].value
        print("Action awaiting approval:", proposal)

        decision = input("Type approve or reject: ").strip().lower()

        # This decision becomes the return value of interrupt().
        result = graph.invoke(
            Command(resume=decision),
            config=config,
        )
    # 5. Display the final outcome.
    print(result["tool_result"])