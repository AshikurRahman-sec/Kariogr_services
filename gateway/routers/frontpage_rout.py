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


@router.get("/images/{image_name}")
async def get_image(image_name: str):
    
   return  await frontpage_service.get_image(image_name)