from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class SingleServiceRequestBody(BaseModel):
    id:int
    type:int

class SingleServiceResponseBody(BaseModel):
    id:int
    type:int

class BookingInputBase(BaseModel):
    service_id: str
    field_name: str = Field(..., description="Field key sent to frontend")
    field_label: Optional[str] = Field(None, description="Human-readable label for UI")
    field_type: Optional[str] = Field(None, description="Type: text, number, select, datetime, etc.")
    options: Optional[List[str]] = Field(None, description="List of options for dropdown fields")
    required: bool = True

class BookingInputOut(BookingInputBase):
    id: str
    class Config:
        from_attributes = True


class ServiceChildOut(BaseModel):
    id: str
    parent_id: Optional[str]
    image_url: Optional[str] = None  # Add image URL

    class Config:
        from_attributes = True

class ServiceRelativesOut(BaseModel):
    parent_id: Optional[str] = None
    children: List[ServiceChildOut] = []

class ServiceChildOut(BaseModel):
    id: str
    name: str
    is_leaf: bool
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class SecondLevelServiceOut(BaseModel):
    id: str
    name: str
    is_leaf: bool
    children: List[ServiceChildOut] = []

class ServiceHierarchyOut(BaseModel):
    services: List[SecondLevelServiceOut]

class ServiceToolRequirementResponse(BaseModel):
    tools: Optional[List[Dict[str, bool]]] = None 

    class Config:
        orm_mode = True
    