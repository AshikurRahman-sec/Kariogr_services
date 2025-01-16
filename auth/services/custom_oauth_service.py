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

import database as _database
import models.oauth_model as _models
import schemas.oauth_schemas as _schemas
from kafka_producer import kafka_producer_service

# Load environment variables
JWT_SECRET = os.getenv("JWT_SECRET")


def get_db():
    # Dependency to get a database session
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    # Create a new user in the database
    try:
        valid = _email_check.validate_email(user.email)
        name = user.name
        email = valid.email
    except _email_check.EmailNotValidError:
        raise _fastapi.HTTPException(status_code=404, detail="Please enter a valid email")

    user_obj = _models.User(email=email, name=name, hashed_password=_hash.bcrypt.hash(user.password))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def authenticate_user(email: str, password: str, db: _orm.Session):
    # Authenticate a user
    user = await get_user_by_email(email=email, db=db)

    if not user:
        return False
    
    if not user.is_verified:
        return 'is_verified_false'
    
    if not user.verify_password(password):
        return False

    return user

async def create_token(user: _models.User):
    # Create a JWT token for authentication
    user_obj = _schemas.User.from_orm(user)
    user_dict = user_obj.model_dump()
    del user_dict["date_created"]
    token = jwt.encode(user_dict, JWT_SECRET, algorithm="HS256")
    return dict(access_token=token, token_type="bearer")

def generate_otp():
    # Generate a random OTP
    return str(random.randint(100000, 999999))


def send_otp(email, otp, channel):
    # Send an OTP email notification using Apache kafka
    
    message = {'email': email,
               'subject': 'Account Verification OTP Notification',
               'other': 'null',
               'body': f'Your OTP for account verification is: {otp} \n Please enter this OTP on the verification page to complete your account setup. \n If you did not request this OTP, please ignore this message.\n Thank you '
                }

    try:
        kafka_producer_service.send_message("email_notification", message)
    except Exception as err:
        print(f"Failed to publish message: {err}")

async def register_client(redirect_uri: str, url:str, db: _orm.Session):

    client_id = str(uuid.uuid4())
    client_secret = hashlib.sha256(client_id.encode()).hexdigest()
    client = _models.Client(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
    db.add(client)
    db.commit()
    return {"client_id": client_id, "client_secret": client_secret, "authorization_url":f"{url}/token", "access_token_url":f"{url}/token"}

async def authorize_service(client_id: str, redirect_uri: str, response_type: str, state: str, db: _orm.Session):

    client = db.query(_models.Client).filter(_models.Client.client_id == client_id).first()
    if not client or client.redirect_uri != redirect_uri:
        raise _fastapi.HTTPException(status_code=400, detail="Invalid client or redirect URI")
    if response_type != "code":
        raise _fastapi.HTTPException(status_code=400, detail="Invalid response type")

    code = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.add(_models.AuthorizationCode(code=code, expires=expires_at, client_id=client.id))
    db.commit()

    return {"redirect_uri": f"{redirect_uri}", "code":code, "state":state}

async def verify_access_token(token: str ):
    try:

        payload = jwt.decode(token, JWT_SECRET, algorithm="HS256")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise _fastapi.HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid token")