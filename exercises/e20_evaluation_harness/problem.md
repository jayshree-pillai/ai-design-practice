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
