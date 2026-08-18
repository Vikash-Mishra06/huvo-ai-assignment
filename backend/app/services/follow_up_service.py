from dataclasses import dataclass


@dataclass
class FollowUpResult:
    """Represents a scheduled customer follow-up."""

    scheduled: bool
    message: str
    follow_up_id: str | None = None


class FollowUpService:
    """Handles simulated customer follow-up requests."""

    def schedule_follow_up(self, preferred_time: str) -> FollowUpResult:
        """Create a simulated follow-up request."""

        follow_up_id = f"FU-{abs(hash(preferred_time)) % 100000:05d}"

        return FollowUpResult(
            scheduled=True,
            message=(
                f"Sure, I'll note your preference for a follow-up at "
                f"{preferred_time}. Our sales team can follow up with you then."
            ),
            follow_up_id=follow_up_id,
        )