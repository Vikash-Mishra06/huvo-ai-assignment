from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.agent_service import AgentService
from app.services.state_service import StateService


router = APIRouter(prefix="/chat", tags=["Conversation"])

agent_service = AgentService()
state_service = StateService()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Process a customer message and return the updated conversation."""

    updated_state = state_service.update_state(
        state=request.state,
        message=request.message,
    )

    response = agent_service.generate_response(
        state=updated_state,
        user_message=request.message,
    )

    return ChatResponse(
        response=response,
        state=updated_state,
    )