import sqlalchemy.orm as _orm
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4
import fastapi as _fastapi
import random, os
from firebase_admin import auth as firebase_auth
from dotenv import load_dotenv
import logging

from schemas.oauth_schemas import UserCreate, GenerateOtp, VerifyOtp
from schemas import auth_schemas as _schemas
from model import auth_model as _model
from kafka_producer import kafka_producer_service
from utilities import verify_password, get_password_hash, create_access_token, decode_token


logging.basicConfig(level=logging.INFO)

async def send_otp_mail(user: GenerateOtp, db: _orm.Session):

    user = db.query(_model.UserAuth).filter(_model.UserAuth.email == user.email).first()
    
    if not user:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise _fastapi.HTTPException(status_code=400, detail="User is already verified")
    # Generate and send OTP
    otp = str(random.randint(100000, 999999))
    
    message = {'email': user.email,
               'subject': 'Account Verification OTP Notification',
               'other': 'null',
               'body': f'Your OTP for account verification is: {otp} \n Please enter this OTP on the verification page to complete your account setup. \n If you did not request this OTP, please ignore this message.\n Thank you '
                }

    try:
        await kafka_producer_service.send_message("email_notification", message)
    except Exception as err:
        print(f"Failed to publish message: {err}")

    # Store the OTP in the database
    user.otp = otp
    db.add(user)
    db.commit()

    return "OTP sent to your email"


async def verify_otp(user_info: VerifyOtp, db: _orm.Session):

    user = db.query(_model.UserAuth).filter(_model.UserAuth.email == user_info.email, _model.UserAuth.otp == user_info.otp).first()
    
    if not user:
        return None
    
    # Update user's is_verified field
    user.is_verified = True
    user.otp = None  # Clear the OTP
    db.commit()
    return user

async def signup_user(db: _orm.Session, user: _schemas.UserAuthCreate):
    hashed_password = get_password_hash(user.password)
    db_user = _model.UserAuth(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

async def login_user(db: _orm.Session, user: _schemas.UserAuthLogin):
    db_user = db.query(_model.UserAuth).filter(_model.UserAuth.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        return None
    
    if not db_user.is_verified:
        email = GenerateOtp(email=db_user.email)
        await send_otp_mail(email, db)
        raise _fastapi.HTTPException(
            status_code=403, 
            detail="OTP not verified. A new OTP has been sent to your email."
        )
    return db_user

async def create_tokens(db: _orm.Session, user_id: str):
    access_token = create_access_token({"user_id": user_id}, expires_delta=timedelta(minutes=15))
    refresh_token = str(uuid4())
    expires_at = datetime.utcnow() + timedelta(days=7)
    db_token = _model.Token(access_token=access_token, refresh_token=refresh_token, expires_at=expires_at, user_id=user_id)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

async def verify_token(db: _orm.Session, token: str):
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    
async def firebase_login(db: _orm.Session, id_token: str):
    """Authenticate with Firebase and generate tokens."""
    # Verify Firebase token
    decoded_token = firebase_auth.verify_id_token(id_token)
    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")

    if not firebase_uid or not email:
        raise _fastapi.HTTPException(status_code=400, detail="Invalid Firebase token")

    # Check if user exists
    db_user = (
        db.query(_model.UserAuth).filter(_model.UserAuth.firebase_uid == firebase_uid).first()
    )

    # Create user if not found
    if not db_user:
        db_user = _model.UserAuth(
            firebase_uid=firebase_uid,
            email=email,
            is_verified=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    # Generate tokens
    return create_tokens(db_user.user_id)
