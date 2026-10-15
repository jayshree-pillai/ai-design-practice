# 30–45 Minute Coding Exercises: OOP + LangGraph

**Complete set: 20 exercises, numbered #1–20.** Exercises #7–10 cover context management, concurrent execution, debugging, and supervisor coordination. Most attempts target 45 minutes; individual time limits are listed below.

## Goal

The focus is **not syntax memorization**. The goal is to strengthen the step between:

**English blurb → program structure → code**

For every exercise, spend the first **5 minutes** converting the problem statement into:

```text
NOUNS       → classes / objects / state
VERBS       → methods / functions / nodes
DATA        → fields / types
RULES       → if conditions / routing
FAILURES    → exceptions / recovery paths
OUTPUT      → what must the caller receive?
```

Only then start coding.

---
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
# Exercise 1 — OOP: Customer Support Tickets
**Time:** 30 minutes

## Problem

Build a small ticket-management system.

Each ticket has:

- Ticket ID
- Customer name
- Category
- Priority
- Status

A support queue should:

- Accept new tickets
- Prevent duplicate ticket IDs
- Return all open tickets
- Allow a ticket to be closed
- Return open tickets ordered by priority:
  - `HIGH`
  - `MEDIUM`
  - `LOW`

Trying to close a ticket that does not exist should raise an error.

## Your job

Before coding, decide:

- What classes are needed?
- What fields belong to each class?
- What methods are needed?
- Where should duplicate validation happen?
- Where should priority sorting happen?
- How should errors be represented?

## Concepts to practice

- `class`
- `__init__`
- Encapsulation
- Collections of objects
- Validation
- Filtering
- Sorting
- Exceptions

---

# Exercise 2 — OOP: External Company API
**Time:** 40 minutes

## Problem

An external REST API returns companies.

Each company contains:

- `id`
- `name`
- `industry`
- `rating`

Build a client that:

1. Calls the external API
2. Uses an HTTP timeout
3. Raises an appropriate error for a non-200 response
4. Converts returned JSON records into `Company` objects
5. Removes duplicate companies based on company ID
6. Returns only companies above a requested rating threshold
7. Sorts final results from highest rating to lowest

## Important

Do **not** begin by copying a pre-defined class structure.

Start from the paragraph and derive the program yourself.

## Concepts to practice

- Domain objects / dataclasses
- API client objects
- `requests`
- Timeouts
- HTTP status handling
- JSON → Python objects
- Deduplication
- Filtering
- Sorting

---

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

# Exercise 8 — Concurrent Execution with Partial Failures

**Time:** 45 minutes  
**Suggested implementation:** Python asynchronous functions and a mocked service.

## Problem

A CAR section contains several independent questions. The product team asks:

> “Process the questions concurrently, with at most three service calls in flight. Preserve every successful answer even if another question fails.”

## Available Information

Each question has a unique question ID and text. An asynchronous mock accepts a question and either returns answer text or raises an exception. Configure different delays so completion order differs from input order.

Use a fixture of five questions: Q1, Q2, Q3, Q4, and Q5. Q2 raises a timeout; the others return distinct answers. Track the number of active calls and the highest active count observed.

## Required Behavior

1. Attempt every question exactly once.
2. Allow at most three service calls to be active at the same time.
3. Return results keyed by question ID, with a structured success or failure outcome for every question.
4. Preserve each successful answer and record the individual error for a failed call.
5. A question's failure must not cancel the other questions. Wait for all submitted work to finish before returning.
6. Associate each result with the correct question even when calls complete out of order.
7. Empty input returns an empty result collection and makes no service calls.

## Verification Cases

- All five questions succeed when failures are disabled.
- With Q2 failing, return four successful answers and one failure.
- The observed number of active calls never exceeds three.
- Use overlapping delays to demonstrate that the implementation actually runs more than one call at a time when capacity is available.
- Q5 completes before Q1, but their answers remain attached to their own IDs.
- Empty input produces no calls.

## Your Design Responsibilities

Decide the result contract, where concurrency is limited, where exceptions are handled, and how results are collected.

**Explain afterward:** Does a limit of three concurrent calls also enforce a requests-per-minute or tokens-per-minute limit?

**Scope:** Unique input IDs, one process, and one batch. No retries, rate limiter, queue infrastructure, or checkpointing. The caller does not cancel the batch during this exercise.

---

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

# Core Decomposition Drill

For every problem, do this **before writing code**.

