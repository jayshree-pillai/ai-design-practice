from collections import deque
from uuid import uuid4


class ReportJobs:
    def __init__(self, generate):
        self.generate = generate
        self.jobs = {}
        self.requests = {}
        self.queue = deque()

    def submit(self, customer_id, request_key, topic):
        key = (customer_id, request_key)

        if key in self.requests:
            job_id = self.requests[key]
            if self.jobs[job_id]["topic"] != topic:
                return {"status": "conflict", "job_id": None}
            return {"status": "accepted", "job_id": job_id}

        job_id = uuid4().hex
        self.jobs[job_id] = {
            "customer_id": customer_id,
            "topic": topic,
            "status": "queued",
            "report": None,
            "attempts": 0,
        }
        self.requests[key] = job_id
        self.queue.append(job_id)

        return {"status": "accepted", "job_id": job_id}

    def get_status(self, customer_id, job_id):
        job = self.jobs.get(job_id)

        if job is None or job["customer_id"] != customer_id:
            raise LookupError("Job not found")

        return job.copy()

    def work_one(self):
        if not self.queue:
            return

        job_id = self.queue.popleft()
        job = self.jobs[job_id]
        job["status"] = "running"

        for _ in range(2):
            job["attempts"] += 1
            try:
                job["report"] = self.generate(
                    job["customer_id"], job["topic"]
                )
                job["status"] = "completed"
                break
            except TimeoutError:
                continue
        else:
            job["status"] = "failed"

    def drain(self):
        while self.queue:
            self.work_one()
