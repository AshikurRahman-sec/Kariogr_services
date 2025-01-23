from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import JWTError, jwt
import sqlalchemy.orm as _orm
import os

from models import auth_model


SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
   
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
   
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
    
    
def get_user_by_email(email: str, db: _orm.Session):
     # Retrieve a user by email from the database
    return db.query(auth_model.User).filter(auth_model.User.email == email).first()