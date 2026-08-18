from typing import Protocol


class LLMProvider(Protocol):
    """Defines the interface used by the agent to generate responses."""

    def generate(self, context: str) -> str:
        """Generate a response from the supplied conversation context."""
        ...


class MockLLMProvider:
    """Provides deterministic responses while developing without API costs."""

    def generate(self, context: str) -> str:
        """Return a simple response based on the current conversation state."""

        if '"property_type": "3 BHK"' in context and '"budget": "₹1.5 Cr"' in context:
            return (
                "Got it. You're looking for a 3 BHK within ₹1.5 Cr for "
                "your family. Would you like to share your preferred "
                "location?"
            )

        return (
            "Thanks for sharing that. I can help you explore the available "
            "property options. Could you tell me your preferred budget?"
        )