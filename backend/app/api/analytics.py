from fastapi import APIRouter

from app.models.conversation import ConversationState
from app.services.analytics_service import AnalyticsService


router = APIRouter(prefix="/analytics", tags=["Analytics"])

analytics_service = AnalyticsService()


@router.post("/summary")
def get_summary(state: ConversationState):
    """Return qualification and conversation outcome metrics."""

    return analytics_service.build_summary(state)