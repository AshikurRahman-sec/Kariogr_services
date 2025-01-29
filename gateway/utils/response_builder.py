import uuid
from datetime import datetime

def build_response(data=None, request_id=None, message="OK", code="200"):
    request_received_time = datetime.utcnow()
    response_time = datetime.utcnow()
    processing_time_ms = int((response_time - request_received_time).total_seconds() * 1000)

    return {
        "header": {
            "responseVersion": "1.0",
            "hopCount": 2,
            "traceId": str(uuid.uuid4()),
            "requestReceivedTime": request_received_time.isoformat() + "Z",
            "requestId": request_id or str(uuid.uuid4()),
            "responseTime": response_time.isoformat() + "Z",
            "responseMessage": message,
            "responseProcessingTimeInMs": processing_time_ms,
            "responseCode": code,
        },
        "meta": {},
        "body":  data if data else {}
        
    }
