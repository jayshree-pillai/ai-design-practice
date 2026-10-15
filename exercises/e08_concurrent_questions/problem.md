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
