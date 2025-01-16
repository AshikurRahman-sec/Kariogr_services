from pydantic import BaseModel


class SingleServiceRequestBody(BaseModel):
    id:int
    type:int

class SingleServiceResponseBody(BaseModel):
    id:int
    type:int