"""Exercise 10: Supervisor and Specialist Coordination.

Not implemented yet. Complete design.md before writing the first solution.
Keep the implementation within the scope in problem.md.
"""
# Mock records: (behavior, finding, evidence ID).
DOCUMENTS = {
    "C1": ("sufficient", "Refunds are allowed within 30 days.", "C1-D1"),
    "C2": ("follow_up", "Refunds are allowed within 14 days.", "C2-D1"),
}

ACCOUNTS = {
    "C1": ("sufficient", "The account balance is $100.", "C1-A1"),
    "C2": ("error", "", ""),
}


def mock_lookup(task, records):
    result = {
        "status": "insufficient",
        "findings": [],
        "evidence_ids": [],
        "error": None,
    }

    # Only read this customer's record.
    record = records.get(task["customer_id"])
    if record is None:
        return result

    behavior, finding, evidence_id = record
    if behavior == "error":
        result["status"] = "error"
        result["error"] = "Lookup failed"
    elif behavior == "sufficient" or (
        behavior == "follow_up" and task["follow_up"]
    ):
        result["status"] = "sufficient"
        result["findings"] = [finding]
        result["evidence_ids"] = [evidence_id]

    return result


def document_specialist(task):
    return mock_lookup(task, DOCUMENTS)


def account_specialist(task):
    return mock_lookup(task, ACCOUNTS)


SPECIALISTS = {
    "document": document_specialist,
    "account": account_specialist,
}


def plan(question):
    question = question.lower()
    required = []

    if "document" in question or "policy" in question:
        required.append("document")

    if "account" in question or "balance" in question:
        required.append("account")

    return required


def choose_follow_up(results):
    questions = {
        "document": "Find the exact refund deadline.",
        "account": "Find the current account balance.",
    }

    for source in ("document", "account"):
        result = results.get(source)
        if result and result["status"] == "insufficient":
            return source, questions[source]

    return None


def supervise(customer_id, question):
    required = plan(question)
    results = {}
    calls = []

    if not required:
        return {
            "status": "clarification",
            "answer": "Do you need document policy, account details, or both?",
            "evidence_ids": [],
            "missing": {},
            "calls": calls,
        }

    def call_specialist(source, task_question, follow_up=False):
        task = {
            "customer_id": customer_id,
            "question": task_question,
            "follow_up": follow_up,
        }
        calls.append(source)
        results[source] = SPECIALISTS[source](task)

    # First round: call every required specialist once.
    for source in required:
        call_specialist(source, question)

    # One follow-up for the entire request.
    follow_up = choose_follow_up(results)
    if follow_up:
        source, focused_question = follow_up
        call_specialist(source, focused_question, follow_up=True)

    # Inspect the latest results, including the follow-up.
    findings = []
    evidence_ids = []
    missing = {}

    for source, result in results.items():
        if result["status"] == "sufficient":
            findings.extend(result["findings"])
            evidence_ids.extend(result["evidence_ids"])
        else:
            missing[source] = result["error"] or "Insufficient evidence"

    if not missing:
        status = "answered"
    elif findings:
        status = "partial"
    else:
        status = "failed"

    return {
        "status": status,
        "answer": " ".join(findings) or "No supported findings.",
        "evidence_ids": evidence_ids,
        "missing": missing,
        "calls": calls,
    }


def main():
    result = supervise("C2", "Explain the policy and account balance")

    for key, value in result.items():
        print(key, ":", value)


if __name__ == "__main__":
    main()

"""


Remember: plan → call specialists → inspect → one follow-up → combine.
The mock behavior "follow_up" means evidence becomes available on the second call.


status : partial
answer : Refunds are allowed within 14 days.
evidence_ids : ['C2-D1']
missing : {'account': 'Lookup failed'}
calls : ['document', 'account', 'document']

Documents succeed on follow-up. The account error remains recorded, giving a partial answer. Change "C2" to "C1" for both sources to succeed.
What happens after routing? The supervisor checks the results, chooses whether a follow-up is needed, inspects that new result, and combines supported findings.
Interview follow-up:
- An LLM could propose the initial plan, focused follow-up question, and final wording.
- Application code must enforce customer scope, allowed specialists, one additional call total, no retries for errors, and evidence preservation.



"""