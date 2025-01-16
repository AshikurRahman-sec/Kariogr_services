import uuid
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Service(Base):
    __tablename__ = 'services'
    __table_args__ = (
        Index('idx_service_parent_id', 'parent_id'),
        {"schema": "karigor"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('karigor.services.id', ondelete='SET NULL'), nullable=True)
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

class ServiceHierarchy(Base):
    __tablename__ = 'service_hierarchy'
    __table_args__ = (
        UniqueConstraint('ancestor_id', 'descendant_id', name='uq_service_hierarchy'),
        {"schema": "karigor"}
    )

    ancestor_id = Column(UUID(as_uuid=True), ForeignKey('karigor.services.id', ondelete='CASCADE'), primary_key=True)
    descendant_id = Column(UUID(as_uuid=True), ForeignKey('karigor.services.id', ondelete='CASCADE'), primary_key=True)
    depth = Column(Integer, nullable=False)

    ancestor = relationship('Service', foreign_keys=[ancestor_id], back_populates='descendants')
    descendant = relationship('Service', foreign_keys=[descendant_id], back_populates='ancestors')

class ServiceLogo(Base):
    __tablename__ = 'service_logos'
    __table_args__ = {"schema": "karigor"}

    service_id = Column(UUID(as_uuid=True), ForeignKey('karigor.services.id', ondelete='CASCADE'), primary_key=True)
    image_url = Column(Text, nullable=True)  # URL for externally stored images
    logo_data = Column(Text, nullable=True)  # Base64 or binary for database-stored logos
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    service = relationship('Service', back_populates='logo')

class ServiceDescription(Base):
    __tablename__ = 'service_descriptions'
    __table_args__ = {"schema": "karigor"}

    service_id = Column(UUID(as_uuid=True), ForeignKey('karigor.services.id', ondelete='CASCADE'), primary_key=True)
    description = Column(Text, nullable=False)  # Store HTML data
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    service = relationship('Service', back_populates='description')