Example blurb:

> Retrieve documents, generate an answer, validate citations, retry twice if validation fails, otherwise escalate.

Convert it first into:

```text
STATE
question
documents
answer
citation_status
retry_count

NODES
retrieve()
generate()
validate()
escalate()

ROUTER
after_validate()

FLOW
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

retry_count >= 2
        ↓
    escalate
        ↓
       END
```

Then code.

---

# Recommended Practice Order

## Round 1 — OOP
1. Customer Support Tickets
2. External Company API
3. Agent Tool Registry

## Round 2 — LangGraph
4. Simple Request Router
5. Evidence Recovery Loop
6. Human Approval Before Tool Execution

## Round 3 — Context, Execution, Debugging, and Coordination
7. Context and Memory Management
8. Concurrent Execution with Partial Failures
9. Debug an Existing Agent Workflow
10. Supervisor and Specialist Coordination

## Round 4 — Application Design and Reliability
11. Customer Support Assistant Using LangGraph
12. Response Caching
13. Background Report Jobs
14. Document Ingestion, Replacement, and Deletion
15. Per-Customer Rate Limiting
16. Report Approval and Notification
17. Bounded Knowledge-Source Crawling
18. Release Gates and Rollback
19. Retrieval Merging and Evidence Selection
20. A Small RAG Evaluation Harness

---

# Interview Practice Format

For each exercise:

### First 5 minutes
Write only:

```text
1. Objects / state
2. Fields
3. Methods / nodes
4. Flow
5. Edge cases
```

### Next 20–30 minutes
Code the solution.

### Final 5–10 minutes
Explain:

- Why you chose the structure
- Where responsibilities live
- How failures are handled
- What edge cases you considered
- What you would improve for production

---

# What This Practice Is Training

The goal is to become fast at turning:

```text
"Here is a paragraph describing a system..."
```

into:

```text
These are my objects.
These are my responsibilities.
This is my state.
These are my transitions.
These are my failure paths.
Now I can code it.
```

That decomposition skill is the main focus of these exercises.
--------------------
---

## Exercise 12 — Response Caching

**Time: 45 minutes**  
**Suggested implementation: Python, an in-memory cache, and a controllable clock.**

### Situation

An assistant repeatedly pays for the same generated answer. The product team asks:

> “Reuse recent answers when the same customer asks the same question. Answers must expire, and a customer must never receive another customer's cached answer.”

### What is available

Each request contains a customer ID, question, and prompt-version identifier. A mocked generator returns a nonempty answer or raises a timeout. A test clock lets you advance time without sleeping.

### Required behavior

1. Generate an answer when no reusable cached answer exists, and cache a successful result.
2. Reuse the answer only when the customer, exact question string, and prompt version all match.
3. An answer remains reusable for **60 seconds after it is stored**. At exactly 60 seconds, it has expired.
4. A cache hit must not call the generator or extend the answer's expiry.
5. A generator timeout must be exposed as an unsuccessful request and must not be cached. A later request can try again.
6. Return the answer on success and indicate whether it came from the cache.

### Verify your implementation

- The first request calls the generator; the identical request 20 seconds later does not.
- The entry still works at 59 seconds and is regenerated at 60 seconds.
- A different customer asking the same question causes a separate generation.
- Changing the prompt version causes a new generation.
- After a timeout, an identical request calls the generator again.

**Scope:** Requests are processed sequentially. Treat differently capitalized or spaced question strings as different questions. Use one fixed expiry duration.

---

## Exercise 13 — Background Report Jobs

**Time: 45 minutes**  
**Suggested implementation: Python with a local queue and one worker.**

### Situation

Report generation is too slow to complete during submission. The product team asks:

> “Return a job ID immediately. Let the user check progress. If they submit the same request twice, don't generate two reports.”

### What is available

A submission contains a customer ID, a client-supplied request key, and a report topic. A mocked report generator either returns report text or raises a timeout. You can control those outcomes per job.

### Required behavior

1. Submission returns a job ID without generating the report. A separate worker processes the queued work.
2. The caller can observe whether a job is queued, running, completed, or failed. A completed job exposes its report text.
3. Repeating the same request key and topic for the same customer returns the existing job ID and creates no additional work.
4. Reusing that key with a different topic for the same customer returns a conflict. Another customer may use the same key independently.
5. A generation timeout permits **one retry**, for at most two generator calls per job. Two timeouts mark the job failed.
6. A failed job must not prevent the worker from processing the next job.
7. Job-status lookup requires the owning customer's ID. A customer cannot read another customer's job.

