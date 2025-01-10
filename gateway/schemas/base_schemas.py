from pydantic import BaseModel



class RequestHeader(BaseModel):
    requestId: str
    requestClient: str
    requestVersion: str
    requestTimeoutInSeconds: int
    requestRetryCount: int
    requestType: str
    requestSource: str
    requestSourceService: str
    requestTime: str

class ResponseHeader(BaseModel):
    responseVersion: str
    hopCount: int
    traceId: str
    requestReceivedTime: str
    requestId: str
    responseTime: str
    responseMessage: str
    responseProcessingTimeInMs: int
    responseCode: str
