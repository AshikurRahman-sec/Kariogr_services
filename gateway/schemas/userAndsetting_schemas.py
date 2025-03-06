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
    header: ResponseHeader
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

# Worker Filter Request (For Gateway)
class WorkerFilterRequest(BaseModel):
    skill_id: str
    district: str

class WorkerFilterGatewayRequest(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: WorkerFilterRequest

# Worker Profile Schemas
class UserProfileOut(BaseModel):
    profile_id: str
    user_id: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    date_of_birth: Optional[str]
    profile_picture_url: Optional[str]

    class Config:
        orm_mode = True

class WorkerProfileOut(BaseModel):
    worker_id: str
    hourly_rate: Optional[float]
    availability_status: Optional[str]
    bio: Optional[str]

    class Config:
        orm_mode = True

class SkillOut(BaseModel):
    skill_id: str
    skill_name: str
    category: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True

class SkillWithZoneOut(BaseModel):
    skill: SkillOut
    worker_zone: WorkerZoneOut

    class Config:
        orm_mode = True

class WorkerWithSkillsAndZonesOut(BaseModel):
    user: UserProfileOut
    worker_profile: WorkerProfileOut
    skill_with_zone: SkillWithZoneOut

    class Config:
        orm_mode = True

# Gateway Response Schema
class WorkerFilterGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: List[WorkerWithSkillsAndZonesOut]