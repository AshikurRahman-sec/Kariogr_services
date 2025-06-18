from pydantic import BaseModel, Field
from typing import Optional, List
from schemas.base_schemas import RequestHeader, ResponseHeader, ErrorResponse
from enum import Enum
from datetime import datetime

class BookingType(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONETIME = "onetime"

class BookingStatus(str, Enum):
    Pending = 'pending'
    WORKER_SELECTED = 'worker_selected'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class ChargeUnit(str, Enum):
    HOURLY = 'hourly'
    DAILY = 'daily'
    PERJOB = 'per job'

class BookingId(BaseModel):
    booking_id: str

class BookingRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: BookingId

class BookingBase(BaseModel):
    service_area: str
    home_address: str
    worker_duration: Optional[int] = None
    worker_count: Optional[int] = None
    booking_type: BookingType
    service_id: str
    #user_id: str
    dates: List[str]
    times: List[str]

class BookingResponse(BookingBase):
    booking_id: str
    user_id: str
    status: BookingStatus
    created_at: str
    updated_at: Optional[str]

class BookingCreateRequest(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: BookingBase

class BookingCreateResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: BookingResponse


class WorkerInfo(BaseModel):
    worker_id: str
    skill_id: str
    charge_amount: float
    discount: float
    charge_unit: ChargeUnit

class WorkerSelection(BaseModel):
    booking_id: str
    workers: List[WorkerInfo]
    addons: Optional[List[WorkerInfo]] = []

class WorkerSelectionRequest(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: WorkerSelection

class WorkerSelectionResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: dict  # Can be adjusted based on actual response structure

class BookingId(BaseModel):
    booking_id: str

class BookingRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: BookingId

class AddToBagBody(BaseModel):
    service_id: str
    quantity: int = Field(default=1, ge=1)
    user_id: Optional[str] = None
    unregistered_address_id: Optional[str] = None

class RemoveFromBagBody(BaseModel):
    bag_id: str

class AddToBagGatewayRequest(BaseModel):
    header: RequestHeader
    meta: dict = {}
    body: AddToBagBody

class RemoveFromBagGatewayRequest(BaseModel):
    header: RequestHeader
    meta: dict = {}
    body: RemoveFromBagBody

class BagItemGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: dict  # or you can define BagItemBodyResponse schema separately if you want stronger typing

class GenericGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: dict

class BagListBody(BaseModel):
    user_id: Optional[str] = None
    unregistered_address_id: Optional[str] = None

class BagListGatewayRequest(BaseModel):
    header: RequestHeader
    meta: dict = {}
    body: BagListBody

class BagListGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: list[dict]

class PaymentMethod(str, Enum):
    CARD = "card"
    MOBILE_BANKING = "mobile_banking"
    CASH_ON_DELIVERY = "cash_on_delivery"

# Request body
class CreatePaymentBody(BaseModel):
    booking_id: str
    #user_id: str
    amount: float
    method: PaymentMethod
    coupon_code: Optional[str] = None
    offer_id: Optional[str] = None
    transaction_id: Optional[str] = None

# Gateway request format
class MakePaymentGatewayRequest(BaseModel):
    header: RequestHeader
    meta: dict = {}
    body: CreatePaymentBody

# Payment response
class PaymentResponseBody(BaseModel):
    id: str
    booking_id: str
    user_id: str
    amount: float
    discount_price: Optional[float]
    final_price: float
    method: str
    status: str
    transaction_id: Optional[str]
    created_at: datetime

# Gateway response format
class MakePaymentGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: PaymentResponseBody

class ConfirmBookingBody(BaseModel):
    booking_id: str

class ConfirmBookingGatewayRequest(BaseModel):
    header: RequestHeader
    meta: dict = {}
    body: ConfirmBookingBody

class ConfirmBookingResponseBody(BaseModel):
    message: str

class ConfirmBookingGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: ConfirmBookingResponseBody

class ApplyCouponBody(BaseModel):
    booking_id: str
    coupon_code: str

class CouponType(str, Enum):
    percentage = "percentage"
    amount = "amount"

class ApplyCouponGatewayRequest(BaseModel):
    header: RequestHeader
    meta: dict = {}
    body: ApplyCouponBody

class CouponInfoBody(BaseModel):
    coupon_code: str
    discount_applied: float
    applied_at: datetime

class CouponInfoGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: CouponInfoBody

class CouponListItem(BaseModel):
    id: str
    code: str
    discount_type: CouponType
    discount_value: float
    max_usage: int
    used_count: int
    expiry_date: datetime
    is_active: bool
    created_at: datetime

class CouponListGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: list[CouponListItem]

class OfferRequestBody(BaseModel):
    service_id: str
    user_id: str

class OfferGatewayRequest(BaseModel):
    header: RequestHeader
    meta: dict = {}
    body: OfferRequestBody

class OfferItem(BaseModel):
    offer_id: str
    user_id: str
    service_id: str
    image_url: Optional[str]
    status: str
    title: Optional[str]
    description: Optional[str]
    discount_type: Optional[CouponType]
    discount_value: Optional[float]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class OfferListGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: OfferItem