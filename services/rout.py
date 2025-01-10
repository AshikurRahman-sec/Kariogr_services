from fastapi import HTTPException, APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import pika
import logging

from database import get_db
import service as services
# import schemas as _schemas
# from models import Client, User, AuthorizationCode

logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.get("/apps-services")
async def get_app_service_data(db: Session = Depends(get_db)):
    
    try:
        data = await services.get_app_service_data(db)
        return JSONResponse(status_code=200,content={"status_code": 200, "data": data})
    except:
        return JSONResponse(status_code=400,content={"status_code": 400, "detail": "Invalid Request"})