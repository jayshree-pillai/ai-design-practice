"""Exercise 10: complete plain Python supervisor implementation.

Run: python supervisor_python_solution.py
Python 3.10+; no extra packages required.

The run_supervisor function is the candidate implementation. Everything else
supplies the existing contracts, mocks, fixtures, and example runner.
The function has five parts: plan, initial calls, one follow-up, inspect results,
and final response. Read the five numbered comments in order.

The follow-up loop's break enforces one extra specialist call across the whole
request, regardless of its outcome. Only insufficient sources qualify. All
results and counters are local to the request; fixtures return fresh copies.
Mock errors are structured results, not raised exceptions, per their contract.
"""

from copy import deepcopy
from pprint import pprint
from typing import Literal, TypedDict


# PROVIDED CONTRACTS — use these as ordinary Python dictionaries.
Source = Literal["document", "account"]


class Plan(TypedDict):
    required_sources: list[Source]
    clarification_question: str | None


class Task(TypedDict):
    customer_id: str
    question: str


class SpecialistResult(TypedDict):
    status: Literal["sufficient", "insufficient", "error"]
    findings: list[str]
    evidence_ids: list[str]
    error: str | None


class SupervisorResult(TypedDict):
    status: Literal["answered", "partial", "failed", "clarification"]
    answer: str
    evidence_ids: list[str]
    issues: dict[str, str]
    call_count: int


# SUPERVISOR IMPLEMENTATION
def run_supervisor(customer_id: str, question: str) -> SupervisorResult:
    # 1. Get the plan; finish immediately if clarification is needed.
    plan = planning_mock(question)
    if plan["clarification_question"] is not None:
        return {
            "status": "clarification",
            "answer": plan["clarification_question"],
            "evidence_ids": [],
            "issues": {},
            "call_count": 0,
        }

    # 2. Call each required specialist once. All state is local to this request.
    required = plan["required_sources"]
    task = {"customer_id": customer_id, "question": question}
    results = {}
    call_count = 0

    for source in required:
        if source == "document":
            results[source] = document_specialist(task)
        else:
            results[source] = account_specialist(task)
        call_count += 1

    # 3. Allow ONE follow-up in total, with document priority.
    for source in ("document", "account"):
        if source in results and results[source]["status"] == "insufficient":
            focused_task = followup_mock(source, task)

            if source == "document":
                results[source] = document_specialist(focused_task)
            else:
                results[source] = account_specialist(focused_task)

            call_count += 1
            break  # No second follow-up, even if evidence is still insufficient.

    # 4. Inspect the latest results, including any follow-up result.
    findings = []
    evidence_ids = []
    issues = {}
    successful_sources = 0

    for source in required:
        result = results[source]
        if result["status"] == "sufficient":
            successful_sources += 1
            findings.extend(result["findings"])
            evidence_ids.extend(result["evidence_ids"])
        elif result["status"] == "insufficient":
            issues[source] = "Insufficient evidence"
        else:
            issues[source] = result["error"] or "Specialist failed"

    # 5. Decide the overall outcome and return the final response.
    if successful_sources == len(required):
        status = "answered"
    elif successful_sources > 0:
        status = "partial"
    else:
        status = "failed"

    return {
        "status": status,
        "answer": " ".join(findings) if findings else "No supported findings.",
        "evidence_ids": evidence_ids,
        "issues": issues,
        "call_count": call_count,
    }


# PROVIDED MOCKS — no implementation work required below this line.
def planning_mock(question: str) -> Plan:
    """Deterministic keyword planner; required_sources is authoritative."""
    sources: list[Source] = []
    text = question.lower()
    if "policy" in text or "document" in text:
        sources.append("document")
    if "account" in text:
        sources.append("account")
    if not sources:
        return {
            "required_sources": [],
            "clarification_question": "Do you mean your policy or your account?",
        }
    return {"required_sources": sources, "clarification_question": None}


