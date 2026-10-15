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
