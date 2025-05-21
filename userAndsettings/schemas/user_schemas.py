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
        from_attributes = True

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
        from_attributes = True

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
        from_attributes = True

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
        from_attributes = True

# Request Schema for Filtering Workers
class WorkerFilterRequest(BaseModel):
    skill_id: str
    district: str

class SkillWithZoneOut(BaseModel):
    skill: SkillOut
    worker_zone: WorkerZoneOut

    class Config:
        from_attributes = True

class RatingOut(BaseModel):
    average: float | None
    count: int

class WorkerWithSkillsAndZonesOut(BaseModel):
    user: UserProfileOut
    worker_profile: WorkerProfileOut
    skill_with_zone: SkillWithZoneOut 
    rating: RatingOut

    class Config:
        from_attributes = True

class SearchWorkerDetails(BaseModel):
    data:List[WorkerWithSkillsAndZonesOut]
    page: int
    size: int
    total_services: int

    class Config:
        from_attributes = True

class WorkerDetailsOut(BaseModel):
    user: UserProfileOut
    worker_profile: WorkerProfileOut
    skills: List[SkillOut]
    working_zone: WorkerZoneOut

    class Config:
        from_attributes = True

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
        from_attributes = True

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

class CommentReactionSchema(BaseModel):
    reaction_type: str

class CommentBase(BaseModel):
    comment_text: str
    parent_comment_id: Optional[str] = None

class CreateComment(CommentBase):
    worker_id: str
    skill_id: str
    user_id: str
    parent_comment_id: Optional[str] = None

class CommentResponse(CommentBase):
    comment_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    depth: int
    reactions: List[CommentReactionSchema] = []
    replies: List["CommentResponse"] = []

    class Config:
        orm_mode = True

class CreateReaction(BaseModel):
    comment_id: str
    reaction_type: str = Field(..., example="like")
    user_id: str

class ReactionResponse(BaseModel):
    reaction_id: str
    comment_id: str
    user_id: str
    reaction_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True