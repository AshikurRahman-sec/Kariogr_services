from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List, Dict, Union

from schemas.base_schemas import RequestHeader, ResponseHeader

class ServiceId(BaseModel):
    service_id: UUID

class ServiceIdRequestBody(BaseModel): 
    meta: dict = {}
    header: RequestHeader
    body: ServiceId

class ServiceRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: dict

class ServiceToolRequirementRequestBody(BaseModel):
    service_id: str

class ServiceToolRequirementGatewayRequest(BaseModel):
    header: RequestHeader
    meta: dict = {}
    body: ServiceToolRequirementRequestBody

class ServiceToolRequirementOut(BaseModel):
    tools: Optional[List[Dict[str, Union[bool, float]]]] = None  

class ServiceToolRequirementGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: ServiceToolRequirementOut