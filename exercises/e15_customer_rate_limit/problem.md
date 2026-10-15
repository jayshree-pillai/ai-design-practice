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
