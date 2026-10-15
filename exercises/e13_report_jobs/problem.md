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
