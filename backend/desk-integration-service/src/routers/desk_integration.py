# Dummy Router for demonstration purposes
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class Booking(BaseModel):
    booking_id: int
    user_id: int
    desk_id: int


bookings = [
    Booking(booking_id=1, user_id=1, desk_id=1),
    Booking(booking_id=2, user_id=2, desk_id=2),
]

router = APIRouter(prefix="/api/v1", tags=["bookings"])


@router.get("/bookings")
def get_bookings():
    return bookings


@router.get("/bookings/{booking_id}", response_model=Booking)
def get_booking_with_id(booking_id: int) -> Booking:
    if booking_id not in [booking.booking_id for booking in bookings]:
        raise HTTPException(
            status_code=404, detail=f"Booking with id={booking_id} not found"
        )
    return next(booking for booking in bookings if booking.booking_id == booking_id)


@router.post("/bookings", response_model=list[Booking])
def create_booking(booking: Booking) -> list[Booking]:
    bookings.append(booking)
    return bookings
