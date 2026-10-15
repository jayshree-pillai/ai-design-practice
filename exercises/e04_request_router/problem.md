# Exercise 4 — LangGraph: Simple Request Router
**Time:** 30 minutes

## Problem

Build a LangGraph workflow that receives a user question.

Routing rules:

- Questions about uploaded documents → document handler
- Questions about database/account information → SQL handler
- Everything else → semantic/general handler

Each handler should:

1. Receive the state
2. Produce an answer
3. Store the answer in state
4. Terminate

## Minimum state

```python
question
route
answer
```

## Constraint

The router should **only decide where the request goes**.

The router should **not generate the answer**.

## Before coding, identify

```text
STATE
NODES
ROUTER
CONDITIONAL EDGES
START
END
```

## Concepts to practice

- Typed state
- Nodes
- Routing functions
- `add_conditional_edges`
- Separation of responsibilities
- `START`
- `END`

---
