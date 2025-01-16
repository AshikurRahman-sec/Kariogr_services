import sqlalchemy.orm as _orm
import passlib.hash as _hash
import jwt
import email_validator as _email_check
import fastapi as _fastapi
import fastapi.security as _security
import random
import json
import time
import os
import uuid
import hashlib
from datetime import datetime, timedelta
from jose import JWTError, jwt

from schemas.oauth_schemas import UserCreate, GenerateOtp, VerifyOtp
from models.oauth_model import User
from kafka_producer import kafka_producer_service


# Load environment variables
JWT_SECRET = os.getenv("JWT_SECRET")

async def create_user(user: UserCreate, db: _orm.Session):
    # Create a new user in the database
    try:
        valid = _email_check.validate_email(user.email)
        name = user.name
        email = valid.email
    except _email_check.EmailNotValidError:
        raise _fastapi.HTTPException(status_code=404, detail="Please enter a valid email")

    user_obj = User(email=email, name=name, hashed_password=_hash.bcrypt.hash(user.password))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def send_otp_mail(user: GenerateOtp, db: _orm.Session):

    user = db.query(User).filter(User.email == user.email).first()
    
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
        kafka_producer_service.send_message("email_notification", message)
    except Exception as err:
        print(f"Failed to publish message: {err}")

    # Store the OTP in the database
    user.otp = otp
    db.add(user)
    db.commit()

    return "OTP sent to your email"


async def verify_otp(user_info: VerifyOtp, db: _orm.Session):

    user = db.query(User).filter(User.email == user_info.email).first()

    if not user:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")

    if not user.otp or user.otp != user_info.otp:
        raise _fastapi.HTTPException(status_code=400, detail="Invalid OTP")
    # Update user's is_verified field
    user.is_verified = True
    user.otp = None  # Clear the OTP
    db.add(user)
    db.commit()

    return "Email verified successfully"

async def authenticate_user(email: str, password: str, db: _orm.Session):
    # Authenticate a user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return False
    
    if not user.is_verified:
        return 'is_verified_false'
    
    if not user.verify_password(password):
        return False

    return user

async def create_token(user_email:str):
    # Create a JWT token for authentication
    token = jwt.encode(user_email, JWT_SECRET, algorithm="HS256")
    return dict(access_token=token, token_type="bearer")