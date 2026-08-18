from openai import OpenAI

from app.core.config import settings


class LLMService:
    """Handles communication with the language model."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.model_name

    def generate_response(self, message: str) -> str:
        """Send a user message to the model and return its response."""
        response = self.client.responses.create(
            model=self.model_name,
            input=message,
        )

        return response.output_text