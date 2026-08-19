from typing import Protocol


class LLMProvider(Protocol):
    """Defines the interface used by the agent to generate responses."""

    def generate(self, context: str) -> str:
        """Generate a response from the supplied conversation context."""
        ...


class MockLLMProvider:
    """Provides deterministic responses while developing without API costs."""

    def generate(self, context: str) -> str:
        """Return a context-aware response based on the conversation state."""

        customer_message = ""

        if "CUSTOMER MESSAGE:" in context:
            customer_message = context.split(
                "CUSTOMER MESSAGE:",
                1,
            )[1].strip()

        lowered_message = customer_message.lower()

        # ---------------------------------------------------------
        # Objections
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Customer is not ready
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Human escalation
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Read qualification state
        # ---------------------------------------------------------

        has_property = (
            '"property_type":' in context
            and '"property_type": null' not in context
        )

        has_budget = (
            '"budget":' in context
            and '"budget": null' not in context
        )

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

        # ---------------------------------------------------------
        # Hindi
        # ---------------------------------------------------------

        if '"language": "Hindi"' in context:

            if not has_property:
                return (
                    "समझ गया। आप किस प्रकार की प्रॉपर्टी देख रहे हैं, "
                    "जैसे 2 BHK या 3 BHK?"
                )

            if not has_budget:
                return (
                    "ठीक है। आपका पसंदीदा बजट कितना है?"
                )

            if not has_location:
                return (
                    "बहुत अच्छा। आप किस लोकेशन या एरिया में प्रॉपर्टी "
                    "देखना पसंद करेंगे?"
                )

            if not has_purpose:
                return (
                    "क्या यह प्रॉपर्टी आपके रहने के लिए है या "
                    "निवेश के लिए?"
                )

            if not has_timeline:
                return (
                    "आप कितने समय के अंदर प्रॉपर्टी खरीदना चाहते हैं?"
                )

            return (
                "धन्यवाद। आपकी मुख्य जरूरतें समझ में आ गई हैं। "
                "क्या आप प्रॉपर्टी के लिए साइट विजिट बुक करना चाहेंगे?"
            )

        # ---------------------------------------------------------
        # Hinglish
        # ---------------------------------------------------------

        if '"language": "Hinglish"' in context:

            if not has_property:
                return (
                    "Bilkul. Aap kis type ki property dekh rahe hain, "
                    "jaise 2 BHK ya 3 BHK?"
                )

            if not has_budget:
                return (
                    "Got it. Aapka preferred budget kya hai?"
                )

            if not has_location:
                return (
                    "Great. Aapki preferred location ya area kaunsa hai?"
                )

            if not has_purpose:
                return (
                    "Samajh gaya. Property self-use ke liye hai "
                    "ya investment ke liye?"
                )

            if not has_timeline:
                return (
                    "Understood. Aap kab tak property purchase karna "
                    "chahte hain?"
                )

            return (
                "Bilkul. Aapki main requirements clear hain. "
                "Kya aap site visit arrange karna chahenge?"
            )

        # ---------------------------------------------------------
        # English
        # ---------------------------------------------------------

        if not has_property:
            return (
                "Sure, I can help you explore the available properties. "
                "What type of property are you looking for, such as a 2 BHK or 3 BHK?"
            )

        if not has_budget:
            return (
                "Got it. What is your preferred budget for the property?"
            )

        if not has_location:
            return (
                "Great. Which location or area do you prefer?"
            )

        if not has_purpose:
            return (
                "Thanks. Is the property mainly for self-use or are you "
                "considering it as an investment?"
            )

        if not has_timeline:
            return (
                "Understood. When are you planning to make the purchase?"
            )

        # ---------------------------------------------------------
        # Qualification complete
        # ---------------------------------------------------------

        return (
            "Thanks, I have the main requirements. Would you like me to "
            "help arrange a site visit for the property?"
        )