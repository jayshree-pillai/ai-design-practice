# Exercise 10 — Supervisor and Specialist Coordination

**Time:** 45 minutes  
**Suggested implementation:** Python or LangGraph with mocked decisions and two mocked specialists.

## Problem

A conversational assistant can use uploaded documents and customer account data. The product team asks:

> “Some questions need one source, and some need both. Delegate the work, inspect what comes back, and combine supported findings. If evidence is incomplete, allow one focused follow-up. Always finish within that limit.”

## Available Information

A request contains an authenticated customer ID and a question. A deterministic planning mock selects document-only, account-only, both, or clarification required.

Two specialists are available:

| Specialist | Task | Possible result |
|---|---|---|
| Document specialist | Find evidence in the customer's uploaded documents | Sufficient evidence, insufficient evidence, or an error |
| Account specialist | Look up the customer's account facts | Sufficient evidence, insufficient evidence, or an error |

Each specialist receives a scoped task and returns a structured result. Successful results include findings and evidence IDs. The fixtures already enforce customer ownership. For the exercise, an `insufficient` result contains no usable finding.

A mocked follow-up decision supplies a more focused question for a specialist that returned insufficient evidence. Use the fixed priority document first, then account, if both are insufficient. An error is recorded as a failure and does not receive a retry in this exercise.

## Required Behavior

1. An unclear request returns a clarification question without calling either specialist.
2. Delegate only to the specialists required by the initial plan, once each on the first round.
3. After collecting their results, let the supervisor decide whether it can finish or needs the permitted follow-up.
4. Allow at most **one additional specialist call across the entire request**, directed to a required specialist with insufficient evidence. This means at most two calls for a one-source plan or three for a two-source plan.
5. The supervisor must inspect the follow-up result before producing the final outcome. Preserve useful findings from the other specialist.
6. Return `answered` when all required sources provide sufficient evidence, `partial` when only some do, and `failed` when none do. An unclear request returns `clarification`.
7. Build the answer only from successful findings, preserve their evidence IDs, and identify missing or failed sources in partial or failed outcomes.
8. Each run starts with fresh request state. A previous customer's findings must never appear in a later run.

## Verification Cases

- A document-only question calls only the document specialist and returns an answer with its evidence IDs.
- A question requiring both sources combines two successful results and preserves both sets of evidence IDs.
- An unclear question asks for clarification and makes zero specialist calls.
- Documents succeed and account lookup errors: return a partial answer, preserve document evidence, and record the account failure.
- One required source is initially insufficient and succeeds on follow-up: finish with `answered` within the call budget.
- Follow-up remains insufficient: stop with `partial` if the other source succeeded, or `failed` if no source succeeded.
- Both required sources are insufficient: follow up with documents only, then stop within three total calls.
- A second run begins without the first run's findings or call count.

## Your Design Responsibilities

Define the supervisor's state, the task/result contracts, specialist-local data, evidence merging, and the decision that controls the follow-up. Keep the supervisor responsible for the final response.

**Explain afterward:** What work happens after the initial routing decision? Which decisions could an LLM propose, and which limits must application code enforce?

**Scope:** One incoming question, sequential specialist calls, deterministic mocks, and in-memory state. No real model, SQL database, retrieval service, ReAct loop inside a specialist, or conversation persistence. A template-based final response is sufficient.

---
