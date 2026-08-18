from typing import Protocol


class LLMProvider(Protocol):
    """Defines the interface used by the agent to generate responses."""

    def generate(self, context: str) -> str:
        """Generate a response from the supplied conversation context."""
        ...


class MockLLMProvider:
    """Provides deterministic responses while developing without API costs."""

    def generate(self, context: str) -> str:
        """Return a deterministic response based on conversation context."""

        if '"language": "Hindi"' in context:
            return (
                "समझ गया। आप 3 BHK की तलाश कर रहे हैं। "
                "कृपया अपना बजट बताइए।"
            )

        if '"language": "Hinglish"' in context:
            return (
                "Bilkul. Aap 3 BHK dekh rahe hain. "
                "Aapka preferred budget kya hai?"
            )

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