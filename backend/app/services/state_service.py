import re

from app.models.conversation import ConversationState


class StateService:
    """Extracts useful lead information from customer messages."""

    def update_state(
        self,
        state: ConversationState,
        message: str,
    ) -> ConversationState:
        """Update known lead details without overwriting existing information."""

        text = message.strip()

        self._extract_property_type(state, text)
        self._extract_budget(state, text)
        self._extract_language(state, text)
        self._extract_buying_purpose(state, text)
        self._extract_location(state, text)
        self._extract_purchase_timeline(state, text)

        return state

    def _extract_property_type(
        self,
        state: ConversationState,
        text: str,
    ) -> None:
        """Detect common residential configurations such as 2 BHK or 3 BHK."""

        match = re.search(r"\b([234])\s*bhk\b", text, re.IGNORECASE)

        if match:
            state.property_type = f"{match.group(1)} BHK"

    def _extract_budget(
        self,
        state: ConversationState,
        text: str,
    ) -> None:
        """Detect simple crore/lakh budget expressions."""

        match = re.search(
            r"(?:under|below|upto|up to|budget(?:\s+is)?|around)?\s*"
            r"(?:₹|rs\.?|inr)?\s*"
            r"(\d+(?:\.\d+)?)\s*(crore|cr|lakh|lac)\b",
            text,
            re.IGNORECASE,
        )

        if match:
            amount = match.group(1)
            unit = match.group(2).lower()

            if unit in {"crore", "cr"}:
                state.budget = f"₹{amount} Cr"
            else:
                state.budget = f"₹{amount} Lakh"

    def _extract_language(
        self,
        state: ConversationState,
        text: str,
    ) -> None:
        """Detect whether the customer is speaking English, Hindi, or Hinglish."""

        if re.search(r"[\u0900-\u097F]", text):
            state.language = "Hindi"
            return

        hindi_words = {
            "bhai",
            "chahiye",
            "hai",
            "hain",
            "mera",
            "mujhe",
            "aap",
            "kya",
            "kitna",
            "ke",
            "liye",
            "mein",
            "milega",
            "chahta",
            "chahti",
        }

        words = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))

        if len(words.intersection(hindi_words)) >= 2:
            state.language = "Hinglish"
        else:
            state.language = "English"

    def _extract_buying_purpose(
        self,
        state: ConversationState,
        text: str,
    ) -> None:
        """Detect whether the lead mentions self-use or investment."""

        lowered = text.lower()

        investment_terms = (
            "investment",
            "invest",
            "rental income",
            "rent ke liye",
            "rental",
        )

        self_use_terms = (
            "for my family",
            "for myself",
            "for me",
            "self use",
            "self-use",
            "khud ke liye",
            "family ke liye",
            "rehne ke liye",
        )

        if any(term in lowered for term in investment_terms):
            state.buying_purpose = "Investment"
        elif any(term in lowered for term in self_use_terms):
            state.buying_purpose = "Self-use"

    def _extract_location(
        self,
        state: ConversationState,
        text: str,
    ) -> None:
        """Detect common Gurgaon/Delhi NCR location mentions."""

        known_locations = (
            "Gurgaon",
            "Gurugram",
            "Noida",
            "Greater Noida",
            "Delhi",
            "Faridabad",
            "Ghaziabad",
            "Dwarka",
            "Manesar",
        )

        lowered = text.lower()

        for location in known_locations:
            if location.lower() in lowered:
                state.preferred_location = location
                return

    def _extract_purchase_timeline(
        self,
        state: ConversationState,
        text: str,
    ) -> None:
        """Detect simple purchase timelines such as weeks or months."""

        lowered = text.lower()

        match = re.search(
            r"\b(?:within|in|after)\s+"
            r"(\d+(?:\.\d+)?)\s*"
            r"(week|weeks|month|months|year|years)\b",
            lowered,
        )

        if match:
            amount = match.group(1)
            unit = match.group(2)

            state.purchase_timeline = f"{amount} {unit}"
            return

        timeline_phrases = (
            ("immediately", "Immediately"),
            ("as soon as possible", "As soon as possible"),
            ("this month", "This month"),
            ("next month", "Next month"),
            ("next year", "Next year"),
            ("not sure", "Not decided"),
        )

        for phrase, value in timeline_phrases:
            if phrase in lowered:
                state.purchase_timeline = value
                return