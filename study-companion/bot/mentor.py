import httpx

EXPLAIN_SYSTEM = (
    "You are a concise DevOps mentor. Answer in under 200 words. "
    "Use analogies from Linux and Kubernetes when helpful. Be direct and practical."
)

HINT_SYSTEM = (
    "You are a DevOps mentor giving a hint. Do NOT give the full answer. "
    "Give a directional nudge in 2-3 sentences maximum. Make the student think."
)

QUIZ_SYSTEM = (
    "You are a DevOps mentor creating a quiz. Generate exactly 1 multiple-choice question "
    "with options A, B, C, D. Do NOT reveal the answer yet — wait for the student to reply."
)


class Mentor:
    def __init__(self, host: str, model: str, timeout: int = 60):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def _call(self, system: str, prompt: str) -> str:
        url = f"{self.host}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()

    async def explain(self, topic: str, task_title: str, phase: int) -> str:
        prompt = (
            f"The student is on Phase {phase}, working on: {task_title}.\n"
            f"Explain this concept: {topic}"
        )
        return await self._call(EXPLAIN_SYSTEM, prompt)

    async def hint(self, step_content: str, task_title: str) -> str:
        prompt = (
            f"The student is working on: {task_title}\n"
            f"They are stuck on this step: {step_content}\n"
            f"Give a hint."
        )
        return await self._call(HINT_SYSTEM, prompt)

    async def quiz(self, task_title: str, phase: int) -> str:
        prompt = f"Phase {phase} topic — {task_title}. Generate a quiz question."
        return await self._call(QUIZ_SYSTEM, prompt)

    async def is_reachable(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.host}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
