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
        payload_dict = request_data.body.dict()
        payload_dict["user_id"] = user["user_id"]
        response = requests.post(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/create-booking",
            json=payload_dict,
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


@router.post(
    "/make-payment",
    #response_model=_schemas.MakePaymentGatewayResponse,
    #tags=["Payment"]
)
async def make_payment_gateway(
    request_data: _schemas.MakePaymentGatewayRequest,
    user: dict = Depends(verify_token),
):
    try:
        # Inject user_id from token
        payload_dict = request_data.body.dict()
        payload_dict["user_id"] = user["user_id"]
        response = requests.post(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/make-payment",
            json=payload_dict,
        )

        if response.status_code in (200, 201):
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Payment created successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to create payment"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Booking service is unavailable")
        return build_response(
            data={},
            message="Booking service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"Unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/payment-confirm",
    response_model=_schemas.ConfirmBookingGatewayResponse,
    #tags=["Payment"]
)
async def confirm_order_gateway(
    request_data: _schemas.ConfirmBookingGatewayRequest,
    user: dict = Depends(verify_token),
):
    try:
        response = requests.put(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/payment-confirm",
            json=request_data.body.dict(),
        )

        if response.status_code in (200, 201):
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Booking confirmed successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to confirm booking"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Booking service is unavailable")
        return build_response(
            data={},
            message="Booking service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"Unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post("/apply-cupon", response_model=_schemas.CouponInfoGatewayResponse)
async def apply_coupon_gateway(
    request_data: _schemas.ApplyCouponGatewayRequest,
    user: dict = Depends(verify_token),
):
    try:
        response = requests.post(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/cupon/apply-cupon",
            json={
                "booking_id": request_data.body.booking_id,
                "user_id": user["user_id"],
                "coupon_code": request_data.body.coupon_code,
            },
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                message="Coupon applied successfully",
                code="200",
                request_id=request_data.header.requestId,
            )
        else:
            return build_response(
                data={},
                message=response.json().get("detail", "Failed to apply coupon"),
                code=str(response.status_code),
                request_id=request_data.header.requestId,
            )

    except requests.exceptions.ConnectionError:
        logging.error("Coupon microservice is unavailable")
        return build_response(
            data={},
            message="Coupon microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message="Unexpected error",
            code="500",
            request_id=request_data.header.requestId,
        )


@router.post("/booking-cupon", response_model=_schemas.CouponInfoGatewayResponse)
async def get_coupon_by_booking_gateway(
    request_data: _schemas.BookingRequestBody,
    user: dict = Depends(verify_token),
):
    try:
        booking_id = request_data.body.booking_id

        response = requests.get(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/api/booking-cupon/{booking_id}"
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                message="Coupon info retrieved successfully",
                code="200",
                request_id=request_data.header.requestId,
            )
        else:
            return build_response(
                data={},
                message=response.json().get("detail", "No coupon found for this booking"),
                code=str(response.status_code),
                request_id=request_data.header.requestId,
            )
    except requests.exceptions.ConnectionError:
        logging.error("Coupon microservice is unavailable")
        return build_response(
            data={},
            message="Coupon microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message="Unexpected error",
            code="500",
            request_id=request_data.header.requestId,
        )


@router.post("/cupons-list", response_model=_schemas.CouponListGatewayResponse)
async def list_all_coupons_gateway(
    request_data: _schemas.RequestHeader,  # dummy body just to get `header`
    #user: dict = Depends(verify_token),
):
    try:
        response = requests.get(f"{PAYMENT_AND_BOOKING_BASE_URL}/api/cupon/all-cupons")

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                message="Coupon list retrieved successfully",
                code="200",
                request_id=request_data.requestId,
            )
        else:
            return build_response(
                data={},
                message="Failed to fetch coupons",
                code=str(response.status_code),
                request_id=request_data.header.requestId,
            )
    except requests.exceptions.ConnectionError:
        logging.error("Coupon microservice is unavailable")
        return build_response(
            data={},
            message="Coupon microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message="Unexpected error",
            code="500",
            request_id=request_data.header.requestId,
        )
    
@router.post("/service-user", response_model= _schemas.OfferListGatewayResponse)
async def get_offers_by_service_user_gateway(
    request_data: _schemas.OfferGatewayRequest,
    user: dict = Depends(verify_token),
):
    try:
        service_id = request_data.body.service_id
        user_id = request_data.body.user_id

        response = requests.get(
            f"{PAYMENT_AND_BOOKING_BASE_URL}/service/{service_id}/user/{user_id}"
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                message="Offer(s) retrieved successfully",
                code="200",
                request_id=request_data.header.requestId,
            )
        else:
            return build_response(
                data={},
                message=response.json().get("detail", "No active offers found"),
                code=str(response.status_code),
                request_id=request_data.header.requestId,
            )

    except requests.exceptions.ConnectionError:
        logging.error("Offer microservice is unavailable")
        return build_response(
            data={},
            message="Offer microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message="Unexpected error",
            code="500",
            request_id=request_data.header.requestId,
        )