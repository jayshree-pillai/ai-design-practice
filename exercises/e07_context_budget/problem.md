# Exercise 7 — Context and Memory Management

**Time:** 45 minutes  
**Suggested implementation:** Plain Python with supplied token counts.

## Problem

CAR Chat has a long conversation history. The product team asks:

> “Build the next model input within a token budget. Always keep the system instruction and current question, retain recent complete turns, and leave the stored conversation unchanged.”

## Available Information

Each request contains:

- A system instruction and its token count.
- The current user question and its token count.
- Previous conversation turns, ordered oldest to newest. Each turn contains its complete group of messages and a total token count.
- A positive input-token budget.

Token counts are supplied and already include message-format overhead. Historical turns do not include the current question. A turn may contain tool calls and their results; treat that whole turn as one indivisible unit.

## Required Behavior

1. Always include the system instruction and current question.
2. Return a clear error if those two mandatory items alone exceed the budget.
3. Starting with the newest historical turn, retain complete turns while they fit. Stop at the first turn that does not fit; do not skip that turn to include older, smaller ones.
4. Return the selected messages in this order: system instruction, retained history in chronological order, current question.
5. Return the total selected token count. A total exactly equal to the budget is allowed.
6. Do not modify the input messages or stored history.

## Verification Cases

- All turns fit and remain in chronological order.
- With a budget of 20, system cost 4, question cost 4, and historical turn costs `[3, 5, 7]`, retain the last two turns and return a total of 20.
- The newest turn alone exceeds the remaining allowance: return only the mandatory content, even if an older turn would fit.
- Empty history returns the system instruction and current question.
- Mandatory content exceeds the budget: return the specified error.
- A selected turn containing tool messages remains complete, and the original history is unchanged.

## Your Design Responsibilities

Decide the input representation, result format, error behavior, and where budget accounting belongs.

**Explain afterward:** What is the difference between the conversation the application stores and the context sent to the model on this call?

**Scope:** No tokenizer, summarizer, database, or cross-session memory. This exercise uses only the supplied counts.

---
