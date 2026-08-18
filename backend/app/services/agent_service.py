from app.core.agent_prompt import HUVO_AGENT_PROMPT
from app.models.conversation import ConversationState


class AgentService:
    """Coordinates conversation state and agent behaviour."""

    def build_context(
        self,
        state: ConversationState,
        user_message: str,
    ) -> str:
        """Build the context that will eventually be sent to the LLM."""

        return f"""
SYSTEM INSTRUCTIONS:
{HUVO_AGENT_PROMPT}

CURRENT CONVERSATION STATE:
{state.model_dump_json(indent=2)}

CUSTOMER MESSAGE:
{user_message}
""".strip()