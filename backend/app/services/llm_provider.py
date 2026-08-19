from typing import Protocol


class LLMProvider(Protocol):
    """Defines the interface used by the agent to generate responses."""

    def generate(self, context: str) -> str:
        """Generate a response from the supplied conversation context."""
        ...


class MockLLMProvider:
    """Provides deterministic responses while developing without API costs."""

    def generate(self, context: str) -> str:
        """Return a predictable response based on the conversation state."""

        customer_message = ""

        if "CUSTOMER MESSAGE:" in context:
            customer_message = context.split(
                "CUSTOMER MESSAGE:",
                1,
            )[1].strip()

        lowered_message = customer_message.lower()

        # Handle price-related objections without inventing discounts or offers.
        if any(
            phrase in lowered_message
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
            phrase in lowered_message
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
            phrase in lowered_message
            for phrase in (
                "human",
                "sales person",
                "salesperson",
                "representative",
                "sales representative",
                "agent se baat",
                "person se baat",
            )
        ):
            return (
                "Sure. I can arrange for a sales representative to assist you "
                "with this. I'll mark this conversation for human follow-up."
            )

        # Use the detected language for the next qualification question.
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

        # Read the current qualification state so the agent asks for the
        # next missing piece instead of repeating an earlier question.
        has_property = '"property_type":' in context and '"property_type": null' not in context
        has_budget = '"budget":' in context and '"budget": null' not in context
        has_location = (
            '"preferred_location":' in context
            and '"preferred_location": null' not in context
        )
        has_purpose = (
            '"buying_purpose":' in context
            and '"buying_purpose": null' not in context
        )
        has_timeline = (
            '"purchase_timeline":' in context
            and '"purchase_timeline": null' not in context
        )

        # Ask for property type when it is still missing.
        if not has_property:
            return (
                "Sure, I can help you explore the available properties. "
                "What type of property are you looking for, such as a 2 BHK or 3 BHK?"
            )

        # Ask for budget when it is still missing.
        if not has_budget:
            return "Got it. What is your preferred budget for the property?"

        # Ask for location after property and budget are known.
        if not has_location:
            return "Great. Which location or area do you prefer?"

        # Ask about buying purpose.
        if not has_purpose:
            return (
                "Thanks. Is the property mainly for self-use or are you "
                "considering it as an investment?"
            )

        # Ask about the expected purchase timeline.
        if not has_timeline:
            return (
                "Understood. When are you planning to make the purchase?"
            )

        # Once the main qualification fields are complete, move the
        # conversation toward a useful sales action.
        return (
            "Thanks, I have the main requirements. Would you like me to "
            "help arrange a site visit for the property?"
        )