from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime
from typing import Any
import json

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


class BookingBase(BaseModel):
    service_area: str = Field(..., example="Mirpur")
    home_address: str = Field(..., example="123 Main St")
    worker_duration: Optional[int] = Field(None, example=2, description="Duration in hours")
    worker_count: Optional[int] = Field(None, example=3)
    booking_type: BookingType
    service_id: str = Field(..., example="service-12345")
    user_id: str = Field(..., example="user-12345")
    dates: List[str] = Field(..., example=["18 week of 2024"])
    times: List[str] = Field(..., example=["11pm-1am"])

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    booking_id: str
    user_id: str
    status: BookingStatus
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True 

    @classmethod
    def from_orm(cls, obj):
        """
        Custom method to transform an ORM object into a BookingResponse instance.
        """
        obj_dict = {key: getattr(obj, key, None) for key in obj.__dict__ if not key.startswith('_')}
        
        # Convert datetime fields to ISO format strings
        if isinstance(obj_dict.get("created_at"), datetime):
            obj_dict["created_at"] = obj_dict["created_at"].isoformat()
        if isinstance(obj_dict.get("updated_at"), datetime):
            obj_dict["updated_at"] = obj_dict["updated_at"].isoformat()

        # Deserialize JSON strings to lists for dates and times
        if isinstance(obj_dict.get("dates"), str):
            obj_dict["dates"] = json.loads(obj_dict["dates"])
        if isinstance(obj_dict.get("times"), str):
            obj_dict["times"] = json.loads(obj_dict["times"])

        # Validate and return the response model
        return cls(**obj_dict)

class WorkerInfo(BaseModel):
    worker_id: str
    skill_id: str
    charge_amount: float
    discount:float
    charge_unit: ChargeUnit

class WorkerSelection(BaseModel):
    booking_id: str
    workers: List[WorkerInfo]  # List of worker IDs
    addons: Optional[List[WorkerInfo]] = []  # Worker ID -> List of add-on service IDs

class AddToBagRequest(BaseModel):
    service_id: str
    quantity: int = Field(default=1, ge=1)
    user_id: Optional[str] = None
    unregistered_address_id: Optional[str] = None

class RemoveFromBagRequest(BaseModel):
    bag_id: str

class BagItemResponse(BaseModel):
    bag_id: str
    service_id: str
    service_name: Optional[str] = None
    user_id: Optional[str]
    unregistered_address_id: Optional[str]
    quantity: int
    added_at: datetime

    class Config:
        orm_mode = True