_FOCUSED_QUESTIONS: dict[Source, str] = {
    "document": "Find the refund window in the signed policy document.",
    "account": "Look up the current account status by customer ID.",
}


def followup_mock(source: Source, previous_task: Task) -> Task:
    """Return a new focused task; source choice and call budget are YOUR job."""
    return {
        "customer_id": previous_task["customer_id"],
        "question": _FOCUSED_QUESTIONS[source],
    }


def document_specialist(task: Task) -> SpecialistResult:
    return _lookup("document", task)


def account_specialist(task: Task) -> SpecialistResult:
    return _lookup("account", task)


def _sufficient(finding: str, evidence_id: str) -> SpecialistResult:
    return {"status": "sufficient", "findings": [finding],
            "evidence_ids": [evidence_id], "error": None}


def _insufficient() -> SpecialistResult:
    return {"status": "insufficient", "findings": [],
            "evidence_ids": [], "error": None}


def _error(message: str) -> SpecialistResult:
    return {"status": "error", "findings": [],
            "evidence_ids": [], "error": message}


# For each source: [initial result, optional focused result].
# One result means the focused task returns the same outcome.
# IDs and facts are fictional. Lookups are scoped to the supplied customer ID.
_FIXTURES = {
    "C1": {
        "document": [_sufficient("Refund window: 30 days.", "C1-D1")],
        "account": [_sufficient("Account status: active.", "C1-A1")],
    },
    "C2": {
        "document": [_sufficient("Refund window: 21 days.", "C2-D1")],
        "account": [_error("Account service unavailable")],
    },
    "C3": {
        "document": [_sufficient("Refund window: 14 days.", "C3-D1")],
        "account": [_insufficient(),
                    _sufficient("Account status: active.", "C3-A1")],
    },
    "C4": {
        "document": [_insufficient()],
        "account": [_sufficient("Account status: suspended.", "C4-A1")],
    },
    "C5": {
        "document": [_insufficient(),
                     _sufficient("Refund window: 7 days.", "C5-D1")],
        "account": [_insufficient(),
                    _sufficient("Account status: active.", "C5-A1")],
    },
    "C6": {
        "document": [_sufficient("Refund window: 60 days.", "C6-D1")],
        "account": [_sufficient("Account status: closed.", "C6-A1")],
    },
}


def _lookup(source: Source, task: Task) -> SpecialistResult:
    customer = _FIXTURES.get(task["customer_id"])
    if customer is None:
        return _error("No fixture available for this customer")
    outcomes = customer[source]
    is_focused = task["question"] == _FOCUSED_QUESTIONS[source]
    index = 1 if is_focused and len(outcomes) > 1 else 0
    # Each call returns its own dict/lists. No global call counters or state.
    return deepcopy(outcomes[index])


# Examples are supplied; you do not need to design test cases.
# Columns: description, customer, question, expected status, expected calls.
EXAMPLES = [
    ("Document only", "C1", "What is my refund policy?", "answered", 1),
    ("Account only", "C1", "What is my account status?", "answered", 1),
    ("Both succeed", "C1", "Check my policy and account.", "answered", 2),
    ("Clarification", "C1", "Can you help me?", "clarification", 0),
    ("Account error", "C2", "Check my policy and account.", "partial", 2),
    ("Follow-up succeeds", "C3", "Check my policy and account.", "answered", 3),
    ("Still insufficient", "C4", "Check my policy and account.", "partial", 3),
    ("No usable evidence", "C4", "What is my refund policy?", "failed", 2),
    ("Both insufficient: document gets only follow-up", "C5",
     "Check my policy and account.", "partial", 3),
    ("New customer: only C6-D1 evidence, fresh count", "C6",
     "What is my refund policy?", "answered", 1),
]


def main() -> None:
    for label, customer_id, question, expected_status, expected_calls in EXAMPLES:
        print(f"\n{label} | {customer_id}")
        print(f"Expected: {expected_status}, {expected_calls} specialist call(s)")
        pprint(run_supervisor(customer_id, question))


if __name__ == "__main__":
    main()
