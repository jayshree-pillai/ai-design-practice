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
