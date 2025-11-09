from uuid import UUID

from sqlmodel import Session, select

from src.models.db.desk_booking import DeskBooking


class DeskBookingRepository:
    """Repository for managing DeskBooking entities in the database."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self._session = session

    def create(self, booking: DeskBooking) -> DeskBooking:
        """Create a new DeskBooking in the database.

        Args:
            booking (DeskBooking): The DeskBooking entity to create.

        Returns:
            DeskBooking: The created DeskBooking entity with updated fields.

        """
        self._save_and_refresh(booking)
        return booking

    def get_by_id(self, booking_id: UUID) -> DeskBooking | None:
        """Retrieve a DeskBooking by its ID.

        Args:
            booking_id (UUID): The ID of the DeskBooking to retrieve.

        Returns:
            DeskBooking | None: The DeskBooking entity if found, else None.

        """
        return self._session.get(DeskBooking, booking_id)

    def get_all(self) -> list[DeskBooking]:
        """Retrieve all DeskBooking entities from the database.

        Returns:
            list[DeskBooking]: A list of all DeskBooking entities.

        """
        return list(self._session.exec(select(DeskBooking)).all())

    def update(self, booking: DeskBooking) -> DeskBooking | None:
        """Update an existing DeskBooking in the database.

        Args:
            booking (DeskBooking): The DeskBooking entity to update.

        Returns:
            DeskBooking: The updated DeskBooking entity.

        """
        update_booking = self._update_fields(booking)
        if update_booking is None:
            return None
        self._save_and_refresh(update_booking)
        return booking

    def delete(self, booking_id: UUID) -> bool:
        """Delete a DeskBooking by its ID.

        Args:
            booking_id (UUID): The ID of the DeskBooking to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.

        """
        booking = self.get_by_id(booking_id)
        if booking is None:
            return False
        self._session.delete(booking)
        self._session.commit()
        return True

    def _save_and_refresh(self, instance: DeskBooking) -> None:
        """Save and refresh an instance in the database.

        Args:
            instance (DeskBooking): The DeskBooking instance to save and refresh.

        """
        self._session.add(instance)
        self._session.commit()
        self._session.refresh(instance)

    def _update_fields(self, updated_booking: DeskBooking) -> DeskBooking | None:
        """Update fields of an existing DeskBooking.

        Args:
            updated_booking (DeskBooking): The DeskBooking entity with updated fields.

        Returns:
            DeskBooking | None: The updated DeskBooking entity or None if not found.

        """
        current_booking = self.get_by_id(updated_booking.id)
        if current_booking is None:
            return None
        current_booking.user_id = updated_booking.user_id
        current_booking.desk_id = updated_booking.desk_id
        current_booking.start_time = updated_booking.start_time
        current_booking.end_time = updated_booking.end_time
        return current_booking
