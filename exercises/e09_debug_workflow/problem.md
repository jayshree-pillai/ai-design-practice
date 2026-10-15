# Exercise 9 — Debug an Existing Agent Workflow

**Time:** 45 minutes  
**Suggested implementation:** Run and repair the supplied Python reproduction.

## Problem

The support team reports:

> “Q7 keeps escalating even though recovery found the supporting evidence. Find the first incorrect behavior, fix the defect, and add a regression test.”

The following small program reproduces the workflow using node functions, state updates, and a routing function. It uses plain Python so the attempt can focus on the incident without graph setup. It intentionally contains one defect.

## Supplied Reproduction

```python
MAX_RECOVERIES = 2


def retrieve(state):
    if state["question_id"] == "Q1":
        ids = ["support"]
    elif state["question_id"] == "Q7":
        ids = ["background"] if state["recovery_attempts"] == 0 else ["support"]
    else:  # Q2 has no supporting evidence on any attempt.
        ids = []
    return {"retrieved_ids": ids}


def generate(state):
    supported = "support" in state["retrieved_ids"]
    return {
        "answer": "Supported answer" if supported else "Insufficient evidence",
        "citation_ids": ["support"] if supported else [],
    }


def validate(state):
    if state["citation_status"] is None:
        valid = (
            "support" in state["retrieved_ids"]
            and bool(state["citation_ids"])
            and set(state["citation_ids"]).issubset(state["retrieved_ids"])
        )
        return {"citation_status": "pass" if valid else "fail"}
    return {}


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


if __name__ == "__main__":
    result = run("Q7")
    for event in result["trace"]:
        print(event)
    assert result["outcome"] == "done", "Q7 should finish after recovery"
```

## Observed Q7 Trace Before the Fix

| Recovery attempts | Retrieved IDs | Cited IDs | Validation | Next action |
|---:|---|---|---|---|
| 0 | background | none | fail | recover |
| 1 | support | support | fail | recover |
| 2 | support | support | fail | escalate |

## Your Task

1. Run the reproduction and observe the failing assertion.
2. Identify the first point where the state or decision disagrees with the current evidence.
3. Explain the cause using the trace and node behavior.
4. Apply a focused fix. Preserve the retrieval fixture and maximum of two recovery attempts.
5. Add regression checks for recovery success, immediate success, and evidence that remains insufficient.

## Verification Cases

- Q7 completes with `done` after one recovery, with the supporting evidence and citation preserved.
- Q1 completes immediately with zero recoveries.
- Q2 escalates after two recoveries, for three retrieval attempts in total.
- Running Q1 followed by Q2 does not leak a passing validation result between requests.

**Explain afterward:** Which trace fields made the defect visible? What would you record at node boundaries in a deployed version?

**Scope:** One seeded defect and deterministic evidence checks. The fixture treats the ID `support` as known supporting evidence; this is not a semantic claim evaluator. No deployment or observability service is required.

---
