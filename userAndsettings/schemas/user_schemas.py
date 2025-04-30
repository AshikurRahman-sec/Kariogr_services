from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# UserProfile Schemas
class UserProfileUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    date_of_birth: Optional[datetime]
    profile_picture_url: Optional[str]

class UserProfileOut(BaseModel):
    profile_id: str
    user_id: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    date_of_birth: Optional[datetime]
    profile_picture_url: Optional[str]

    class Config:
        orm_mode = True

# WorkerProfile Schemas
class WorkerProfileUpdate(BaseModel):
    hourly_rate: Optional[float]
    availability_status: Optional[str]
    bio: Optional[str]

class WorkerProfileOut(BaseModel):
    worker_id: str
    #user_id: str
    hourly_rate: Optional[float]
    availability_status: Optional[str]
    bio: Optional[str]

    class Config:
        orm_mode = True

class UnregisteredUserAddressCreate(BaseModel):
    mobile_id: str
    street_address: Optional[str] = None
    division: Optional[str] = None
    district: Optional[str] = None
    thana: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

class UnregisteredUserAddressOut(UnregisteredUserAddressCreate):
    address_id: str

class WorkerZoneOut(BaseModel):
    worker_zone_id: str
    worker_id: str
    division: str
    district: str
    thana: str
    road_number: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    class Config:
        orm_mode = True

# Skill Info
class SkillOut(BaseModel):
    skill_id: str
    skill_name: str
    category: Optional[str]
    description: Optional[str]
    service_charge: float
    charge_unit: str
    discount: float

    class Config:
        orm_mode = True

# Request Schema for Filtering Workers
class WorkerFilterRequest(BaseModel):
    skill_id: str
    district: str

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

class SearchWorkerDetails(BaseModel):
    data:List[WorkerWithSkillsAndZonesOut]
    page: int
    size: int
    total_services: int

    class Config:
        orm_mode = True

class WorkerDetailsOut(BaseModel):
    user: UserProfileOut
    worker_profile: WorkerProfileOut
    skills: List[SkillOut]
    working_zone: WorkerZoneOut

    class Config:
        orm_mode = True

# Request Schema
class WorkerByZoneRequest(BaseModel):
    worker_id: str
    district: str
    
# Response Schema
class PaginatedWorkerListResponse(BaseModel):
    data: List[WorkerDetailsOut]
    total_workers: int
    page: int
    size: int

    class Config:
        orm_mode = True

class CreateWorkerSkillRatingRequest(BaseModel):
    worker_id: str
    skill_id: str
    user_id: str
    rating: Decimal = Field(..., ge=0, le=5, decimal_places=2)
    review_text: Optional[str] = None

class WorkerSkillRatingResponse(BaseModel):
    rating_id: str
    worker_id: str
    skill_id: str
    user_id: str
    rating: Decimal
    review_text: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CreateWorkerSkillRatingResponse(BaseModel):
    rating: WorkerSkillRatingResponse
    average_rating: float
    total_ratings: int

    class Config:
        from_attributes = True

