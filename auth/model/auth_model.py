from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Float,
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
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

# UserProfile Table
class UserProfile(database.Base):
    __tablename__ = 'user_profiles'
    __table_args__ = {"schema": "karigor"}
    profile_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('karigor.users.user_id', ondelete="CASCADE"), unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20), index=True)
    date_of_birth = Column(Date)
    profile_picture_url = Column(String(255))

    user = relationship("UserAuth", back_populates="profile")
    address = relationship("Address", back_populates="user", uselist=False, cascade="all, delete-orphan")
    #service_preferences = relationship("UserServicePreference", back_populates="user")
    worker_profile = relationship("WorkerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

# Address Table
class Address(database.Base):
    __tablename__ = 'addresses'
    __table_args__ = {"schema": "karigor"}
    address_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('karigor.user_profiles.profile_id', ondelete="CASCADE"), unique=True)
    street_address = Column(String(255))
    city = Column(String(100), index=True)
    state_province = Column(String(100))
    postal_code = Column(String(20), index=True)
    country = Column(String(100))
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))

    user = relationship("UserProfile", back_populates="address")

# WorkerProfile Table
class WorkerProfile(database.Base):
    __tablename__ = 'worker_profiles'
    __table_args__ = {"schema": "karigor"}
    worker_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('karigor.user_profiles.profile_id', ondelete="CASCADE"), unique=True)
    hourly_rate = Column(Numeric(10, 2))
    rating = Column(Numeric(3, 2))
    availability_status = Column(Enum('available', 'busy', 'away', name='availability_status'))
    experience_years = Column(Integer)
    bio = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    user = relationship("UserProfile", back_populates="worker_profile")
    skills = relationship("WorkerSkill", back_populates="worker", cascade="all, delete-orphan")
    certifications = relationship("WorkerCertification", back_populates="worker", cascade="all, delete-orphan")

# Skill Table
class Skill(database.Base):
    __tablename__ = 'skills'
    __table_args__ = {"schema": "karigor"}
    skill_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    skill_name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100), index=True)
    description = Column(Text)
    workers = relationship("WorkerSkill", back_populates="skill", cascade="all, delete-orphan")

# WorkerSkill Association Table
class WorkerSkill(database.Base):
    __tablename__ = 'worker_skills'
    __table_args__ = {"schema": "karigor"}
    worker_id = Column(String(36), ForeignKey('karigor.worker_profiles.worker_id', ondelete="CASCADE"), primary_key=True)
    skill_id = Column(String(36), ForeignKey('karigor.skills.skill_id', ondelete="CASCADE"), primary_key=True)
    proficiency_level = Column(Enum('beginner', 'intermediate', 'expert', name='proficiency_level'))
    years_of_experience = Column(Integer)
    
    worker = relationship("WorkerProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="workers")

# Certification Table
class Certification(database.Base):
    __tablename__ = 'certifications'
    __table_args__ = {"schema": "karigor"}
    certification_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255))
    description = Column(Text)

# WorkerCertification Association Table
class WorkerCertification(database.Base):
    __tablename__ = 'worker_certifications'
    __table_args__ = {"schema": "karigor"}
    worker_id = Column(String(36), ForeignKey('karigor.worker_profiles.worker_id', ondelete="CASCADE"), primary_key=True)
    certification_id = Column(String(36), ForeignKey('karigor.certifications.certification_id', ondelete="CASCADE"), primary_key=True)
    issue_date = Column(Date)
    expiration_date = Column(Date)
    
    worker = relationship("WorkerProfile", back_populates="certifications")
    certification = relationship("Certification")

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

# class Service(database.Base):
#     __tablename__ = 'services'
#     service_id = Column(Integer, primary_key=True)
#     name = Column(String(255), unique=True, nullable=False)
#     category = Column(String(100), index=True)
#     description = Column(Text)
#     avg_hourly_rate = Column(Numeric(10, 2))
    
#     preferences = relationship("UserServicePreference", back_populates="service")
#     recommendations = relationship("ServiceRecommendation", back_populates="service")

# class UserServicePreference(database.Base):
#     __tablename__ = 'user_service_preferences'
#     user_id = Column(Integer, ForeignKey('user_profiles.profile_id'), primary_key=True)
#     service_id = Column(Integer, ForeignKey('services.service_id'), primary_key=True)
#     preference_weight = Column(Numeric(3, 2))
    
#     user = relationship("UserProfile", back_populates="service_preferences")
#     service = relationship("Service", back_populates="preferences")

# class ServiceRecommendation(database.Base):
#     __tablename__ = 'service_recommendations'
#     recommendation_id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
#     service_id = Column(Integer, ForeignKey('services.service_id'), index=True)
#     score = Column(Numeric(3, 2))
#     algorithm_version = Column(String(50))
#     created_at = Column(TIMESTAMP, server_default=func.now())
    
#     user = relationship("UserAuth")
#     service = relationship("Service", back_populates="recommendations")



