from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# UserProfile Schemas
class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    profile_picture_url: Optional[str] = None

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
    hourly_rate: Optional[Decimal] = None
    availability_status: Optional[str] = None
    bio: Optional[str] = None

class WorkerProfileOut(BaseModel):
    worker_id: str
    #user_id: str
    hourly_rate: Optional[Decimal] = None
    availability_status: Optional[str] = None
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
class SkillCreate(BaseModel):
    skill_name: str
    category: Optional[str] = None
    description: Optional[str] = None

class SkillSimpleOut(BaseModel):
    skill_id: str
    skill_name: str
    category: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True

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
    user_id: str

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
    bookmarked : bool

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
        from_attributes = True

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
        from_attributes = True


CommentResponse.model_rebuild()

class WorkerBookmarkCreate(BaseModel):
    user_id: str   # This should be the profile_id from UserProfile
    worker_id: str

class WorkerBookmarkOut(BaseModel):
    bookmark_id: str
    user_id: str
    worker_id: str
    created_at: datetime

    class Config:
        from_attributes = True

from typing import Optional, List, Literal

# ... (rest of imports)

# Worker Portfolio Setup Schemas
class WorkerSkillZoneCreate(BaseModel):
    skill_id: str
    skill_name: str
    service_charge: Decimal
    charge_unit: Literal['hourly', 'daily', 'per job']
    discount: Optional[Decimal] = 0

class WorkerZoneCreate(BaseModel):
    division: str
    district: str
    thana: str
    road_number: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    skills: List[WorkerSkillZoneCreate]

class WorkerPortfolioCreate(BaseModel):
    user_id: str  # profile_id of the user
    hourly_rate: Optional[Decimal] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    working_zones: List[WorkerZoneCreate]

class WorkerPortfolioOut(BaseModel):
    worker_id: str
    message: str