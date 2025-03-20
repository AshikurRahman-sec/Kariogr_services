from sqlalchemy import (
    Column, String, Text, Boolean,
    ForeignKey, TIMESTAMP, Date, Numeric, Enum, Integer, func, UniqueConstraint
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
    working_zones = relationship("WorkerZone", back_populates="worker", cascade="all, delete-orphan") 
    skill_zones = relationship("WorkerSkillZone", back_populates="worker", cascade="all, delete-orphan")

# Skill Table
class Skill(database.Base):
    __tablename__ = 'skills'
    __table_args__ = {"schema": "karigor"}
    skill_id = Column(String(36), primary_key=True, nullable=False)
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

    worker = relationship("WorkerProfile", back_populates="working_zones")
    skill_zones = relationship("WorkerSkillZone", back_populates="worker_zone", cascade="all, delete-orphan")

# WorkerSkillZone Association Table (NEW)
class WorkerSkillZone(database.Base):
    __tablename__ = 'worker_skill_zones'
    __table_args__ = {"schema": "karigor"}

    worker_skill_zone_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(36), ForeignKey('karigor.worker_profiles.worker_id', ondelete="CASCADE"), index=True)
    skill_id = Column(String(36), ForeignKey('karigor.skills.skill_id', ondelete="CASCADE"), index=True)
    worker_zone_id = Column(String(36), ForeignKey('karigor.worker_zones.worker_zone_id', ondelete="CASCADE"), index=True)
    
    service_charge = Column(Numeric(10, 2), nullable=False)  # Store charge amount
    charge_unit = Column(Enum('hourly', 'daily', 'per job', name="charge_unit_enum"), nullable=False)  # Define charge unit
    discount = Column(Numeric(10, 2), nullable=True, default=0)  # Store discount amount

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    worker = relationship("WorkerProfile", back_populates="skill_zones")
    skill = relationship("Skill")
    worker_zone = relationship("WorkerZone", back_populates="skill_zones")

# WorkerSkillComment Table
class WorkerSkillComment(database.Base):
    __tablename__ = 'worker_skill_comments'
    __table_args__ = {"schema": "karigor"}

    comment_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(36), ForeignKey('karigor.worker_profiles.worker_id', ondelete="CASCADE"), index=True)
    skill_id = Column(String(36), ForeignKey('karigor.skills.skill_id', ondelete="CASCADE"), index=True)
    user_id = Column(String(36), ForeignKey('karigor.user_profiles.profile_id', ondelete="CASCADE"), index=True)
    comment_text = Column(Text, nullable=False)
    parent_comment_id = Column(String(36), ForeignKey('karigor.worker_skill_comments.comment_id', ondelete="CASCADE"), nullable=True, index=True)
    depth = Column(Integer, default=0, comment="Limits reply depth")

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserProfile")  
    worker = relationship("WorkerProfile")  
    skill = relationship("Skill")
    parent_comment = relationship("WorkerSkillComment", remote_side=[comment_id], backref="replies")
    reactions = relationship("CommentReaction", back_populates="comment", cascade="all, delete-orphan")

# CommentReaction Table
class CommentReaction(database.Base):
    __tablename__ = 'comment_reactions'
    __table_args__ = (
        UniqueConstraint('comment_id', 'user_id', name='unique_comment_reaction'),
        {"schema": "karigor"}
    )

    reaction_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    comment_id = Column(String(36), ForeignKey('karigor.worker_skill_comments.comment_id', ondelete="CASCADE"), index=True)
    user_id = Column(String(36), ForeignKey('karigor.user_profiles.profile_id', ondelete="CASCADE"), index=True)
    reaction_type = Column(String(50), nullable=False, comment="Reaction type (e.g., like, love, laugh, etc.)")

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    comment = relationship("WorkerSkillComment", back_populates="reactions")
    user = relationship("UserProfile")

# WorkerSkillRating Table
class WorkerSkillRating(database.Base):
    __tablename__ = 'worker_skill_ratings'
    __table_args__ = (
        UniqueConstraint('worker_id', 'skill_id', 'user_id', name='unique_worker_skill_rating'),
        {"schema": "karigor"}
    )

    rating_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(36), ForeignKey('karigor.worker_profiles.worker_id', ondelete="CASCADE"), index=True)
    skill_id = Column(String(36), ForeignKey('karigor.skills.skill_id', ondelete="CASCADE"), index=True)
    user_id = Column(String(36), ForeignKey('karigor.user_profiles.profile_id', ondelete="CASCADE"), index=True)
    rating = Column(Numeric(3, 2), nullable=False, comment="Rating out of 5")
    review_text = Column(Text, nullable=True, comment="Optional review")

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    worker = relationship("WorkerProfile")
    skill = relationship("Skill")
    user = relationship("UserProfile")


