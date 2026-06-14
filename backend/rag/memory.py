from collections import deque


class ConversationMemory:
    def __init__(self, max_turns: int = 5):
        self._history: deque[tuple[str, str]] = deque(maxlen=max_turns)

    def add(self, query: str, response: str) -> None:
        self._history.append((query, response))

    def get_history(self) -> list[tuple[str, str]]:
        return list(self._history)

    def format_for_prompt(self) -> str:
        if not self._history:
            return "No previous conversation history."
        return "\n".join(f"Query: {q}\nResponse: {r}" for q, r in self._history)

    def clear(self) -> None:
        self._history.clear()
