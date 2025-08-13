from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime

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
    service_charge: float
    charge_unit: str
    discount: float

    class Config:
        orm_mode = True

class SkillWithZoneOut(BaseModel):
    skill: SkillOut
    worker_zone: WorkerZoneOut

    class Config:
        orm_mode = True

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
        orm_mode = True

# Gateway Response Schema
class WorkerFilterGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: List[WorkerWithSkillsAndZonesOut]

class WorkerByZoneRequestBody(BaseModel):
    worker_id: str
    district: str

class WorkerByZoneGatewayRequest(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: WorkerByZoneRequestBody

class WorkerDetailsOut(BaseModel):
    user: UserProfileOut
    worker_profile: WorkerProfileOut
    skills: List[SkillOut]
    working_zone: WorkerZoneOut

    class Config:
        orm_mode = True

class WorkerByZoneGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: List[WorkerDetailsOut]

class CreateWorkerSkillRatingBody(BaseModel):
    worker_id: str
    skill_id: str
    user_id: str
    rating: Decimal = Field(..., ge=0, le=5, decimal_places=2)
    review_text: Optional[str] = None

class CreateWorkerSkillRatingRequest(BaseModel):
    header: RequestHeader
    meta: Dict = {}
    body: CreateWorkerSkillRatingBody

# Response body
class WorkerSkillRatingResponse(BaseModel):
    rating_id: str
    worker_id: str
    skill_id: str
    user_id: str
    rating: Decimal
    review_text: Optional[str]
    created_at: datetime
    updated_at: datetime

class CreateWorkerSkillRatingResponse(BaseModel):
    header: ResponseHeader
    meta: Dict = {}
    body: Dict[str, Optional[Dict]]

class WorkerDetailsRequestBody(BaseModel):
    worker_id: str
    skill_id: str

class WorkerDetailsGatewayRequest(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: WorkerDetailsRequestBody

class WorkerDetailsGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: WorkerWithSkillsAndZonesOut

class CommentGatewayBody(BaseModel):
    worker_id: str
    skill_id: str
    #user_id: str
    comment_text: str
    parent_comment_id: Optional[str] = None


class CommentGatewayRequest(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: CommentGatewayBody


class CommentReactionSchema(BaseModel):
    reaction_type: str


class CommentResponseBase(BaseModel):
    comment_text: str
    parent_comment_id: Optional[str] = None


class CommentGatewayResponseBody(CommentResponseBase):
    comment_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    depth: int
    reactions: List[CommentReactionSchema] = []
    replies: List["CommentGatewayResponseBody"] = []

    class Config:
        orm_mode = True

class CommentGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: CommentGatewayResponseBody

class CommentListGatewayBody(BaseModel):
    worker_id: str
    skill_id: str
    limit: int = 10
    offset: int = 0


class CommentListGatewayRequest(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: CommentListGatewayBody


class CommentListGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: List[CommentGatewayResponseBody]

class CommentReplyListGatewayBody(BaseModel):
    parent_comment_id: str
    limit: int = 10
    offset: int = 0


class CommentReplyListGatewayRequest(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: CommentReplyListGatewayBody

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

class CommentReactionGatewayRequest(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: CreateReaction  # from your existing service schemas


class CommentReactionGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: ReactionResponse  # from your existing service schemas

CommentGatewayResponseBody.update_forward_refs()

class WorkerBookmarkCreate(BaseModel):
    user_id: str
    worker_id: str

class WorkerBookmarkRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: WorkerBookmarkCreate

class WorkerBookmarkOut(WorkerBookmarkCreate):
    bookmark_id: str
    created_at: datetime

class WorkerBookmarkResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: List[WorkerBookmarkOut]

