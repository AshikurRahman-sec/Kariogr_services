from pydantic import BaseModel
from typing import Optional, List
from schemas.base_schemas import RequestHeader, ResponseHeader, ErrorResponse
from decimal import Decimal
from enum import Enum

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
    user_id: str
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