from fastapi import HTTPException, APIRouter, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from uuid import UUID
import logging

from database import get_db
import service as services
import schemas as _schemas
# from models import Client, User, AuthorizationCode

logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.get("/root-services/")
def get_root_services(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size")
):
    """
    API to get paginated root services with second-level hierarchy data.
    """
    try:
        offset = (page - 1) * size
        data = services.get_root_services(db, offset, size)
        return {
            "page": page,
            "size": size,
            "total_services": len(data),
            "data": data
        }
    except HTTPException as exc:
        # Raise the exception to be handled by the custom HTTP exception handler
        raise exc
    except Exception as e:
        # Catch unexpected exceptions
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.get("/second-level-services/{root_service_id}")
def get_second_level_hierarchy(
    root_service_id: UUID,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
):
    """
    API endpoint to fetch paginated second-level hierarchy services for a specific root service.
    """
    
    try:
        offset = (page - 1) * size
        result = services.get_second_level_hierarchy(db, root_service_id, offset, size)

        return {
            "root_service_id": root_service_id,
            "page": page,
            "size": size,
            "total_services": result["total_count"],
            "data": result["data"],
        }

    except HTTPException as exc:
        raise exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.get("/service/{service_id}/hierarchy/")
def get_descendant_hierarchy(
    service_id: UUID,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
):
    """
    API endpoint to fetch paginated first-level descendants of a service,
    including up to 5 second-level descendants for each first-level descendant.
    """
    try:
        offset = (page - 1) * size
        result = services.get_descendant_hierarchy(db, service_id, offset, size)

        return {
            "service_id": service_id,
            "page": page,
            "size": size,
            "total_first_level_services": result["total_count"],
            "data": result["data"],
        }

    except HTTPException as exc:
        raise exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.get("/service/{service_id}/details/")
def get_service_details(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    """
    API endpoint to fetch details of a specific service by its ID.
    """
    try:
        # Call the service function to get service details
        service_details = services.get_service_details(db, service_id)

        if not service_details:
            raise HTTPException(
                status_code=404, detail=f"Service with ID {service_id} not found."
            )

        return service_details

    except HTTPException as exc:
        raise exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/special-services/")
def get_special_services(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
):
    """
    API endpoint to fetch paginated leaf-node services.
    """
    try:
        offset = (page - 1) * size
        result = services.get_special_services(db, offset, size)

        return {
            "page": page,
            "size": size,
            "total_leaf_services": result["total_count"],
            "data": result["data"],
        }

    except HTTPException as exc:
        raise exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.get("/search-services/")
def get_search_services(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
):
    """
    API endpoint to fetch paginated leaf-node services.
    """
    try:
        offset = (page - 1) * size
        result = services.get_search_services(db, offset, size)

        return {
            "page": page,
            "size": size,
            "total_search_services": result["total_count"],
            "data": result["data"],
        }

    except HTTPException as exc:
        raise exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.get("/booking_inputs/{service_id}", response_model=List[_schemas.BookingInputOut])
async def get_booking_inputs_by_service(service_id: str, db: Session = Depends(get_db)):
    try:
        booking_inputs = await services.get_booking_inputs_by_service(db, service_id)
        if not booking_inputs:
            raise HTTPException(status_code=404, detail="No booking inputs found for this service")
        return booking_inputs
    except HTTPException as exc:
        raise exc
    except Exception as e:
        logging.error(f"Error fetching booking inputs: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching booking inputs")
    
@router.get("/{service_id}/relatives", response_model=_schemas.ServiceRelativesOut)
async def get_service_relatives(
    service_id: str,
    limit: int = Query(10, ge=1, le=100),  # Pagination limit (1-100)
    offset: int = Query(0, ge=0),  # Offset for pagination
    db: Session = Depends(get_db)
):
    try:
        relatives = await services.get_service_relatives(db, service_id, limit, offset)
        if not relatives:
            raise HTTPException(status_code=404, detail="Service not found")
        return relatives
    except HTTPException as exc:
        raise exc
    except Exception as e:
        logging.error(f"Error fetching service relatives: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching service relatives")
    
@router.get("/second-level", response_model=_schemas.ServiceHierarchyOut)
async def get_all_second_level_services(
    limit: int = Query(10, ge=1, le=100),  # Pagination limit
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    try:
        second_level_services = await services.get_all_second_level_services(db, limit, offset)
        return {"services": second_level_services}
    except HTTPException as exc:
        raise exc
    except Exception as e:
        logging.error(f"Error fetching 2nd-level services: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching services")

