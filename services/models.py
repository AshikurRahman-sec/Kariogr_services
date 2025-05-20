import uuid
import json
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP, Index, UniqueConstraint, Numeric, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

import database

class Service(database.Base):
    __tablename__ = 'services'
    __table_args__ = (
        Index('idx_service_parent_id', 'parent_id'),
        {"schema": "karigor"}
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String, ForeignKey('karigor.services.id', ondelete='SET NULL'), nullable=True)
    name = Column(String(255), nullable=False)
    level = Column(Integer, nullable=False)
    is_leaf = Column(Boolean, default=False, server_default='false', nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    parent = relationship('Service', remote_side=[id], back_populates='children')
    children = relationship('Service', back_populates='parent', cascade="all, delete-orphan")

    logo = relationship('ServiceLogo', back_populates='service', cascade="all, delete-orphan")
    description = relationship('ServiceDescription', back_populates='service', cascade="all, delete-orphan")

    descendants = relationship('ServiceHierarchy', foreign_keys='ServiceHierarchy.ancestor_id', back_populates='ancestor', cascade="all, delete-orphan")
    ancestors = relationship('ServiceHierarchy', foreign_keys='ServiceHierarchy.descendant_id', back_populates='descendant', cascade="all, delete-orphan")
    
    # Relationships
    booking_inputs = relationship("BookingInput", back_populates="service", cascade="all, delete-orphan")
    recommendations = relationship("ServiceRecommendation", back_populates="service", cascade="all, delete-orphan")
    preferred_services = relationship("ServicePreference", back_populates="service", cascade="all, delete-orphan")

class ServiceHierarchy(database.Base):
    __tablename__ = 'service_hierarchy'
    __table_args__ = (
        UniqueConstraint('ancestor_id', 'descendant_id', name='uq_service_hierarchy'),
        {"schema": "karigor"}
    )

    ancestor_id = Column(String, ForeignKey("karigor.services.id", ondelete="CASCADE"), primary_key=True)
    descendant_id = Column(String, ForeignKey("karigor.services.id", ondelete="CASCADE"), primary_key=True)
    depth = Column(Integer, nullable=False)

    ancestor = relationship('Service', foreign_keys=[ancestor_id], back_populates='descendants')
    descendant = relationship('Service', foreign_keys=[descendant_id], back_populates='ancestors')

class ServiceLogo(database.Base):
    __tablename__ = 'service_logos'
    __table_args__ = {"schema": "karigor"}

    service_id = Column(String, ForeignKey("karigor.services.id", ondelete="CASCADE"), primary_key=True)
    image_url = Column(String, nullable=True)  # URL for externally stored images
    image_name = Column(String, nullable=True) 
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    service = relationship('Service', back_populates='logo')

class ServiceDescription(database.Base):
    __tablename__ = 'service_descriptions'
    __table_args__ = {"schema": "karigor"}

    service_id = Column(String, ForeignKey("karigor.services.id", ondelete="CASCADE"), primary_key=True)
    language_code = Column(String(10), primary_key=True) # e.g., 'en', 'bn', 'fr'
    description = Column(Text, nullable=False)  # Store HTML data
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    service = relationship('Service', back_populates='description')

class BookingInput(database.Base):
    __tablename__ = "booking_inputs"
    __table_args__ = (
        UniqueConstraint("service_id", "field_name", name="uq_booking_input"),
        {"schema": "karigor"}
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    service_id = Column(String, ForeignKey("karigor.services.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String, nullable=False, comment="Field key sent to frontend")
    field_label = Column(String, nullable=True, comment="Human-readable label for UI")
    field_type = Column(String, nullable=True, comment="Type: text, number, select, datetime, etc.")
    options = Column(Text, nullable=True, comment="Serialized JSON for dropdown options")
    required = Column(Boolean, default=True, nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, onupdate=datetime.utcnow)

    # Relationship with Service (Back-Populated)
    service = relationship("Service", back_populates="booking_inputs")

    def set_options(self, options_list):
        """Store a list of options for select fields as JSON."""
        self.options = json.dumps(options_list)

    def get_options(self):
        """Retrieve the list of options from JSON."""
        return json.loads(self.options) if self.options else []
     
class ServicePreference(database.Base):
    __tablename__ = "user_service_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", "service_id", name="uq_user_service_preference"),
        {"schema": "karigor"}
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)  # Only store the user_id
    service_id = Column(String, ForeignKey("karigor.services.id", ondelete="CASCADE"), nullable=False)
    preference_weight = Column(Numeric(3, 2), nullable=True, comment="User's preference score for a service")

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)  # Automatically set to current timestamp
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow)  # Updated automatically when modified

    # Relationships
    service = relationship("Service", back_populates="preferred_services")

class ServiceRecommendation(database.Base):
    __tablename__ = "service_recommendations"
    __table_args__ = {"schema": "karigor"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)  # Only store the user_id
    service_id = Column(String, ForeignKey("karigor.services.id", ondelete="CASCADE"), index=True, nullable=False)
    score = Column(Numeric(3, 2), comment="Recommendation score")
    algorithm_version = Column(String(50), comment="Version of recommendation algorithm used")
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)  # Automatically set to current timestamp
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow)  # Updated automatically when modified

    # Relationships
    service = relationship("Service", back_populates="recommendations")

class ServiceToolRequirement(database.Base):
    __tablename__ = 'service_tool_requirements'
    __table_args__ = {"schema": "karigor"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = Column(String, ForeignKey('karigor.services.id', ondelete="CASCADE"), nullable=False, index=True)
    needs_tools = Column(Boolean, nullable=False, default=False)  # True if tools are required
    
   
   

