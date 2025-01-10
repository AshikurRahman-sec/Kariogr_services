from fastapi import HTTPException, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
import requests, os, jwt, uuid, datetime 
from jwt.exceptions import DecodeError
from sqlalchemy.orm import Session

from services import frontpage_service
from schemas.frontpage_schemas import *
from utils.response_builder import build_response
from database import get_db

router = APIRouter()
SERVICE_BASE_URL = os.environ.get("SERVICE_BASE_URL")

@router.post("/apps-services")
async def get_app_service_data(request: RequestHeader, db: Session = Depends(get_db)):
    
    data = await frontpage_service.get_app_service_data(db)

    response = build_response(
        data=data,
        request_id=request.requestId,
        message="Apps and services fetched successfully"
    )

    return response

@router.post("/services")
async def registeration(request: RequestHeader):

    try:
        service_data = requests.get(f"{SERVICE_BASE_URL}/api/apps-services")
        if service_data.json()["status_code"] == 200:
            response = build_response(
            data=service_data.json()["data"],
            request_id=request.requestId,
            message="Apps and services fetched successfully")
            
            return response
        else:
            raise HTTPException(status_code=service_data.json()["status_code"], detail=service_data.json()["detail"])
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Service service is unavailable")


@router.get("/images/{image_name}")
async def get_image(image_name: str):
    
   return  await frontpage_service.get_image(image_name)