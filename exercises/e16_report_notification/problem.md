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
