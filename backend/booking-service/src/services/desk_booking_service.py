from uuid import UUID

from src.messaging.messaging_manager import MessagingManager
from src.models.db.desk_booking import DeskBooking
from src.models.dto.desk_booking_create_request import DeskBookingCreateRequest
from src.models.dto.desk_booking_dto import DeskBookingDTO
from src.models.dto.desk_booking_update_request import DeskBookingUpdateRequest
from src.repositories.booking_repository import DeskBookingRepository


class DeskBookingService:
    """Service for managing desk bookings."""

    def __init__(
        self,
        repo: DeskBookingRepository,
        messaging: MessagingManager,
    ) -> None:
        """Initialize the DeskBookingService.

        Args:
            repo (DeskBookingRepository): The repository for desk bookings.
            messaging (MessagingManager): The messaging manager for handling messages.

        """
        self._repo = repo
        self._messaging = messaging

    async def create_booking(self, request: DeskBookingCreateRequest) -> DeskBookingDTO:
        """Create a new desk booking.

        Args:
            request (DeskBookingCreateRequest): The request DTO containing booking details.

        Returns:
            DeskBookingDTO: The response DTO containing created booking details.

        """  # noqa: E501
        booking = self._repo.create(DeskBooking.from_create_dto(request))
        return DeskBookingDTO.from_entity(booking)

    async def list_bookings(self) -> list[DeskBookingDTO]:
        """List all desk bookings.

        Returns:
            list[DeskBookingDTO]: A list of all desk bookings.

        """
        bookings = self._repo.get_all()
        return [DeskBookingDTO.from_entity(booking) for booking in bookings]

    async def get_booking(self, booking_id: UUID) -> DeskBookingDTO | None:
        """Get a specific desk booking by its ID.

        Args:
            booking_id (UUID): The ID of the booking to retrieve.

        Returns:
            DeskBookingDTO: The requested booking data.

        """
        booking = self._repo.get_by_id(booking_id)
        return DeskBookingDTO.from_entity(booking) if booking else None

    async def update_booking(
        self, booking_id: UUID, request: DeskBookingUpdateRequest
    ) -> DeskBookingDTO | None:
        """Update an existing desk booking.

        Args:
            booking_id (UUID): The ID of the booking to update.
            request (DeskBookingDTO): The DTO containing updated booking details.

        Returns:
            DeskBookingDTO: The updated booking data.

        """
        booking = self._repo.get_by_id(booking_id)
        if booking is None:
            return None
        updated_booking = self._repo.update(
            DeskBooking.from_update_dto(booking.id, request)
        )
        return DeskBookingDTO.from_entity(updated_booking)

    async def delete_booking(self, booking_id: UUID) -> bool:
        """Delete a desk booking by its ID.

        Args:
            booking_id (UUID): The ID of the booking to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.

        """
        return self._repo.delete(booking_id)
