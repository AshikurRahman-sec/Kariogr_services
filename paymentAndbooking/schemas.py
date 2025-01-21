from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
from typing import Any
import json

class BookingType(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class BookingBase(BaseModel):
    service_area: str = Field(..., example="Mirpur")
    home_address: str = Field(..., example="123 Main St")
    worker_duration: Optional[int] = Field(None, example=2, description="Duration in hours")
    worker_count: Optional[int] = Field(None, example=3)
    booking_type: BookingType
    service_id: str = Field(..., example="service-12345")
    dates: List[str] = Field(..., example=["18 week of 2024"])
    times: List[str] = Field(..., example=["11pm-1am"])

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: str
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
