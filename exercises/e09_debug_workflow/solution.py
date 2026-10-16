"""Exercise 09: Debug an Existing Agent Workflow.

Not implemented yet. Complete design.md before writing the first solution.
Keep the implementation within the scope in problem.md.
"""
MAX_RECOVERIES = 2


def retrieve(state):
    if state["question_id"] == "Q1":
        ids = ["support"]
    elif state["question_id"] == "Q7":
        ids = ["background"] if state["recovery_attempts"] == 0 else ["support"]
    else:
        ids = []
    return {"retrieved_ids": ids}


def generate(state):
    supported = "support" in state["retrieved_ids"]
    return {
        "answer": "Supported answer" if supported else "Insufficient evidence",
        "citation_ids": ["support"] if supported else [],
    }


def validate(state):
    # FIX: check the current evidence every time.
    valid = (
        "support" in state["retrieved_ids"]
        and bool(state["citation_ids"])
        and set(state["citation_ids"]).issubset(state["retrieved_ids"])
    )
    return {"citation_status": "pass" if valid else "fail"}


def route_after_validate(state):
    if state["citation_status"] == "pass":
        return "done"
    if state["recovery_attempts"] >= MAX_RECOVERIES:
        return "escalate"
    return "recover"


def run(question_id):
    state = {
        "question_id": question_id,
        "recovery_attempts": 0,
        "citation_status": None,
        "retrieved_ids": [],
        "citation_ids": [],
        "answer": "",
    }
    trace = []

    while True:
        state.update(retrieve(state))
        state.update(generate(state))
        state.update(validate(state))
        action = route_after_validate(state)

        trace.append({
            "recovery_attempts": state["recovery_attempts"],
            "retrieved_ids": list(state["retrieved_ids"]),
            "citation_ids": list(state["citation_ids"]),
            "citation_status": state["citation_status"],
            "next_action": action,
        })

        if action in ("done", "escalate"):
            return {**state, "outcome": action, "trace": trace}

        state["recovery_attempts"] += 1


def main():
    # Q7: succeeds after one recovery.
    q7 = run("Q7")
    for event in q7["trace"]:
        print(event)

    assert q7["outcome"] == "done"
    assert q7["recovery_attempts"] == 1
    assert q7["retrieved_ids"] == ["support"]
    assert q7["citation_ids"] == ["support"]
    assert q7["citation_status"] == "pass"
    assert len(q7["trace"]) == 2

    # Q1: succeeds immediately.
    q1 = run("Q1")
    assert q1["outcome"] == "done"
    assert q1["recovery_attempts"] == 0

    # Q2: still fails after Q1, with no passing status carried over.
    q2 = run("Q2")
    assert q2["outcome"] == "escalate"
    assert q2["recovery_attempts"] == 2
    assert len(q2["trace"]) == 3
    assert q2["citation_status"] == "fail"

    print("All regression checks passed.")


if __name__ == "__main__":
    main()

"""
What exposed the bug? At recovery attempt 1, retrieved_ids and citation_ids both contained "support", but citation_status remained "fail" and next_action was "recover".

after the fix:
| Question | Outcome | Recoveries |
|---|---|---:|
| Q7 | done | 1 |
| Q1 | done | 0 |
| Q2 | escalate | 2 |

Q2 makes three retrieval attempts: the initial attempt plus two recoveries.
For the interview: “I compared the current evidence with the validation result and found stale state. I fixed validation to recompute after every generation.”
At deployed node boundaries, record the request ID, node name, attempt number, evidence and citation IDs, validation result, next action, duration, and errors.

"""