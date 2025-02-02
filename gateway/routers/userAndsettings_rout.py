from fastapi import APIRouter, HTTPException, Depends
from typing import Union
import requests
import logging
import os

import schemas.userAndsetting_schemas as _schemas
from utils.response_builder import build_response  # Ensure this function is available
from dependencies import verify_token

USER_SETTINGS_BASE_URL = os.environ.get("AUTH_BASE_URL")

router = APIRouter()

@router.post(
    "/addresses",
    tags=["Addresses"],
    response_model=Union[_schemas.AddressResponse, _schemas.ErrorResponse],
)
async def create_address_gateway(request_data: _schemas.AddressRequestBody):
    """
    Gateway API to forward the `create_address` request to the Address microservice.
    """
    try:
        address_data = request_data.body.dict()

        response = requests.post(f"{USER_SETTINGS_BASE_URL}/api/addresses", json=address_data)

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
    tags=["Worker Zones"],
    response_model=_schemas.WorkerZoneResponse
)
async def get_worker_zones_gateway(
    request_data: _schemas.WorkerZoneRequestBody,
    user: dict = Depends(verify_token),
):
    """
    Gateway API that forwards the `get_worker_zones_by_skill` request to the Worker microservice.
    """
    try:
        skill_id = request_data.body.skill_id  

        response = requests.get(
            f"{USER_SETTINGS_BASE_URL}/api/worker_zones/{skill_id}"
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
