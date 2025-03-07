from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.encoders import jsonable_encoder
from typing import Union
import requests
import logging
import os

import schemas.userAndsetting_schemas as _schemas
from utils.response_builder import build_response  # Ensure this function is available
from dependencies import verify_token

USER_SETTINGS_BASE_URL = os.environ.get("USER_SETTINGS_BASE_URL")

router = APIRouter()

@router.post(
    "/create/unregister_user_address",
    response_model=Union[_schemas.AddressResponse, _schemas.ErrorResponse],
)
async def create_address_gateway(request_data: _schemas.AddressRequestBody):
    """
    Gateway API to forward the `create_address` request to the Address microservice.
    """
    try:
        address_data = jsonable_encoder(request_data.body)

        response = requests.post(f"{USER_SETTINGS_BASE_URL}/api/create/unregister_user_address", json=address_data)

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Address created successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to create address"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Address microservice is unavailable")
        return build_response(
            data={},
            message="Address microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )


@router.post(
    "/worker-zones",
    response_model=Union[_schemas.WorkerZoneResponse,  _schemas.ErrorResponse]
)
async def get_worker_zones_gateway(
    request_data: _schemas.WorkerZoneRequestBody,
    user: dict = Depends(verify_token),
):
    """
    Gateway API that forwards the `get_worker_zones_by_skill` request to the Worker microservice.
    """
    try:
        service_id = request_data.body.service_id 

        response = requests.get(
            f"{USER_SETTINGS_BASE_URL}/api/worker_zones/{service_id}"
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Worker zones retrieved successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch worker zones"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Worker microservice is unavailable")
        return build_response(
            data={},
            message="Worker microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/workers/filter",
    response_model=Union[_schemas.WorkerFilterGatewayResponse, _schemas.ErrorResponse]
)
async def get_workers_by_skill_and_district_gateway(
    request_data: _schemas.WorkerFilterGatewayRequest,
    limit: int = Query(10, ge=1),  # Default limit: 10, min: 1
    offset: int = Query(0, ge=0),  # Default offset: 0, min: 0
    user: dict = Depends(verify_token),  # Auth validation
):
    """
    Gateway API that forwards the `get_workers_by_skill_and_district` request to the Worker microservice.
    Supports pagination using limit and offset.
    """
    try:
        # Forward request to the worker microservice
        response = requests.post(
            f"{USER_SETTINGS_BASE_URL}/api/workers/filter",
            json={
                "skill_id": request_data.body.skill_id,
                "district": request_data.body.district,
            },
            params={"limit": limit, "offset": offset},  # Pass limit & offset as query parameters
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data["data"],
                request_id=request_data.header.requestId,
                message="Workers retrieved successfully",
                code="200",
                meta={  # Include pagination metadata
                    "page": response_data["page"],
                    "size": response_data["size"],
                    "total_services": response_data["total_services"]
                },
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch workers"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Worker microservice is unavailable")
        return build_response(
            data={},
            message="Worker microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )



@router.post(
    "/workers/by-zone",
    response_model=Union[_schemas.WorkerByZoneGatewayResponse, _schemas.ErrorResponse]
)
async def get_workers_by_zone_gateway(
    request_data: _schemas.WorkerByZoneGatewayRequest,
    page: int = Query(0, ge=0),   # Default page: 0, minimum: 0
    size: int = Query(10, ge=1),  # Default size: 10, minimum: 1
    user: dict = Depends(verify_token),  # Auth validation
):
    """
    Gateway API that forwards the `get_workers_by_zone` request to the Worker microservice.
    Supports pagination using `page` and `size` query parameters.
    """
    try:
        # Forward request to the Worker microservice
        response = requests.post(
            f"{USER_SETTINGS_BASE_URL}/api/workers/by-zone",
            json={
                "worker_id": request_data.body.worker_id,
                "district": request_data.body.district
            },
            params={"page": page, "size": size},  # Pass pagination params
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data["data"],
                request_id=request_data.header.requestId,
                message="Workers retrieved successfully",
                code="200",
                meta={
                    "page": response_data["page"],
                    "size": response_data["size"],
                    "total_workers": response_data["total_workers"]
                },
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch workers"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Worker microservice is unavailable")
        return build_response(
            data={},
            message="Worker microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )
