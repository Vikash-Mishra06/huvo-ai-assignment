from app.models.conversation import ConversationState


class AnalyticsService:
    """Builds a simple summary of the lead conversation."""

    def build_summary(self, state: ConversationState) -> dict:
        """Return the key outcomes collected during the conversation."""

        qualification_fields = {
            "budget": state.budget,
            "preferred_location": state.preferred_location,
            "property_type": state.property_type,
            "buying_purpose": state.buying_purpose,
            "purchase_timeline": state.purchase_timeline,
        }

        completed_fields = sum(
            value is not None for value in qualification_fields.values()
        )

        qualification_score = round(
            (completed_fields / len(qualification_fields)) * 100
        )

        return {
            "qualification_score": qualification_score,
            "qualified_fields": qualification_fields,
            "site_visit": {
                "requested": state.site_visit_requested,
                "status": state.booking_status,
                "date": state.site_visit_date,
                "time": state.site_visit_time,
            },
            "follow_up": {
                "requested": state.follow_up_requested,
                "time": state.follow_up_time,
                "id": state.follow_up_id,
            },
            "human_escalation": {
                "requested": state.human_escalation_requested,
                "id": state.escalation_id,
            },
        }