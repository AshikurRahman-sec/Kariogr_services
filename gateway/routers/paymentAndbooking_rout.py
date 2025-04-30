from fastapi import APIRouter, Depends
from typing import Union
import requests
import logging
import os

import schemas.paymentAndbooking_schemas as _schemas
from dependencies import verify_token
from utils.response_builder import build_response

PAYMENT_AND_BOOKING_BASE_URL = os.environ.get("PAYMENT_AND_BOOKING_BASE_URL")

router = APIRouter()

@router.post(
    "/bookings",
    response_model=_schemas.BookingCreateResponse
)
async def get_booking_gateway(
    request_data: _schemas.BookingRequestBody,
    user: dict = Depends(verify_token),
):
    """
    Gateway API that forwards the `get_booking` request to the Booking microservice.
    """
    try:
        booking_id = request_data.body.booking_id  

        response = requests.get(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/bookings/{booking_id}"
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Booking retrieved successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch booking"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Booking microservice is unavailable")
        return build_response(
            data={},
            message="Booking microservice is unavailable",
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
    "/create-booking",
    response_model=Union[_schemas.BookingCreateResponse, _schemas.ErrorResponse]
)
async def create_booking_gateway(
    request_data: _schemas.BookingCreateRequest,
    user: dict = Depends(verify_token),
):
    """
    Gateway API that forwards the `create_booking` request to the Booking microservice.
    """
    try:
        booking_payload = request_data.body

        response = requests.post(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/create-booking",
            json=booking_payload.dict(),
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Booking created successfully",
                code="201",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to create booking"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Booking microservice is unavailable")
        return build_response(
            data={},
            message="Booking microservice is unavailable",
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
    "/select-workers",
    response_model=_schemas.WorkerSelectionResponse,
)
async def select_workers_gateway(
    request_data: _schemas.WorkerSelectionRequest,
    user: dict = Depends(verify_token),
):
    """
    Gateway API that forwards the `select_workers_for_booking` request 
    to the Booking microservice.
    """
    try:
        response = requests.post(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/select-workers",
            json=request_data.body.dict(),
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Workers selected successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to select workers"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Booking microservice is unavailable")
        return build_response(
                    data={},
                    message="Booking microservice is unavailable",
                    code="503",
                    request_id=request_data.header.requestId,
                )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
                        data={},
                        message=f"An unexpected error occurred: {str(e)}",
                        code="503",
                        request_id=request_data.header.requestId,
                    )
    
@router.post(
    "/bookings/summary",
    #tags=["Bookings"],
)
async def booking_summary_gateway(
    request_data: _schemas.BookingRequestBody,
    user: dict = Depends(verify_token),
):
    """
    Gateway API that forwards the `booking_summary` request 
    to the Booking microservice.
    """
    try:
        booking_id = request_data.body.booking_id
        response = requests.get(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/bookings/{booking_id}/summary"
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Booking summary retrieved successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to retrieve booking summary"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Booking microservice is unavailable")
        return build_response(
            data={},
            message="Booking microservice is unavailable",
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
    "/bag/add",
    response_model=_schemas.BagItemGatewayResponse,
    #tags=["gateway-bag"]
)
async def add_to_bag_gateway(
    request_data: _schemas.AddToBagGatewayRequest,
    #user: dict = Depends(verify_token),
):
    try:
        response = requests.post(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/bag/add",
            json=request_data.body.dict()
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Item added to bag successfully",
                code="200"
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to add item to bag"),
                code=str(response.status_code)
            )

    except requests.exceptions.ConnectionError:
        return build_response(
            data={},
            message="Bag service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="503",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/bag/remove",
    response_model=_schemas.GenericGatewayResponse,
    #tags=["gateway-bag"]
)
async def remove_from_bag_gateway(
    request_data: _schemas.RemoveFromBagGatewayRequest,
    #user: dict = Depends(verify_token),
):
    try:
        response = requests.post(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/bag/remove",
            json=request_data.body.dict()
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Item removed from bag",
                code="200"
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to remove item from bag"),
                code=str(response.status_code)
            )

    except requests.exceptions.ConnectionError:
        return build_response(
            data={},
            message="Bag service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="503",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/bag/bag-list",
    response_model=_schemas.BagListGatewayResponse,
    #tags=["gateway-bag"]
)
async def get_bag_list_gateway(
    request_data: _schemas.BagListGatewayRequest,
    #user: dict = Depends(verify_token),
):
    try:
        params = {}
        if request_data.body.user_id:
            params["user_id"] = request_data.body.user_id
        if request_data.body.unregistered_address_id:
            params["unregistered_address_id"] = request_data.body.unregistered_address_id

        response = requests.get(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/bag/bag-list",
            params=params
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Bag list fetched successfully",
                code="200"
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch bag list"),
                code=str(response.status_code)
            )

    except requests.exceptions.ConnectionError:
        return build_response(
            data={},
            message="Bag service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="503",
            request_id=request_data.header.requestId,
        )
