from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
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
    
    client_profile = relationship("ClientProfile", uselist=False, back_populates="user")
    worker_profile = relationship("WorkerProfile", uselist=False, back_populates="user")

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
    
class WorkerProfile(database.Base):
    __tablename__ = "worker_profiles"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("karigor.users.id", ondelete="CASCADE"))
    bio = Column(Text)
    availability = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class Skill(database.Base):
    __tablename__ = "skills"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)  # e.g., 'Plumbing', 'Carpentry'
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class WorkerSkill(database.Base):
    __tablename__ = "worker_skills"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("karigor.worker_profiles.id", ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("karigor.skills.id", ondelete="CASCADE"))
    price = Column(Float)  # Price for the specific skill
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class ClientProfile(database.Base):
    __tablename__ = "client_profiles"
    __table_args__ = {"schema": "karigor"}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("karigor.users.id", ondelete="CASCADE"))
    preferences = Column(Text)  # Client's service preferences
    service_history = Column(Text)  # A record of the services hired by the client
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="client_profile")


