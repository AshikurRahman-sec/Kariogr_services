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

@router.put("/user/profile", response_model=_schemas.UserProfileOut,)
async def update_user_profile(user_id: str, profile_data: _schemas.UserProfileUpdate, db: Session = Depends(get_db)):
    try:
        return await _service.update_user_profile(db, user_id, profile_data)
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating user profile")

@router.put("/worker/profile", response_model=_schemas.WorkerProfileOut,)
async def update_worker_profile(user_id: str, profile_data: _schemas.WorkerProfileUpdate, db: Session = Depends(get_db)):
    try:
        return await _service.update_worker_profile(db, user_id, profile_data)
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating worker profile")
    
@router.post("/create/unregister_user_address", response_model=_schemas.UnregisteredUserAddressOut,)
async def create_address(address: _schemas.UnregisteredUserAddressCreate, db: Session = Depends(get_db)):
    try:
        return await _service.create_address(db, address)
    except Exception as e:
        logging.error(f"Error creating address: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the address")
    
@router.get("/worker_zones/{service_id}", response_model=list[_schemas.WorkerZoneOut],)
async def get_worker_zones_by_skill(service_id: str, db: Session = Depends(get_db)):
    try:
        return await _service.get_worker_zones_by_skill(db, service_id)
    except Exception as e:
        logging.error(f"Error retrieving worker zones for skill {service_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching worker zones")

@router.post("/workers/filter", response_model=list[_schemas.WorkerWithSkillsAndZonesOut])
async def get_workers_by_skill_and_district(request: _schemas.WorkerFilterRequest, db: Session = Depends(get_db)):
    """
    Get workers based on skill and district.
    """
    workers = await _service.get_workers_by_skill_and_district(db, request.skill_id, request.district)
    try:
        workers = await _service.get_workers_by_skill_and_district(db, request.skill_id, request.district)
        if not workers:
            raise HTTPException(status_code=404, detail="No workers found for the given criteria")
        return workers
    except Exception as e:
        logging.error(f"Error retrieving workers: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching workers")