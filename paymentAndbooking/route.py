from fastapi import HTTPException, APIRouter, Depends, Request, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
import pika
import logging

from database import get_db
import service as _service
import schemas as _schemas


logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.post("/create-booking", response_model=_schemas.BookingResponse, tags=["Bookings"])
async def create_booking_handler(booking_data: _schemas.BookingCreate, db: Session = Depends(get_db)):
    try:
        return await _service.create_booking(db, booking_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/select-workers", tags=["Bookings"])
async def select_workers_for_booking(worker_selection: _schemas.WorkerSelection, db: Session = Depends(get_db)):
    """
    Allows users to select multiple workers for a booking.
    """
    try:
        return await _service.add_workers_to_booking(db, worker_selection)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{booking_id}", response_model=_schemas.BookingResponse, tags=["Bookings"])
async def get_booking_handler(booking_id: str, db: Session = Depends(get_db)):
    try:
        return await _service.get_booking(db, booking_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.get("/bookings/{booking_id}/summary", tags=["Bookings"])
async def booking_summary(booking_id: str, db: Session = Depends(get_db)):
    try:
        return await _service.get_booking_summary(db, booking_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )