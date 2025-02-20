from fastapi import HTTPException, APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from datetime import datetime
import logging
from firebase_admin import credentials, initialize_app
import os

from schemas import auth_schemas as _schemas
from schemas.oauth_schemas import GenerateOtp, VerifyOtp
from model import auth_model as _model
from database import get_db
import services.auth_service as _service

logging.basicConfig(level=logging.INFO)


# Rebuild the Firebase credentials dictionary
firebase_credentials = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
}

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_credentials)
initialize_app(cred)

router = APIRouter()


@router.post("/signup", response_model=_schemas.UserAuthOut, tags=["Auth"])
async def signup(user: _schemas.UserAuthCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(_model.UserAuth).filter(_model.UserAuth.email == user.email).first()
        if existing_user:
            logging.info('User with that email already exists')
            raise HTTPException(status_code=400, detail="Email already registered")
        return await _service.signup_user(db, user)
    except HTTPException as exc:
        raise exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while signing up")
    
@router.post("/login", response_model=_schemas.TokenOut, tags=["Auth"])
async def login(user: _schemas.UserAuthLogin, db: Session = Depends(get_db)):
    db_user = await _service.login_user(db, user)
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

@router.post("/users/generate_otp", response_model=dict, tags=["Auth"])
async def send_otp_mail(userdata: GenerateOtp, db: Session = Depends(get_db)):
    try:
        await _service.send_otp_mail(userdata, db)
        return {"message": "OTP sent successfully"}
    except HTTPException as exec:
        raise exec
    except Exception:
        raise HTTPException(status_code="500", detail="An error occurred while generating OTP")
    
@router.post("/users/verify_otp", tags=["Auth"])
async def verify_otp(userdata: VerifyOtp, db: Session = Depends(get_db)):
    try:
        verified_otp = await _service.verify_otp(userdata, db)
        if not verified_otp:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        return {"message": "OTP verified successfully"}
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while verifying OTP")
     
@router.post("/forgot-password", tags=["Auth"])
async def forgot_password(email: _schemas.RequestEmail, db: Session = Depends(get_db)):
    try:
        await _service.request_password_reset(email, db)
        return {"message": "reset otp sent successfully"}
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while verifying OTP")
    
@router.post("/reset-password/",response_model=_schemas.TokenOut, tags=["Auth"])
async def reset_password(request_data: _schemas.ResetPassword, db: Session = Depends(get_db)):
    try:
        await _service.reset_password(request_data.otp, request_data.new_password, db)
        return {"message": "password reset successfully"}
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while verifying OTP")
    
@router.post("/token/refresh",response_model=_schemas.TokenOut, tags=["Auth"])
async def refresh_token(request: _schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        refresh_token = request.refresh_token  # Extract from request body
        result = db.execute(select(_model.Token).where(_model.Token.refresh_token == refresh_token))
        db_token = result.scalars().first()
        
        if not db_token or db_token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        return await _service.create_tokens(db, db_token.user_id)
    except HTTPException as e:
        # Return the HTTP exception raised in the service
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while refreshing token")

@router.post("/token/verify", tags=["Auth"])
async def verify_token(authorization: str = Header(None), db: Session = Depends(get_db)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid or missing token")

        token = authorization.split(" ")[-1].strip()  # Extract the token from "Bearer <token>"
        user_id = await _service.verify_token(db, token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return {"user_id": user_id}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while verifying token")
    
@router.post("/auth/firebase", response_model=_schemas.TokenResponse, tags=["Firebase Auth"])
async def firebase_auth(data: _schemas.FirebaseAuthRequest, db: Session = Depends(get_db)):
    """Authenticate using Firebase and return tokens."""
    try:
        return await _service.firebase_login(db, data.id_token)
    except HTTPException as exc:
        raise exc  # Propagate HTTPExceptions with appropriate status codes
    except Exception as e:
        # Log the error if needed
        raise HTTPException(status_code=500, detail="An unexpected error occurred during Firebase authentication")