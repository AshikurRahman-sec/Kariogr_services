from sqlalchemy import (
    Column, String, Text, Boolean,
    ForeignKey, TIMESTAMP, Date, Numeric, Enum, Integer, func
)
from sqlalchemy.orm import relationship
import uuid
import database

# Role Table
class Role(database.Base):
    __tablename__ = 'roles'
    __table_args__ = {"schema": "karigor"}
    role_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_name = Column(String(100), unique=True, nullable=False)
    users = relationship("UserAuth", back_populates="role", cascade="all, delete-orphan")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

# Permission Table
class Permission(database.Base):
    __tablename__ = 'permissions'
    __table_args__ = {"schema": "karigor"}
    permission_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    permission_name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

# RolePermission Association Table
class RolePermission(database.Base):
    __tablename__ = 'role_permissions'
    __table_args__ = {"schema": "karigor"}
    role_id = Column(String(36), ForeignKey('karigor.roles.role_id', ondelete="CASCADE"), primary_key=True)
    permission_id = Column(String(36), ForeignKey('karigor.permissions.permission_id', ondelete="CASCADE"), primary_key=True)
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")

# UserAuth Table
class UserAuth(database.Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "karigor"}
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255))
    firebase_uid = Column(String(255), unique=True, index=True)
    role_id = Column(String(36), ForeignKey('karigor.roles.role_id'))
    is_verified = Column(Boolean , default=False)
    otp = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    role = relationship("Role", back_populates="users")

# Token Table
class Token(database.Base):
    __tablename__ = 'tokens'
    __table_args__ = {"schema": "karigor"}
    token_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('karigor.users.user_id', ondelete="CASCADE"), index=True)
    access_token = Column(String(512), index=True)
    refresh_token = Column(String(512), index=True)
    token_type = Column(String(50), default='bearer')
    scopes = Column(String(255))
    expires_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())




