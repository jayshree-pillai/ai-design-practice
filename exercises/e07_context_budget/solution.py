def build_context(system, question, history, budget):
    # Always keep the system instruction and current question.
    total_tokens = system["tokens"] + question["tokens"]

    if total_tokens > budget:
        raise ValueError("System instruction and current question exceed the budget")

    # Keep whole turns, starting with the newest.
    kept_turns = []
    for turn in reversed(history):
        if total_tokens + turn["tokens"] > budget:
            break

        kept_turns.append(turn)
        total_tokens += turn["tokens"]

    # Put the selected messages back into chronological order.
    messages = [system["message"]]
    for turn in reversed(kept_turns):
        messages.extend(turn["messages"])
    messages.append(question["message"])

    return {"messages": messages, "total_tokens": total_tokens}


def main():
    # Sample token counts are supplied, not calculated.
    system = {
        "message": {"role": "system", "content": "You are a helpful assistant."},
        "tokens": 4,
    }
    question = {
        "message": {"role": "user", "content": "Can I track my refund?"},
        "tokens": 4,
    }

    # Stored history: oldest turn first, newest turn last.
    history = [
        {
            "messages": [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello!"},
            ],
            "tokens": 3,
        },
        {
            "messages": [
                {"role": "user", "content": "Can I get a refund?"},
                {"role": "assistant", "content": "Yes, within 30 days."},
            ],
            "tokens": 5,
        },
        {
            "messages": [
                {"role": "user", "content": "How long does it take?"},
                {"role": "assistant", "content": "Five working days."},
            ],
            "tokens": 7,
        },
    ]

    result = build_context(system, question, history, budget=20)

    for message in result["messages"]:
        print(f"{message['role']}: {message['content']}")
    print("Total tokens:", result["total_tokens"])


if __name__ == "__main__":
    main()

"""
Remember these three steps:
1. Reserve tokens for the system instruction and current question.
2. Select backwards through history; break at the first turn that won’t fit.
3. Restore order before returning the messages.
append() adds one message; extend() adds all messages from a selected turn.

Stored history is the full conversation. Context is the selection sent to the model for this call. This function leaves the stored history unchanged.


"""
