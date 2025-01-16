from fastapi import HTTPException, APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import logging


from schemas.oauth_schemas import UserCreate, GenerateOtp, VerifyOtp, GenerateUserToken
from database import get_db
from utils import get_user_by_email
import services.email_auth_service as _service

logging.basicConfig(level=logging.INFO)


router = APIRouter()

@router.post("/sign_up" ,  tags = ['Fastapi Auth'])
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db)):
    db_user = await get_user_by_email(email=user.email, db=db)

    if db_user:
        logging.info('User with that email already exists')
        raise HTTPException(
            status_code=200,
            detail="User with that email already exists")
    

    user = await _service.create_user(user=user, db=db)

    return JSONResponse(status_code=201,content={"status_code": 201, "detail": "User Registered, Please verify email to activate account !"})

@router.post("/users/generate_otp", response_model=str, tags=["Fastapi Auth"])
async def send_otp_mail(userdata: GenerateOtp, db: Session = Depends(get_db)):

    await _service.send_otp_mail(userdata, db)
    

@router.post("/users/verify_otp", tags=["Fastapi Auth"])
async def verify_otp(userdata: VerifyOtp, db: Session = Depends(get_db)):
    
    await _service.verify_otp(userdata, db)
    

@router.post("/token" ,tags = ['Fastapi Auth'])
async def generate_token(
    #form_data: _security.OAuth2PasswordRequestForm = Depends(), 
    user_data: GenerateUserToken, code:str,
    db: Session = Depends(get_db)):
    user = await _service.authenticate_user(email=user_data.username, password=user_data.password, db=db)

    if user == "is_verified_false":
        logging.info('Email verification is pending. Please verify your email to proceed. ')
        raise HTTPException(
            status_code=403, detail="Email verification is pending. Please verify your email to proceed.")

    if not user:
        logging.info('Invalid Credentials')
        raise HTTPException(
            status_code=401, detail="Invalid Credentials")
    
    logging.info('JWT Token Generated')
    return await _service.create_token(user_email=user.email)