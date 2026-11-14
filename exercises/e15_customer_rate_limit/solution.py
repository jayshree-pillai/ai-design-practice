
## limiter = CustomerRateLimiter(model, clock)
## result = limiter.handle("C1", "What is the return policy?")

from threading import Lock


class CustomerRateLimiter:
    def __init__(self, model, clock):
        self.model = model
        self.clock = clock
        self.counts = {}
        self.lock = Lock()

    def handle(self, customer_id, question):
        with self.lock:
            now = self.clock()
            key = (customer_id, now // 60)
            used = self.counts.get(key, 0)

            if used >= 5:
                return {
                    "status": "rate_limited",
                    "retry_after": 60 - now % 60,
                }

            self.counts[key] = used + 1

        try:
            answer = self.model(customer_id, question)
        except Exception:
            return {"status": "failed", "answer": None}

        return {"status": "answered", "answer": answer}
