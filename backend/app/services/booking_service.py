from dataclasses import dataclass


@dataclass
class BookingResult:
    """Represents the outcome of a site-visit booking attempt."""

    success: bool
    message: str
    booking_id: str | None = None


class BookingService:
    """Handles site-visit booking operations."""

    def book_site_visit(
        self,
        date: str,
        time: str,
        simulate_failure: bool = False,
    ) -> BookingResult:
        """Create a simulated site-visit booking."""

        if simulate_failure:
            return BookingResult(
                success=False,
                message=(
                    "We couldn't complete the site-visit booking right now. "
                    "Please try another time or request assistance from our "
                    "sales team."
                ),
            )

        booking_id = f"HUVO-{date.replace('-', '')}-{time.replace(':', '')}"

        return BookingResult(
            success=True,
            message=(
                f"Your site visit has been booked for {date} at {time}. "
                f"Your booking reference is {booking_id}."
            ),
            booking_id=booking_id,
        )