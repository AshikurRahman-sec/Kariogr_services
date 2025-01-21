from pydantic import BaseModel
from uuid import UUID

from schemas.base_schemas import RequestHeader, ResponseHeader

class ServiceId(BaseModel):
    service_id: UUID

class ServiceIdRequestBody(BaseModel): 
    meta: dict = {}
    header: RequestHeader
    body: ServiceId