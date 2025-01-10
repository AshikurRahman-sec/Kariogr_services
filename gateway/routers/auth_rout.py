from fastapi import HTTPException, APIRouter
import fastapi as _fastapi
from fastapi.security import OAuth2PasswordBearer
import requests
import os
import jwt
from jwt.exceptions import DecodeError

from schemas.auth_schemas import *

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
JWT_SECRET = os.environ.get("JWT_SECRET")
AUTH_BASE_URL = os.environ.get("AUTH_BASE_URL")


# JWT token validation
async def jwt_validation(token: str = _fastapi.Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except DecodeError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")

# Authentication routes
@router.post("/login", tags=['Authentication Service'])
async def login(user_data: UserCredentials):
    try:
        response = requests.post(f"{AUTH_BASE_URL}/api/token", json={"username": user_data.username, "password": user_data.password})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Authentication service is unavailable")

@router.post("/register", tags=['Authentication Service'])
async def registeration(user_data:UserRegisteration):

    try:
        response = requests.post(f"{AUTH_BASE_URL}/api/users", json={"name":user_data.name,"email": user_data.email, "password": user_data.password})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Authentication service is unavailable")

@router.post("/generate_otp", tags=['Authentication Service'])
async def generate_otp(user_data:GenerateOtp):
    try:
        response = requests.post(f"{AUTH_BASE_URL}/api/users/generate_otp", json={"email":user_data.email})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Authentication service is unavailable")

@router.post("/verify_otp", tags=['Authentication Service'])
async def verify_otp(user_data:VerifyOtp):
    try:
        response = requests.post(f"{AUTH_BASE_URL}/api/users/verify_otp", json={"email":user_data.email ,"otp":user_data.otp})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Authentication service is unavailable")
    
@router.get("/view_profile", tags=['Authentication Service'])
async def view_profile(user_data:GenerateOtp, payload: dict = _fastapi.Depends(jwt_validation)):
    try:
        response = requests.get(f"{AUTH_BASE_URL}/api/users/profile?email={user_data.email}")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Authentication service is unavailable")
    

    