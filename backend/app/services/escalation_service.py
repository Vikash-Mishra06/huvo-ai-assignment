from dataclasses import dataclass


@dataclass
class EscalationResult:
    """Represents the outcome of a human escalation request."""

    escalated: bool
    message: str
    escalation_id: str | None = None


class EscalationService:
    """Handles requests that need to be transferred to a human sales representative."""

    def escalate(self, reason: str) -> EscalationResult:
        """Create a simulated human handoff."""

        escalation_id = f"ESC-{abs(hash(reason)) % 100000:05d}"

        return EscalationResult(
            escalated=True,
            message=(
                "I've marked this conversation for a sales representative "
                "to follow up with you. They can assist you with the details "
                "I cannot confirm here."
            ),
            escalation_id=escalation_id,
        )