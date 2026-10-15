# AI Design Interview Practice

A practice repository for Jay's 20 exercises: turn a problem statement into a small, working Python program and explain the design under interview time pressure.

**Current status: starter only. All 20 prompts are included; solutions and tests are intentionally unimplemented.** Build and commit each solution as you learn it. This is a new, separate project.

## Start in VS Code

Extract the ZIP and open the `ai-design-practice` folder in VS Code. In its terminal:

```bash
git init -b main
python -m venv .venv
```

Activate the environment using the command for your terminal:

| Terminal | Command |
|---|---|
| WSL / Linux / macOS | `source .venv/bin/activate` |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |

Then run:

```bash
python -m pip install -r requirements-dev.txt
git add .
git commit -m "chore: scaffold 20 AI design interview exercises"
```

Use `python3` for environment creation if that is your system's Python command. Python 3.11 or later is the project baseline. If Git asks for an author identity, use your own name and email. The ZIP excludes local Git metadata; the commands above create your own history. No GitHub repository or remote has been created.

The initial exercises do not need model credentials or infrastructure. Install `requests` when reaching exercise 2 and `langgraph` when reaching exercise 4. Keep external services mocked as required by each prompt.

## What lives in each exercise folder

| File | Purpose |
|---|---|
| `problem.md` | The exercise statement extracted from the supplied document |
| `design.md` | Your five-minute decomposition, review notes, and attempt log |
| `solution.py` | Your working solution, developed during practice |
| `test_solution.py` | Checks derived from the requirements and verification cases |

The unchanged original is in `docs/Design_Practise.md`. `PROGRESS.md` tracks evidence of readiness. Folder IDs always match the original exercise numbers; practice order is separate.

## Learning sequence

| Phase | Exercises in order |
|---|---|
| Python objects and contracts | [1](exercises/e01_support_tickets/problem.md) → [3](exercises/e03_tool_registry/problem.md) → [2](exercises/e02_company_api/problem.md) |
| Data selection and state changes | [7](exercises/e07_context_budget/problem.md) → [19](exercises/e19_evidence_selection/problem.md) → [12](exercises/e12_response_cache/problem.md) → [14](exercises/e14_document_lifecycle/problem.md) |
| Graph fundamentals and recovery | [4](exercises/e04_request_router/problem.md) → [11](exercises/e11_support_assistant/problem.md) → [5](exercises/e05_evidence_recovery/problem.md) → [9](exercises/e09_debug_workflow/problem.md) |
| Execution and bounded work | [8](exercises/e08_concurrent_questions/problem.md) → [13](exercises/e13_report_jobs/problem.md) → [15](exercises/e15_customer_rate_limit/problem.md) → [17](exercises/e17_bounded_crawler/problem.md) |
| Approval and coordination | [6](exercises/e06_human_approval/problem.md) → [16](exercises/e16_report_notification/problem.md) → [10](exercises/e10_supervisor/problem.md) |
| Evaluation and release control | [20](exercises/e20_evaluation_harness/problem.md) → [18](exercises/e18_release_rollback/problem.md) |

This order is a recommendation based on prerequisites, not a fixed calendar. Start with exercise 1 as a short baseline. Adjust the next practice session from the observed blockers.

## Practice method

1. **Baseline:** Spend five minutes deriving the objects/state, contracts, responsibilities, flow, and edge cases. Explain them before receiving a proposed design.
2. **Guided build:** Implement one part at a time. Use a small hint when blocked, record it, and finish a working solution with the required checks.
3. **Independent rebuild:** Save the working version in Git. Rebuild from the prompt without consulting the previous solution or receiving generated code. Use the exercise's stated time limit.
4. **Delayed variation:** After a gap of at least two days, solve it again with changed fixtures or a small related requirement. Record the result and explanation.

For a 45-minute attempt, use roughly 5 minutes for design, 25 for implementation, 10 for verification, and 5 for explanation. Scale the split for shorter exercises. A guided first encounter may take longer; record the actual time without calling it a timed pass.

Mark **interview-ready** only after two independent timed passes, including the delayed variation. Both must satisfy all stated requirements and verification cases. You must explain responsibility boundaries, state changes, failure handling, and termination. A hint-assisted completion remains useful practice and is recorded separately.

Keep the scope in the prompt. Do not add a real database, paid model call, deployment, or a reusable framework to a mocked 45-minute exercise. Discuss production extensions after the required solution works.

## Running checks once they exist

From the repository root:

```bash
python -m pytest exercises/e01_support_tickets -q
```

After several exercises are complete:

```bash
python -m pytest -q
```

There are no implemented tests in this starter. Pytest reporting no tests collected (exit code 5) is expected until you add real checks; it is not evidence of correctness.

Commit a finished attempt before changing it. Suggested message:

```text
feat: solve exercise 01 support tickets with acceptance tests
```

## Source notes and boundaries

- The original places exercise 11 before exercise 1 and leaves its final design question unfinished. Use the common five-minute design questions in `design.md`.
- Exercise 11 permits 45–60 minutes despite the document's 30–45 minute title. Respect the individual time limits.
- Exercise 2 does not specify an endpoint or response envelope. Agree on a deterministic mocked HTTP contract before its timed attempt.
- Exercises 1–6 have fewer explicit verification cases. Derive the missing checks from their requirements; do not invent extra product scope.
- Exercise 5 and 9 allow two recovery attempts after the initial attempt. Exercise 11, 13, and 16 allow one retry. Exercise 10 allows one extra specialist call across the entire request.
- Exercise 8 uses async concurrency; exercise 15 requires thread-safe admission with a shared limiter.
- Exercise 9 deliberately uses plain Python. Exercise 10 permits Python or LangGraph. Exercise 16 requires real graph pause/resume.
- Exercise 20 checks routing, evidence IDs, citation membership, and answer presence. Its metrics do not establish semantic answer correctness.

## First session

Open `exercises/e01_support_tickets/problem.md`, then fill in only the first-five-minutes section of `design.md`. Start by explaining what objects you need and which responsibilities belong to each. Do not read a reference solution before this baseline.
