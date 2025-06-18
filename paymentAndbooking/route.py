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
    
@router.put("/payment-confirm", tags=["Bookings"])
def confirm_order(confirm_data: _schemas.BookingConfirm, db: Session = Depends(get_db)):
    try:
        return _service.confirm_booking(db, confirm_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/make-payment", response_model=_schemas.PaymentResponse, tags=["Bookings"])
def make_payment(payload: _schemas.CreatePaymentRequest, db: Session = Depends(get_db)):
    try:
        payment = _service.create_payment(db, payload)
        return payment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/bag/add", response_model=_schemas.BagItemResponse, tags=["addtobag"])
async def add_to_bag(request: _schemas.AddToBagRequest, db: Session = Depends(get_db)):
    try:
        return await _service.add_to_bag(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bag/remove", response_model=dict, tags=["addtobag"])
async def remove_from_bag(request: _schemas.RemoveFromBagRequest, db: Session = Depends(get_db)):
    item = await _service.remove_from_bag(db, request.bag_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item removed from bag"}

@router.get("/bag/bag-list", response_model=list[_schemas.BagItemResponse], tags=["addtobag"])
async def view_bag(user_id: str = None, unregistered_address_id: str = None, db: Session = Depends(get_db)):
    try:
        items = await _service.get_bag_items_by_user(db, user_id, unregistered_address_id)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.post("/apply-cupon", response_model=_schemas.CouponInfoResponse)
def apply_coupon_route(data: _schemas.ApplyCouponRequest, db: Session = Depends(get_db)):
    try:
        return _service.apply_coupon(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the error in real apps
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/booking-cupon/{booking_id}", response_model=_schemas.CouponInfoResponse)
def get_coupon_for_booking(booking_id: str, db: Session = Depends(get_db)):
    try:
        return _service.get_coupon_by_booking(db, booking_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/all-cupons", response_model=list[_schemas.CouponResponse])
def get_all_coupons(db: Session = Depends(get_db)):
    try:
        return _service.list_all_coupons(db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.get("/service/{service_id}/user/{user_id}", response_model= _schemas.OfferResponse)
def get_offers_for_service_and_user(service_id: str, user_id: str, db: Session = Depends(get_db)):
    try:
        offers = _service.get_active_offers_by_user_and_service(db, user_id, service_id)

        if not offers:
            raise HTTPException(status_code=404, detail="No active offers for this user and service")

        return offers
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")