### Verify your implementation

- Submission returns while the generator call count is still zero; processing later completes the job.
- Duplicate submission produces one job and one report.
- Conflicting reuse of a request key is rejected; another customer's matching key is accepted.
- Timeout followed by success completes the original job.
- Two timeouts fail one job, and the next queued job still completes.
- A status request from the wrong customer is rejected.

**Scope:** One worker; sequential submissions; one report per job. You may explicitly start or drain the worker in your demonstration. All storage remains in memory.

---

## Exercise 14 — Document Ingestion, Replacement, and Deletion

**Time: 45 minutes**  
**Suggested implementation: Python with in-memory document and search stores.**

### Situation

A RAG assistant accepts customer documents. The product team asks:

> “Users must be able to upload, replace, and delete their documents. Search must reflect the latest successful change. A failed update must not destroy the working version.”

### What is available

An upload supplies a customer ID, document name, and plain text. A mocked preparation step either returns searchable text or raises an error. For this exercise, search is a case-insensitive substring search over that text, with one search entry per document.

### Required behavior

1. A successful upload returns a document ID and makes the document searchable for its owner.
2. Replacing a document keeps its ID. On success, only its new text is searchable.
3. If replacement preparation fails, the previous document and searchable text remain intact.
4. Deletion removes the document from search. Deleting an unknown or already deleted ID is harmless.
5. Search returns only the requesting customer's documents. Attempts to replace or delete an existing document owned by someone else are rejected.
6. Replacing an unknown document ID returns an error. Failed initial ingestion creates no searchable entry.
7. Every change returns a clear success or failure outcome.

### Verify your implementation

- Upload “refunds are available” and find it by searching for “refunds.”
- Replace it with “exchanges are available”: the old term no longer finds it, while “exchanges” does.
- Force a replacement failure and confirm the last successful content remains searchable.
- Delete it and confirm it disappears from search; repeat the deletion safely.
- A second customer cannot search, replace, or delete the first customer's document.
- Failed initial ingestion leaves no searchable document behind.

**Scope:** Synchronous changes, plain text, one current version per document, and sequential operations. Real parsing, embeddings, and version history are outside this attempt.

---

## Exercise 15 — Per-Customer Rate Limiting

**Time: 45 minutes**  
**Suggested implementation: Python, an in-memory shared store, and a controllable clock.**

### Situation

One busy customer is exhausting an LLM endpoint's capacity. The product team asks:

> “Each customer gets five requests per minute. Reject extra requests before calling the model, and tell the caller when they can try again.”

### What is available

Requests carry an authenticated customer ID and a question. A mocked model records how many calls it receives. Time is supplied as whole seconds through a test clock.

### Required behavior

1. Use fixed, globally aligned 60-second windows: seconds **0–59**, **60–119**, and so on.
2. Allow at most **five requests per customer per window**. Customers have independent limits.
3. An allowed request consumes one slot before the model runs. The slot remains consumed even if the model fails.
4. A rejected request must not call the model or consume another slot. Return a rate-limit outcome and the number of seconds until the next window.
5. At the next window boundary, the customer receives a fresh allowance.
6. All handler calls in this process must consult the same allowance. If two calls compete for the last slot, exactly one may be accepted.

### Verify your implementation

- Five requests from customer A succeed; the sixth is rejected.
- Customer B still has its own five slots.
- A rejection at second 45 reports a 15-second wait.
- A request at second 60 can succeed in the new window.
- A model failure still consumes a slot.
- With four slots already consumed, two concurrent requests result in one acceptance and one rejection.

**Scope:** One process with concurrent threads and one shared limiter. Count requests, not tokens. The caller handles any later retry; the handler does not sleep or retry automatically.

---

## Exercise 16 — Report Approval and Notification

**Time: 45 minutes**  
**Suggested implementation: LangGraph with in-memory checkpointing and a mocked notifier.**

### Situation

A report has already been generated. The product team asks:

> “Pause for a reviewer. If approved, notify the customer that the report is ready. If rejected, stop. Repeated processing must not send the same notification twice.”

### What is available

You receive a report ID, customer ID, and report text. A reviewer supplies `approve` or `reject` in a later call. The notifier records successful deliveries and can be configured to raise a timeout.

**Mock guarantee:** A notification timeout always occurs before delivery is recorded. There is no delivered-but-acknowledgment-lost case in this exercise.

### Required behavior

1. Start the workflow and pause while awaiting the review decision. The caller can inspect that pending state, and no notification is sent yet.
2. Resume the paused workflow in a separate call within the same process.
3. Approval permits notification. Rejection completes the workflow without notifying.
4. A notification timeout permits one retry. Two timeouts end with a visible notification failure while preserving the approval decision.
5. Once notification succeeds, another application request to process that same report must not send it again. Handle the duplicate at the application boundary; repeated resume calls to an already completed graph are not required.
6. The caller can distinguish review pending, review rejected, approved-and-notified, and approved-but-notification-failed.

### Verify your implementation

- A paused run has sent no notification.
- Approval sends one notification; rejection sends none.
- A timeout followed by success records exactly one delivery.
- Two timeouts expose delivery failure without changing the approval to rejection.
- Reprocessing a successfully notified report records no additional delivery.

**Scope:** One reviewer, already generated report text, same-process pause/resume, and sequential calls. Use a real graph pause/resume mechanism. Notifications are local test records.

---

## Exercise 17 — Bounded Knowledge-Source Crawling

**Time: 45 minutes**  
**Suggested implementation: Python with mocked pages and an in-memory index.**

### Situation

A company wants to refresh a small knowledge collection. The product team asks:

> “Start from this page and follow approved links. Avoid cycles and repeated work. Stop at the page budget, and update the index only when content changes.”

### What is available

The request supplies a start URL, an explicit set of allowed URLs, and a positive page budget. Mock fetching returns page text and a list of outgoing URLs, or raises an error. URLs are already normalized.

Use a tiny fixture: the start page links to A, B, A again, and an unapproved page. A links back to the start and to B. B links to a permitted broken page that raises an error and another approved healthy page, C.

### Required behavior

1. Fetch only URLs present in the allowed set. An unapproved start URL is rejected.
2. Fetch each URL at most once per run, including URLs reached through cycles or duplicate links.
3. Stop when there are no more reachable approved pages or the page budget is reached. Every distinct fetch attempt, including a failed one, consumes one budget slot.
4. Successfully fetched new pages become searchable entries in the in-memory index.
5. Across runs, unchanged text causes no index write. Changed text replaces the previous entry for that URL.
6. A failed fetch is reported, leaves any existing indexed content intact, and does not prevent other permitted pages from being processed.
7. Return a summary of attempted URLs, failures, and entries added, updated, or unchanged.

### Verify your implementation

- Cycles and duplicate links cause no repeated fetch within a run.
- The unapproved page is never fetched.
- A budget of two results in only two distinct fetch attempts when enough permitted pages are reachable.
- Arrange a run with enough budget where the broken page fails while a healthy page is still pending; confirm the healthy page is then processed.
- An unchanged second run performs no index writes; changing one page updates one entry.
- A fetch failure on a later run preserves that page's previously indexed content.

**Scope:** Sequential fetching, any consistent traversal order, already extracted links, and exact text comparison for changes. Fetch failures receive no retry in this problem.

---

## Exercise 18 — Release Gates and Rollback

**Time: 45 minutes**  
**Suggested implementation: Python with an in-memory version registry.**

### Situation

A team wants to change the prompt/model configuration used by an assistant. The product team asks:

> “Check the evaluation results before activating a version. Keep the working version if a candidate fails. If a release later causes trouble, let us roll back.”

### What is available

Each version has an ID, prompt text, and model name. A mocked evaluation service provides an accuracy value and a p95 latency value, or raises an error. A mocked answer service records which version it receives.

Start with `v1` active. Use these candidate results:

| Candidate | Accuracy | p95 latency |
|---|---:|---:|
| `v2` | 0.90 | 1,200 ms |
| `v3` | 0.70 | 900 ms |
| `v4` | 0.95 | 2,500 ms |

### Required behavior

1. Activate a candidate only when accuracy is **at least 0.80** and p95 latency is **at most 2,000 ms**.
2. A rejected candidate or evaluation error leaves the current active version unchanged.
3. Return the release decision and the reasons for rejection or failure.
4. Ordinary answer requests use the currently active version.
5. After a successful activation, allow one rollback to the version active immediately before that activation.
6. Rejected release attempts must not replace the rollback target. After rollback, another rollback returns “nothing to roll back.” The same applies before any successful release.

### Verify your implementation

