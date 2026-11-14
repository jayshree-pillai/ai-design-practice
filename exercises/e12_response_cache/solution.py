from time import monotonic


class ResponseCache:
    def __init__(self, generate, clock=monotonic):
        self.generate = generate
        self.clock = clock
        self.cache = {}

    def ask(self, customer_id, question, prompt_version):
        key = (customer_id, question, prompt_version)
        entry = self.cache.get(key)

        if entry is not None and self.clock() < entry["expires_at"]:
            return {
                "status": "answered",
                "answer": entry["answer"],
                "cached": True,
            }

        self.cache.pop(key, None)

        try:
            answer = self.generate(customer_id, question, prompt_version)
        except TimeoutError:
            return {"status": "failed", "answer": None, "cached": False}

        # Start the 60 seconds after generation finishes.
        self.cache[key] = {
            "answer": answer,
            "expires_at": self.clock() + 60,
        }

        return {"status": "answered", "answer": answer, "cached": False}
