from sqlalchemy import (
    Column, String, Text, Boolean,
    ForeignKey, TIMESTAMP, Date, Numeric, Enum, Integer, func
)
from sqlalchemy.orm import relationship
import uuid
import database


# UserProfile Table
class UserProfile(database.Base):
    __tablename__ = 'user_profiles'
    __table_args__ = {"schema": "karigor"}
    profile_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20), index=True)
    date_of_birth = Column(Date)
    profile_picture_url = Column(String(255))

    address = relationship("Address", back_populates="user", uselist=False, cascade="all, delete-orphan")
    worker_profile = relationship("WorkerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

# Address Table
class Address(database.Base):
    __tablename__ = 'addresses'
    __table_args__ = {"schema": "karigor"}

    address_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('karigor.user_profiles.profile_id', ondelete="CASCADE"), unique=True)
    street_address = Column(String(255))
    division = Column(String(100), index=True)
    district = Column(String(100), index=True)
    thana = Column(String(100), index=True)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

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

class UnregisteredUserAddress(database.Base):
    __tablename__ = 'unregistered_user_addresses'
    __table_args__ = {"schema": "karigor"}

    address_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mobile_id = Column(String(255), nullable=False, index=True, comment="Unique mobile device identifier")
    street_address = Column(String(255))
    division = Column(String(100), index=True)
    district = Column(String(100), index=True)
    thana = Column(String(100), index=True)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

# WorkerZone Table (New Table for Worker Locations)
class WorkerZone(database.Base):
    __tablename__ = 'worker_zones'
    __table_args__ = {"schema": "karigor"}

    worker_zone_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(36), ForeignKey('karigor.worker_profiles.worker_id', ondelete="CASCADE"), index=True)
    division = Column(String(100), index=True)
    district = Column(String(100), index=True)
    thana = Column(String(100), index=True)
    road_number = Column(String(50), nullable=True)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)  # Soft delete

    worker = relationship("WorkerProfile", back_populates="working_zones")
