import datetime as _dt
from sqlalchemy import Column,Integer, String, Text, Boolean, DateTime, ForeignKey
import passlib.hash as _hash
from datetime import datetime

import database 


class User(database.Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    #name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    is_verified = Column(Boolean , default=False)
    otp = Column(Integer)
    hashed_password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)

class Client(database.Base):
    __tablename__ = "clients"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, unique=True, index=True)
    client_secret = Column(String)
    redirect_uri = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuthorizationCode(database.Base):
    __tablename__ = "authorization_codes"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    expires = Column(DateTime)
    client_id = Column(Integer, ForeignKey("karigor.clients.id", ondelete="CASCADE"))
    scopes = Column(Text)  # comma-separated scopes
    state = Column(String)  # added for CSRF protection
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Token(database.Base):
    __tablename__ = "tokens"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, unique=True)
    refresh_token = Column(String, unique=True)
    token_type = Column(String)
    expires = Column(DateTime)
    user_id = Column(Integer, ForeignKey("karigor.users.id", ondelete="CASCADE"))
    scopes = Column(Text)  # comma-separated scopes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Role(database.Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserRole(database.Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("karigor.users.id", ondelete="CASCADE"))
    role_id = Column(Integer, ForeignKey("karigor.roles.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Permission(database.Base):
    __tablename__ = "permissions"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RolePermission(database.Base):
    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("karigor.roles.id", ondelete="CASCADE"))
    permission_id = Column(Integer, ForeignKey("karigor.permissions.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
