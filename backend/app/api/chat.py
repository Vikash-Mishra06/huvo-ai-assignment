from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.agent_service import AgentService
from app.services.booking_service import BookingService
from app.services.state_service import StateService


router = APIRouter(prefix="/chat", tags=["Conversation"])

agent_service = AgentService()
state_service = StateService()
booking_service = BookingService()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Process a customer message and handle supported conversation actions."""

    updated_state = state_service.update_state(
        state=request.state,
        message=request.message,
    )

    if request.site_visit_date and request.site_visit_time:
        booking_result = booking_service.book_site_visit(
            date=request.site_visit_date,
            time=request.site_visit_time,
            simulate_failure=request.simulate_booking_failure,
        )

        updated_state.site_visit_requested = True
        updated_state.site_visit_date = request.site_visit_date
        updated_state.site_visit_time = request.site_visit_time
        updated_state.booking_status = (
            "confirmed" if booking_result.success else "failed"
        )

        return ChatResponse(
            response=booking_result.message,
            state=updated_state,
        )

    response = agent_service.generate_response(
        state=updated_state,
        user_message=request.message,
    )

    return ChatResponse(
        response=response,
        state=updated_state,
    )