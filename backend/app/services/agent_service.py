from app.core.agent_prompt import HUVO_AGENT_PROMPT
from app.models.conversation import ConversationState
from app.services.llm_provider import LLMProvider, MockLLMProvider


class AgentService:
    """Coordinates conversation state, prompts, and LLM responses."""

    def __init__(self, llm_provider: LLMProvider | None = None):
        self.llm_provider = llm_provider or MockLLMProvider()

    def build_context(
        self,
        state: ConversationState,
        user_message: str,
    ) -> str:
        """Build the context that is passed to the language model."""

        return f"""
SYSTEM INSTRUCTIONS:
{HUVO_AGENT_PROMPT}

CURRENT CONVERSATION STATE:
{state.model_dump_json(indent=2)}

CUSTOMER MESSAGE:
{user_message}
""".strip()

    def generate_response(
        self,
        state: ConversationState,
        user_message: str,
    ) -> str:
        """Generate an agent response using the configured LLM provider."""

        context = self.build_context(state, user_message)

        return self.llm_provider.generate(context)