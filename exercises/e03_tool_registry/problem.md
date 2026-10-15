# Exercise 3 — OOP: Agent Tool Registry
**Time:** 40 minutes

## Problem

An AI application has multiple tools.

Every tool has:

- A name
- A description
- A callable function

The system should:

- Register a tool
- Reject duplicate tool names
- Look up a tool by name
- Execute the tool with arguments
- Prevent execution of unregistered tools
- Catch execution failures
- Return execution results in a structured format

The execution result should contain:

```text
success
result
error
```

Create two example tools:

```python
search_company(name)
get_rating(company_id)
```

## Questions to answer before coding

- Is a tool itself an object?
- Is the registry a separate object?
- Who owns duplicate checking?
- Who owns execution?
- Where should exceptions be caught?
- What does the caller receive if execution fails?

## Concepts to practice

- Abstraction
- Callable functions
- Registry pattern
- Validation
- Safe execution boundaries
- Error handling
- Structured return values

---
