from fastapi import HTTPException, APIRouter, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
import pika
import logging

from database import get_db
import schemas.user_schemas as _schemas
import services.user_service as _service

router = APIRouter()

@router.put("/user/profile", response_model=_schemas.UserProfileOut, tags=["Auth"])
async def update_user_profile(user_id: str, profile_data: _schemas.UserProfileUpdate, db: Session = Depends(get_db)):
    try:
        return await _service.update_user_profile(db, user_id, profile_data)
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating user profile")

@router.put("/worker/profile", response_model=_schemas.WorkerProfileOut, tags=["Auth"])
async def update_worker_profile(user_id: str, profile_data: _schemas.WorkerProfileUpdate, db: Session = Depends(get_db)):
    try:
        return await _service.update_worker_profile(db, user_id, profile_data)
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating worker profile")
    
@router.post("/addresses", response_model=_schemas.UnregisteredUserAddressOut, tags=["Addresses"])
async def create_address(address: _schemas.UnregisteredUserAddressCreate, db: Session = Depends(get_db)):
    try:
        return await _service.create_address(db, address)
    except Exception as e:
        logging.error(f"Error creating address: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the address")