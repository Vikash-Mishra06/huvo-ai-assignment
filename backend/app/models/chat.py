from pydantic import BaseModel, Field

from app.models.conversation import ConversationState


class ChatRequest(BaseModel):
    """Request body accepted by the conversation endpoint."""

    message: str = Field(min_length=1)
    state: ConversationState = Field(default_factory=ConversationState)


class ChatResponse(BaseModel):
    """Response returned by the conversation endpoint."""

    response: str
    state: ConversationState