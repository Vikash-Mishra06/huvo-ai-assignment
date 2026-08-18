from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.agent_service import AgentService
from app.services.booking_service import BookingService
from app.services.escalation_service import EscalationService
from app.services.state_service import StateService
from app.services.follow_up_service import FollowUpService

router = APIRouter(prefix="/chat", tags=["Conversation"])

agent_service = AgentService()
state_service = StateService()
booking_service = BookingService()
escalation_service = EscalationService()
follow_up_service = FollowUpService()

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Process a customer message and handle supported conversation actions."""

    updated_state = state_service.update_state(
        state=request.state,
        message=request.message,
    )
    
    if request.follow_up_time:
        follow_up_result = follow_up_service.schedule_follow_up(
            preferred_time=request.follow_up_time
        )

        updated_state.follow_up_requested = True
        updated_state.follow_up_time = request.follow_up_time
        updated_state.follow_up_id = follow_up_result.follow_up_id

        return ChatResponse(
            response=follow_up_result.message,
            state=updated_state,
        )

    # Handle requests that need to be transferred to a human representative.
    if request.escalation_reason:
        escalation_result = escalation_service.escalate(
            reason=request.escalation_reason
        )

        updated_state.human_escalation_requested = True
        updated_state.escalation_id = escalation_result.escalation_id

        return ChatResponse(
            response=escalation_result.message,
            state=updated_state,
        )

    # Handle site-visit booking only when both date and time are available.
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