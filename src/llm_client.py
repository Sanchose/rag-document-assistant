import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Thin wrapper around the Anthropic API."""

    def __init__(self, model: str | None = None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set (check your .env)")
        self.client = Anthropic(api_key=api_key)
        self.model = model or os.getenv("MODEL_NAME", "claude-haiku-4-5")

    def generate(self, system: str, user: str, max_tokens: int = 1000) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text
