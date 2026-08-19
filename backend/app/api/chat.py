import re

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


def extract_booking_details(message: str) -> tuple[str | None, str | None]:
    """Extract a simple site-visit date and time from a customer message."""

    date_match = re.search(
        r"\b(\d{1,2})\s+"
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\b",
        message,
        re.IGNORECASE,
    )

    time_match = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*"
        r"(AM|PM)\b",
        message,
        re.IGNORECASE,
    )

    if not date_match or not time_match:
        return None, None

    day = date_match.group(1)
    month = date_match.group(2).title()

    hour = time_match.group(1)
    minute = time_match.group(2) or "00"
    meridiem = time_match.group(3).upper()

    return (
        f"{day} {month}",
        f"{hour}:{minute} {meridiem}",
    )


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Process a customer message and handle supported conversation actions."""

    updated_state = state_service.update_state(
        state=request.state,
        message=request.message,
    )

    # Extract booking details when the customer provides a date and time
    # directly in their message.
    extracted_date, extracted_time = extract_booking_details(request.message)

    site_visit_date = request.site_visit_date or extracted_date
    site_visit_time = request.site_visit_time or extracted_time

    # Handle follow-up requests before normal agent responses.
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
    if site_visit_date and site_visit_time:
        booking_result = booking_service.book_site_visit(
            date=site_visit_date,
            time=site_visit_time,
            simulate_failure=request.simulate_booking_failure,
        )

        updated_state.site_visit_requested = True
        updated_state.site_visit_date = site_visit_date
        updated_state.site_visit_time = site_visit_time
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