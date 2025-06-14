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

    # Try to get user by email or phone
    query = db.query(_model.UserAuth)
    if user.email:
        existing_user = query.filter(_model.UserAuth.email == user.email).first()
    else:
        existing_user = query.filter(_model.UserAuth.phone == user.phone).first()

    # If user doesn't exist, create it
    if not existing_user:
        new_user = _model.UserAuth(
            email=user.email,
            phone=user.phone,
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user_to_update = new_user
    else:
        user_to_update = existing_user

    # Generate and send OTP
    otp = random.randint(100000, 999999)
    expiry_time = datetime.utcnow() + timedelta(minutes=5)  # OTP expires in 5 minutes

    user_to_update.otp = otp
    user_to_update.otp_expiry = expiry_time
    db.add(user_to_update)
    db.commit()
    
    message = {
        'email': user.email,
        'subject': 'Account Verification OTP Notification',
        'other': 'null',
        'body': f'Your OTP for account verification is: {otp} \n This OTP will expire in 5 minutes.\n Please enter this OTP on the verification page to complete your account setup.\n If you did not request this OTP, please ignore this message.\n Thank you.'
    }

    try:
        await kafka_producer_service.send_message("email_verification", message)
    except Exception as err:
        print(f"Failed to publish message: {err}")

    return "OTP sent to your email"

async def request_password_reset(email: str, db: _orm.Session):
    user = db.query(_model.UserAuth).filter(_model.UserAuth.email == email).first()
    
    if not user:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")
    
    # Generate reset token
    reset_otp = str(random.randint(100000, 999999))
    expiry_time = datetime.utcnow() + timedelta(minutes=15)
    
    # Store token in DB
    user.reset_otp = reset_otp
    user.reset_otp_expiry = expiry_time
    db.add(user)
    db.commit()
    
    
    message = {
    'email': user.email,
    'subject': 'Password Reset Request',
    'other': 'null',
    'body': f"""
    Dear User,

    You have requested to reset your password. Your One-Time Password (OTP) is:

    {reset_otp}

    This OTP is valid for 15 minutes. If you did not request this, please ignore this email.

    Regards,  
    Your Application Team
    """
    }
    
    await kafka_producer_service.send_message("password_reset", message)

async def reset_password(otp: str, new_password: str, db: _orm.Session):
    user = db.query(_model.UserAuth).filter(_model.UserAuth.reset_otp == otp, _model.UserAuth.reset_otp_expiry > datetime.utcnow()).first()
    
    if not user:
        raise _fastapi.HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Check if the token is expired
    if datetime.datetime.utcnow() > user.reset_token_expiry:
        raise _fastapi.HTTPException(status_code=400, detail="Reset token has expired")
    
    # Hash and update the new password
    user.password = get_password_hash(new_password)
    
    # Invalidate the used reset token
    user.reset_token = None
    user.reset_token_expiry = None
    
    db.add(user)
    db.commit()  


async def verify_otp(user_info: VerifyOtp, db: _orm.Session):
    user = db.query(_model.UserAuth).filter(
        _model.UserAuth.email == user_info.email,
        _model.UserAuth.otp == user_info.otp
    ).first()

    if not user:
        raise _fastapi.HTTPException(status_code=400, detail="Invalid OTP or email")

    # Check if OTP is expired
    if user.otp_expiry and user.otp_expiry < datetime.utcnow():
        raise _fastapi.HTTPException(status_code=400, detail="OTP has expired")

    # Update user's is_verified field
    user.is_verified = True
    user.otp = None  # Clear the OTP
    user.otp_expiry = None  # Clear OTP expiry time
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
    return await create_tokens(db, db_user.user_id)
