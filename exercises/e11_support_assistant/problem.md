# Exercise 11 — Customer Support Assistant Using LangGraph

**Time:** 45–60 minutes  
**Scope:** One incoming customer message per run, with mocked external dependencies.

## Problem

A company wants an assistant that can answer questions about its policies and check a customer’s latest order.

The product manager says:

> “Customers should be able to ask about returns, shipping policies, or their order. The assistant should find the right information and answer. Sometimes our services time out. Handle that gracefully, and don’t let the assistant keep trying forever.”

The application already authenticates the customer. Each request includes:

- Customer ID
- Message

## Available Information Sources

| Source | Information available | Possible outcomes |
|---|---|---|
| Help documents | Return rules and shipping policies | Relevant text, no matching information, or a timeout |
| Order service | The authenticated customer’s latest order | Order details, no order found, or a timeout |

## Requirements

1. **Choose the appropriate source.**
   Policy questions use the help documents. Questions about the customer’s latest order use the order service. Assume a supported message needs only one source.

2. **Handle unclear requests.**
   If the message does not provide enough information to choose a source, ask a clarifying question without calling either source.

3. **Use the returned information.**
   Produce an answer supported by the selected source. If it returns no information, tell the customer that the answer could not be found.

4. **Recover from timeouts.**
   Allow one retry of the selected source. If that also times out, return a helpful failure response and finish. An empty result does not trigger a retry.

5. **Expose the outcome.**
   The calling application must be able to distinguish an answered request, a clarification request, and an unsuccessful lookup.

6. **Keep requests isolated.**
   Information from one customer’s run must not appear in another customer’s answer.

## Implementation Constraints

Use Python and LangGraph.

Simulate routing, information retrieval, and answer generation with simple Python mocks so the behavior is repeatable.

## Verification Cases

Your implementation should demonstrate:

- A policy question receives a supported answer.
- An order question receives that customer’s order information.
- An unclear message produces a clarification.
- A timeout followed by success produces an answer.
- Two consecutive timeouts end the workflow.
- An empty result ends with an appropriate response.

## Your Design Responsibilities

You own the design of:

- Result format
- State
- Function contracts
- Workflow
- Error handling

## First Design Question

Before coding, explain in your own words:

---------------------
