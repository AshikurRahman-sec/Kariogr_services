from fastapi import APIRouter, Depends
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
    response_model=_schemas.BookingResponse
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
