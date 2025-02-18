from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

from schemas.base_schemas import RequestHeader, ResponseHeader, ErrorResponse


class UnregisteredUserAddressCreate(BaseModel):
    mobile_id: str
    street_address: Optional[str] = None
    division: Optional[str] = None
    district: Optional[str] = None
    thana: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

class AddressRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: UnregisteredUserAddressCreate

class UnregisteredUserAddressOut(UnregisteredUserAddressCreate):
    address_id: str

class AddressResponse(BaseModel):
    header: "ResponseHeader"
    meta: dict = {}
    body: List[UnregisteredUserAddressOut]

class ServiceId(BaseModel):
    service_id: str

class WorkerZoneRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: ServiceId

class WorkerZoneOut(BaseModel):
    worker_zone_id: str
    worker_id: str
    division: str
    district: str
    thana: str
    road_number: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

class WorkerZoneResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: List[WorkerZoneOut]