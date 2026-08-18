from typing import Optional

from pydantic import BaseModel


class ConversationState(BaseModel):
    """Stores the information collected during a lead conversation."""

    name: Optional[str] = None
    language: Optional[str] = None

    budget: Optional[str] = None
    preferred_location: Optional[str] = None
    property_type: Optional[str] = None

    buying_purpose: Optional[str] = None
    purchase_timeline: Optional[str] = None

    site_visit_requested: bool = False
    site_visit_date: Optional[str] = None
    site_visit_time: Optional[str] = None

    booking_status: Optional[str] = None
    human_escalation_requested: bool = False