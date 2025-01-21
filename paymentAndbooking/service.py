from sqlalchemy.orm import Session
from sqlalchemy.future import select
import uuid
import json

from models import Booking, BookingType
from schemas import BookingCreate, BookingResponse



async def create_booking(db: Session, booking_data: BookingCreate) -> BookingResponse:
    """
    Create a new booking in the database.
    """
    new_booking = Booking(
        id=str(uuid.uuid4()),
        service_area=booking_data.service_area,
        home_address=booking_data.home_address,
        worker_duration=booking_data.worker_duration,
        worker_count=booking_data.worker_count,
        booking_type=BookingType(booking_data.booking_type).value,
        service_id=booking_data.service_id,
    )
    new_booking.set_dates(booking_data.dates)  # Pass list directly
    new_booking.set_times(booking_data.times)  # Pass list directly

    #print("Initialize Booking ORM Object:", new_booking.__dict__)

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking) 
    
    # Debugging: Log the ORM object
    #print("Booking ORM Object:", new_booking.__dict__)

    # Use the `from_orm` method to transform the object
    return BookingResponse.from_orm(new_booking)

async def get_booking(db: Session, booking_id: str) -> BookingResponse:
    """
    Retrieve a booking by its ID.
    """
    result = db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise ValueError(f"Booking with id {booking_id} not found.")
    return BookingResponse.from_orm(booking)  
