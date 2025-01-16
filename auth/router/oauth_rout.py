from fastapi import HTTPException, APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import logging


import services.custom_oauth_service as services
import schemas.oauth_schemas as _schemas
from models.oauth_model import Client, User, AuthorizationCode
from database import get_db


logging.basicConfig(level=logging.INFO)


router = APIRouter()

@router.post("/register")
async def register_client(request: Request, redirect_uri: str, db: Session = Depends(get_db)):

    return await services.register_client(redirect_uri=redirect_uri,  url=str(request.url), db=db)
    

@router.get("/authorize")
async def authorize_service(client_id: str, redirect_uri: str, response_type: str, state: str, db: Session = Depends(get_db)):

    return await services.authorize_service(client_id=client_id, redirect_uri=redirect_uri, response_type=response_type, state=state, db=db)
    

@router.post("/users" )
async def create_user(
    user: _schemas.UserCreate, 
    db: Session = Depends(services.get_db)):
    db_user = await services.get_user_by_email(email=user.email, db=db)

    if db_user:
        logging.info('User with that email already exists')
        raise HTTPException(
            status_code=200,
            detail="User with that email already exists")
    

    user = await services.create_user(user=user, db=db)

    return JSONResponse(status_code=201,content={"status_code": 201, "detail": "User Registered, Please verify email to activate account !"})

@router.post("/users/generate_otp", response_model=str)
async def send_otp_mail(userdata: _schemas.GenerateOtp, db: Session = Depends(services.get_db)):
    user = await services.get_user_by_email(email=userdata.email, db=db)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")

    # Generate and send OTP
    otp = services.generate_otp()
    services.send_otp(userdata.email, otp)

    # Store the OTP in the database
    user.otp = otp
    db.add(user)
    db.commit()

    return "OTP sent to your email"

@router.post("/users/verify_otp")
async def verify_otp(userdata: _schemas.VerifyOtp, db: Session = Depends(services.get_db)):
    user = await services.get_user_by_email(email=userdata.email, db=db )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.otp or user.otp != userdata.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Update user's is_verified field
    user.is_verified = True
    user.otp = None  # Clear the OTP
    db.add(user)
    db.commit()

    return "Email verified successfully"

@router.get("/users/profile")
async def get_user(email: str, db: Session = Depends(services.get_db)):
    return db.query(User).filter_by(email=email).first()

@router.post("/token" )
async def generate_token(
    #form_data: _security.OAuth2PasswordRequestForm = Depends(), 
    user_data: _schemas.GenerateUserToken, code:str,
    db: Session = Depends(services.get_db)):
    user = await services.authenticate_user(email=user_data.username, password=user_data.password, db=db)

    if user == "is_verified_false":
        logging.info('Email verification is pending. Please verify your email to proceed. ')
        raise HTTPException(
            status_code=403, detail="Email verification is pending. Please verify your email to proceed.")

    if not user:
        logging.info('Invalid Credentials')
        raise HTTPException(
            status_code=401, detail="Invalid Credentials")
    
    auth_code = db.query(AuthorizationCode).filter(AuthorizationCode.code == code, AuthorizationCode.user_id == user.id).first()
    if not auth_code or auth_code.expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired authorization code")
    
    logging.info('JWT Token Generated')
    return await services.create_token(user=user)