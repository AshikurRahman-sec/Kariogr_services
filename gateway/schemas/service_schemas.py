from pydantic import BaseModel
from uuid import UUID

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
    service_id: str
    needs_tools: bool

class ServiceToolRequirementGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict = {}
    body: ServiceToolRequirementOut