- `v2` becomes active; requests then use `v2`.
- `v3` is rejected for accuracy, and `v4` for latency.
- An evaluation exception leaves the active version unchanged.
- After activating `v2` and rejecting `v3`, rollback restores `v1`.
- Another rollback changes nothing and reports that no target exists.
- Candidate metrics exactly at both thresholds are accepted.

**Scope:** Use the supplied evaluation metrics. Activation changes an in-memory setting. Support one rollback level and sequential release operations; actual deployment infrastructure is outside this attempt.

---

## Exercise 19 — Retrieval Merging and Evidence Selection

**Time: 45 minutes**  
**Suggested implementation: Plain Python.**

### Situation

Two search services return overlapping evidence. The product team asks:

> “Give the answer generator a small, relevant evidence set. Remove duplicates, enforce customer ownership, and avoid letting one document occupy every slot.”

### What is available

You receive an authenticated customer ID and two lists of search results. Each result has a chunk ID, document ID, customer ID, text, and numeric relevance score. Both services use the same score scale; higher is better. Duplicate chunk IDs have identical text, document, and owner, but may have different scores.

### Required behavior

1. Exclude results belonging to other customers and results with empty or whitespace-only text.
2. Combine the two lists and retain one copy per chunk ID, using its highest score.
3. Return at most three chunks in descending score order. Break equal-score ties by chunk ID in ascending alphabetical order.
4. Include no more than two chunks from the same document. Keep considering lower-ranked candidates when a document has already filled its allowance.
5. Return both the selected evidence records and their chunk IDs in matching order.
6. Return all eligible selections if fewer than three fit the rules; return empty collections if none fit. Leave the input lists unchanged.

### Verify your implementation

- A chunk returned by both services appears once with its higher score.
- A highly scored foreign customer's chunk is excluded.
- A blank-text chunk is excluded.
- Given eligible chunks `c1`, `c2`, and `c3` from document A with scores 0.99, 0.98, and 0.97, plus `c4` from document B with score 0.90, the selection is `c1`, `c2`, `c4`.
- Equal scores follow the stated chunk-ID tie rule.
- One empty source and two empty sources are handled correctly; the original inputs remain unchanged.

**Scope:** Search results are already available and scored. This exercise ends at evidence selection; answer generation is a later consumer.

---

## Exercise 20 — A Small RAG Evaluation Harness

**Time: 45 minutes**  
**Suggested implementation: Plain Python with a mocked assistant.**

### Situation

An assistant appears to work, but changes sometimes break routing or citations. The team asks:

> “Run a small set of known questions and show what failed. One broken request should not prevent us from evaluating the others.”

### What is available

Each test case contains a case ID, question, expected route, and a nonempty set of acceptable evidence IDs. A mocked assistant returns its actual route, answer text, retrieved evidence IDs, and cited evidence IDs, or raises a timeout.

### Required behavior

1. Run every case independently. Record a timeout as a case error and continue.
2. Check routing: the actual route must equal the expected route.
3. Check evidence retrieval: at least one acceptable evidence ID must appear in the retrieved IDs.
4. Check citations: at least one citation must exist, and every cited ID must occur in the retrieved IDs. Treat IDs as sets for these checks.
5. A case passes overall only when all three checks pass and the answer contains non-whitespace text.
6. Report each case's outcome and all failed checks. A timeout is recorded as the error and counts as a failure for every aggregate metric.
7. Report total cases, overall passed cases, timeout count, routing accuracy, evidence hit rate, and citation-validity rate. Each rate uses **all cases** as its denominator.

### Verify your implementation

Create five cases with these controlled outcomes:

| Case | Mock behavior |
|---|---|
| 1 | Nonempty answer; routing, evidence, and citations are all correct. |
| 2 | Only the route is incorrect. |
| 3 | Only evidence retrieval fails: retrieved IDs contain none of the expected evidence, but citations refer to the evidence actually retrieved. |
| 4 | Only citation validation fails: one citation refers to an ID that was never retrieved. |
| 5 | The assistant raises a timeout. |

Confirm that all five cases are reported, only case 1 passes overall, and the timeout count is one. Each of the three aggregate rates should be **3/5 = 60%**. Then change case 1's answer to whitespace and confirm its overall result fails even though its three checks still pass.

**Scope:** Use a nonempty dataset and fixed mock outputs. Evaluate routing and evidence handling mechanically; answer text is checked for presence. Model-based judging and semantic answer-quality scoring are outside this attempt.

---
