from pydantic import BaseModel, Field

from app.models.conversation import ConversationState


class ChatRequest(BaseModel):
    """Request body accepted by the conversation endpoint."""

    message: str = Field(min_length=1)
    state: ConversationState = Field(default_factory=ConversationState)

    site_visit_date: str | None = None
    site_visit_time: str | None = None
    simulate_booking_failure: bool = False
    escalation_reason: str | None = None
    follow_up_time: str | None = None

class ChatResponse(BaseModel):
    """Response returned by the conversation endpoint."""

    response: str
    state: ConversationState