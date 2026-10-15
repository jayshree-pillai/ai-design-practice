# Exercise 5 — LangGraph: Evidence Recovery Loop
**Time:** 45 minutes

## Problem

Build a workflow that answers a question using retrieved evidence.

The workflow should:

1. Retrieve documents
2. Generate an answer
3. Validate whether the answer has sufficient citation support

If validation passes:

- Finish

If validation fails:

- Expand or modify the retrieval query
- Retrieve again
- Regenerate the answer

Allow at most **2 recovery attempts**.

If evidence is still insufficient after the retries:

- Return an escalation response
- Terminate

## Constraint

Do **not** write a Python `while` loop around the graph.

The graph itself should represent the retry path.

## Think about state such as

```text
question
retrieved_docs
answer
citation_status
retry_count
```

Decide whether you need anything else.

## Possible conceptual flow

```text
START
  ↓
retrieve
  ↓
generate
  ↓
validate
 ↙       ↘
retry     END
 ↓
retrieve
```

If retry limit is reached:

```text
validate
   ↓
escalate
   ↓
 END
```

## Concepts to practice

- Typed state
- Conditional routing
- Graph loops
- Retry counters
- State propagation
- Bounded retries
- Deterministic termination

---
