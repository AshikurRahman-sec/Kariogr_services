from fastapi import HTTPException, APIRouter, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
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

@router.post("/workers/filter")
async def get_workers_by_skill_and_district(
    request: _schemas.WorkerFilterRequest,
    size: int = Query(10, ge=1),  # Default 10, minimum 1
    page: int = Query(0, ge=0),  # Default 0, minimum 0
    db: Session = Depends(get_db),
):
    """
    Get workers based on skill and district with pagination using query parameters.
    """
    await _service.get_workers_by_skill_and_district(
            db,
            request.skill_id, 
            request.district,
            size,
            page,
            "string"
        )
    try:
        response = await _service.get_workers_by_skill_and_district(
            db,
            request.skill_id, 
            request.district,
            size,
            page,
            "string"
        )
        
        if not response["data"]:
            raise HTTPException(status_code=404, detail="No workers found for the given criteria")
    
        return response
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        logging.error(f"Error retrieving workers: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching workers")

@router.post("/workers/by-zone", response_model=_schemas.PaginatedWorkerListResponse )
async def get_workers_by_zone(
    request: _schemas.WorkerByZoneRequest,
    size: int = Query(10, ge=1),  # Default 10, minimum 1
    page: int = Query(0, ge=0),  # Default 0, minimum 0
    db: Session = Depends(get_db),
):
    """
    Fetch paginated workers by specific user_id and working zone.
    """
    workers, total_workers = await _service.get_workers_by_zone(db, request.worker_id, request.district, size, page)
    try:
        workers, total_workers = await _service.get_workers_by_zone(db, request.worker_id, request.district, size, page)
        
        if not workers:
            raise HTTPException(status_code=404, detail="No workers found in this zone")

        return {
            "data": workers,
            "total_workers": total_workers,
            "page": page,
            "size": size
        }
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        logging.error(f"Error retrieving workers: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching workers")

@router.post(
    "/worker-skill-rating",
    response_model=_schemas.CreateWorkerSkillRatingResponse,
    #tags=["ratings"]
)
async def create_worker_skill_rating(
    request: _schemas.CreateWorkerSkillRatingRequest,
    db: Session = Depends(get_db),
):
    try:
        return await _service.create_or_update_worker_skill_rating(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/worker_details/{worker_id}/{skill_id}", 
            response_model=_schemas.WorkerWithSkillsAndZonesOut
            )
async def get_worker_details(worker_id: str, skill_id: str, db: Session = Depends(get_db)):
    result = await _service.get_worker_details_by_worker_and_skill(db, worker_id, skill_id)
    try:
        result = await _service.get_worker_details_by_worker_and_skill(db, worker_id, skill_id)
        if not result:
            raise HTTPException(status_code=404, detail="Worker or skill not found")
        return result
    except Exception as e:
        logging.error(f"Error getting worker details for worker_id={worker_id}, skill_id={skill_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/post-comment", response_model=_schemas.CommentResponse)
async def post_comment(comment: _schemas.CreateComment, db: Session = Depends(get_db)):
    try:
        return await _service.create_comment(db, comment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/get-comment/{worker_id}/{skill_id}", response_model=List[_schemas.CommentResponse])
def fetch_comments(
    worker_id: str,
    skill_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    try:
        return _service.get_top_level_comments(db, worker_id, skill_id, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/comment/replies/{parent_comment_id}", response_model=List[_schemas.CommentResponse])
def fetch_replies(
    parent_comment_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    try:
        return _service.get_replies(db, parent_comment_id, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/comment/reaction", response_model=_schemas.ReactionResponse)
def react_to_comment(
    reaction_data: _schemas.CreateReaction,
    db: Session = Depends(get_db),
):
    try:
        return _service.create_reaction(db, reaction_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/worker/bookmark", response_model=_schemas.WorkerBookmarkOut)
async def create_worker_bookmark(bookmark_data: _schemas.WorkerBookmarkCreate, db: Session = Depends(get_db)):
    try:
        return _service.add_worker_bookmark(db, bookmark_data)
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while bookmarking worker")
    
@router.delete("/worker/bookmark")
async def delete_worker_bookmark(user_id: str, worker_id: str, db: Session = Depends(get_db)):
    try:
        return _service.remove_worker_bookmark(db, user_id, worker_id)
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while removing bookmark")


@router.get("/worker/bookmarks", response_model=List[_schemas.WorkerBookmarkOut])
async def get_worker_bookmarks(user_id: str, db: Session = Depends(get_db)):
    try:
        return _service.list_worker_bookmarks(db, user_id)
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while fetching bookmarks")
