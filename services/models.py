from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, TIMESTAMP, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base, create_database


class App(Base):
    __tablename__ = 'apps'
    __table_args__ = {"schema": "karigor"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    logo = Column(LargeBinary)  # Store the logo as binary data
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to Service
    service = relationship('Service', back_populates='apps')

class Service(Base):
    __tablename__ = 'services'
    __table_args__ = {"schema": "karigor"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(Integer, ForeignKey('karigor.apps.id', ondelete='CASCADE'))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    logo = Column(LargeBinary)  # Store the path to the logo image (file system or URL)
    image_path = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with Subservice table
    subservices = relationship('Subservice', back_populates='service')

    # Relationship with Apps table
    apps = relationship('App', back_populates='service')

class Subservice(Base):
    __tablename__ = 'subservices'
    __table_args__ = {"schema": "karigor"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey('karigor.services.id', ondelete='CASCADE'))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    logo = Column(LargeBinary)
    image_path = Column(String(255))  # Store the path to the image (file system or URL)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    service = relationship('Service', back_populates='subservices')

    details = relationship('SubserviceDetail', back_populates='subservice')


class SubserviceDetail(Base):
    __tablename__ = 'subservice_details'
    __table_args__ = {"schema": "karigor"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    subservice_id = Column(Integer, ForeignKey('karigor.subservices.id', ondelete='CASCADE'), nullable=False)
    category = Column(String(255), nullable=False)  # Example: "What We Offer", "Liability"
    detail = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to Subservice
    subservice = relationship('Subservice', back_populates='details')


