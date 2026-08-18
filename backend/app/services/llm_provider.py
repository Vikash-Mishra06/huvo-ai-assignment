from typing import Protocol


class LLMProvider(Protocol):
    """Defines the interface used by the agent to generate responses."""

    def generate(self, context: str) -> str:
        """Generate a response from the supplied conversation context."""
        ...


class MockLLMProvider:
    """Provides deterministic responses while developing without API costs."""

    def generate(self, context: str) -> str:
        """Return a response based on the current conversation context."""

        lowered_context = context.lower()

        # Handle price-related objections without inventing discounts or offers.
        if any(
            phrase in lowered_context
            for phrase in (
                "too expensive",
                "too costly",
                "bahut zyada",
                "mehenga",
                "expensive",
            )
        ):
            return (
                "I understand your concern about the price. I don't have "
                "confirmed information about discounts or special offers, "
                "so I don't want to give you incorrect information. "
                "Would you like me to arrange a conversation with our sales team?"
            )

        # Handle customers who are not ready to make a decision yet.
        if any(
            phrase in lowered_context
            for phrase in (
                "not ready",
                "not now",
                "later",
                "baad mein",
                "abhi nahi",
            )
        ):
            return (
                "Absolutely, no problem. I can help you follow up later. "
                "Would you like to share when you'd prefer us to contact you?"
            )

        # Handle customers who explicitly want a human representative.
        if any(
            phrase in lowered_context
            for phrase in (
                "human",
                "sales person",
                "salesperson",
                "representative",
                "agent se baat",
                "person se baat",
            )
        ):
            return (
                "Sure. I can arrange for a sales representative to assist you "
                "with this. I'll mark this conversation for human follow-up."
            )

        if '"language": "Hindi"' in context:
            return (
                "समझ गया। मैं आपकी जरूरत के अनुसार विकल्प देखने में मदद कर सकता हूँ। "
                "कृपया अपना बजट बताइए।"
            )

        if '"language": "Hinglish"' in context:
            return (
                "Bilkul. Main aapki requirement ke according options dekhne mein "
                "help kar sakta hoon. Aapka budget kya hai?"
            )

        if (
            '"property_type": "3 BHK"' in context
            and '"budget": "₹1.5 Cr"' in context
        ):
            return (
                "Got it. You're looking for a 3 BHK within ₹1.5 Cr for "
                "your family. Would you like to share your preferred "
                "location?"
            )

        return (
            "Thanks for sharing that. I can help you explore the available "
            "property options. Could you tell me your preferred budget?"
        )