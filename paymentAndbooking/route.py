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


@router.post("/create-booking", response_model=_schemas.BookingResponse, tags=["Bookings"], status_code=status.HTTP_201_CREATED)
async def create_booking_handler(booking_data: _schemas.BookingCreate, db: Session = Depends(get_db)):

    #return await _service.create_booking(db, booking_data)
    try:
        return await _service.create_booking(db, booking_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{booking_id}", response_model=_schemas.BookingResponse, tags=["Bookings"])
async def get_booking_handler(booking_id: str, db: Session = Depends(get_db)):
    try:
        return await _service.get_booking(db, booking_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )