"""Exercise 08: Concurrent Execution with Partial Failures.

Not implemented yet. Complete design.md before writing the first solution.
Keep the implementation within the scope in problem.md.


Yes, your 4 + 1 math works if every question takes the same amount of time. If each takes one second, 13 questions finish in about 5 seconds: 3 + 3 + 3 + 3 + 1.

In the snippet you shared, asyncio.gather schedules all 13 questions. Semaphore(3) lets up to three run inside async with semaphore at once. Say Q1, Q2, and Q3 start together. If Q2 finishes first, Q4 can start immediately while Q1 and Q3 are still running

"""
import asyncio


class MockService:
    def __init__(self, fail_q2=True):
        self.fail_q2 = fail_q2
        self.active = 0
        self.max_active = 0
        self.completed = []

    async def answer(self, question):
        delays = {"Q1": 1.0, "Q2": 0.1, "Q3": 0.2, "Q4": 0.3, "Q5": 0.1}
        question_id = question["id"]

        self.active += 1
        self.max_active = max(self.max_active, self.active)

        try:
            await asyncio.sleep(delays[question_id])

            if self.fail_q2 and question_id == "Q2":
                raise TimeoutError("Q2 timed out")

            return f"Mock answer for {question['text']}"
        finally:
            self.active -= 1
            self.completed.append(question_id)


async def run_batch(questions, service):
    semaphore = asyncio.Semaphore(3)
    results = {}

    async def process_one(question):
        async with semaphore:
            try:
                answer = await service.answer(question)
                results[question["id"]] = {
                    "success": True,
                    "answer": answer,
                    "error": None,
                }
            except Exception as error:
                results[question["id"]] = {
                    "success": False,
                    "answer": None,
                    "error": str(error),
                }

    tasks = [process_one(question) for question in questions]
    await asyncio.gather(*tasks)
    return results


async def main():
    questions = [
        {"id": "Q1", "text": "Revenue?"},
        {"id": "Q2", "text": "Profit?"},
        {"id": "Q3", "text": "Costs?"},
        {"id": "Q4", "text": "Tax?"},
        {"id": "Q5", "text": "Headcount?"},
    ]

    service = MockService()  # Use fail_q2=False for five successes.
    results = await run_batch(questions, service)

    for question in questions:
        print(question["id"], results[question["id"]])

    print("Completion order:", service.completed)
    print("Maximum active calls:", service.max_active)


if __name__ == "__main__":
    asyncio.run(main())
"""
Completion order: ['Q2', 'Q3', 'Q5', 'Q4', 'Q1']
Maximum active calls: 3
"""
