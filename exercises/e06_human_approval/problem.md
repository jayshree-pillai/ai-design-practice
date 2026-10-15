# Exercise 6 — LangGraph: Human Approval Before Tool Execution
**Time:** 45 minutes

## Problem

An agent receives a requested action and proposes a tool call.

There are two categories of tools:

### Safe tools
Read-only tools may execute immediately.

### Sensitive tools
Sensitive tools require human approval before execution.

The workflow should:

1. Receive the request
2. Propose a tool and its arguments
3. Determine whether approval is required
4. Execute immediately if safe
5. Pause for human review if approval is required
6. Resume when the human provides a decision
7. Execute the tool only if approved
8. Skip execution and return a rejection response if rejected
9. Return structured failure information if tool execution fails

## Potential state concepts

```text
request
proposed_tool
proposed_args
requires_approval
human_decision
tool_result
answer
```

Your job is to decide which fields are truly necessary.

## Concepts to practice

- `interrupt()`
- `Command(resume=...)`
- Human-in-the-loop
- Conditional routing
- Separating proposal from execution
- State persistence across pause/resume
- Safe tool execution

---
