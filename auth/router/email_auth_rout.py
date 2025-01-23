from fastapi import HTTPException, APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from datetime import datetime
import logging

from schemas import eamil_auth_schemas as _schemas
from schemas.oauth_schemas import GenerateOtp, VerifyOtp
from models import auth_model as _model
from database import get_db
import services.email_auth_service as _service

logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.post("/signup", response_model=_schemas.UserAuthOut, tags=["Email Auth"])
async def signup(user: _schemas.UserAuthCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(_model.UserAuth).filter(_model.UserAuth.email == user.email).first()
        if existing_user:
            logging.info('User with that email already exists')
            raise HTTPException(status_code=400, detail="Email already registered")
        return await _service.signup_user(db, user)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while signing up")
    
@router.post("/login", response_model=_schemas.TokenOut, tags=["Email Auth"])
async def login(user: _schemas.UserAuthLogin, db: Session = Depends(get_db)):
    try:
        db_user = await _service.login_user(db, user)
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return await _service.create_tokens(db, db_user.user_id)
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during login")

@router.post("/users/generate_otp", response_model=str, tags=["Email Auth"])
async def send_otp_mail(userdata: GenerateOtp, db: Session = Depends(get_db)):

    try:
        await _service.send_otp_mail(userdata, db)
        return {"message": "OTP sent successfully"}
    except Exception as exec:
        raise exec
    
@router.post("/users/verify_otp", tags=["Fastapi Auth"])
async def verify_otp(userdata: VerifyOtp, db: Session = Depends(get_db)):
    
    try:
        verified_otp = await _service.verify_otp(userdata, db)
        if not verified_otp:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        return {"message": "OTP verified successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while verifying OTP")
    
@router.put("/user/profile", response_model=_schemas.UserProfileOut)
async def update_user_profile(user_id: str, profile_data: _schemas.UserProfileUpdate, db: Session = Depends(get_db)):
    try:
        return await _service.update_user_profile(db, user_id, profile_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating user profile")

@router.put("/worker/profile", response_model=_schemas.WorkerProfileOut)
async def update_worker_profile(user_id: str, profile_data: _schemas.WorkerProfileUpdate, db: Session = Depends(get_db)):
    try:
        return await _service.update_worker_profile(db, user_id, profile_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating worker profile")

@router.post("/token/refresh", response_model=_schemas.TokenOut)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        result = await db.execute(select(_model.Token).where(_model.Token.refresh_token == refresh_token))
        db_token = result.scalars().first()
        if not db_token or db_token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        return await _service.create_tokens(db, db_token.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while refreshing token")

@router.post("/token/verify")
async def verify_token(token: str, db: Session = Depends(get_db)):
    try:
        user_id = await _service.verify_token(db, token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while verifying token")