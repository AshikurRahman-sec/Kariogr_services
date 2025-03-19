from sqlalchemy import Column, String, Integer, Enum, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as pyEnum
from datetime import datetime
import json

import database

# Enum for Booking Type
class BookingType(pyEnum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    PER_JOB = "per job"

class Booking(database.Base):
    __tablename__ = "bookings"
    __table_args__ = {"schema": "karigor"}

    booking_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = Column(String(36), nullable=False)
    service_area = Column(String, nullable=False)
    home_address = Column(String, nullable=False)
    worker_duration = Column(Integer, comment="Duration in hours")
    booking_type = Column(Enum(BookingType, values_callable=lambda x: [e.value for e in x], name="booking_type_enum"))
    dates = Column(Text, nullable=False, comment="Serialized JSON list of dates")
    times = Column(Text, nullable=False, comment="Serialized JSON list of time slots")
    service_id = Column(String, nullable=False, comment="ID of the service from another service")
    status = Column(Enum('pending', 'worker_selected', 'confirmed', 'completed', 'cancelled', name='booking_status_enum'), default='pending')
    total_charge = Column(Numeric(10, 2), default=0)  # Total booking charge
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    workers = relationship("BookingWorker", back_populates="booking")
    payments = relationship("Payment", back_populates="booking")

    def set_dates(self, dates_list):
        """Store a list of dates as JSON."""
        self.dates = json.dumps(dates_list)

    def get_dates(self):
        """Retrieve the list of dates from JSON."""
        return json.loads(self.dates)

    def set_times(self, times_list):
        """Store a list of time slots as JSON."""
        self.times = json.dumps(times_list)

    def get_times(self):
        """Retrieve the list of time slots from JSON."""
        return json.loads(self.times)


class BookingWorker(database.Base):
    __tablename__ = "booking_workers"
    __table_args__ = {"schema": "karigor"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey('karigor.bookings.booking_id'), nullable=False)
    worker_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    booking = relationship("Booking", back_populates="workers")
    skills = relationship("BookingWorkerSkill", back_populates="booking_worker")
    addons = relationship("WorkerAddonService", back_populates="booking_worker")


class BookingWorkerSkill(database.Base):
    __tablename__ = "booking_worker_skills"
    __table_args__ = {"schema": "karigor"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_worker_id = Column(String(36), ForeignKey('karigor.booking_workers.id'), nullable=False)
    skill_id = Column(String(36), nullable=False)
    charge_amount = Column(Numeric(10, 2), nullable=False)
    charge_unit = Column(Enum('weekly', 'monthly', 'per job', name='charge_unit_enum'))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    booking_worker = relationship("BookingWorker", back_populates="skills")


class WorkerAddonService(database.Base):
    __tablename__ = "worker_addon_services"
    __table_args__ = {"schema": "karigor"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_worker_id = Column(String(36), ForeignKey('karigor.booking_workers.id'), nullable=False)
    addon_service_id = Column(String(36), nullable=False)  # Should reference an add-on service table
    quantity = Column(Integer, nullable=False, default=1)
    charge_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    booking_worker = relationship("BookingWorker", back_populates="addons")

class Payment(database.Base):
    __tablename__ = "payments"
    __table_args__ = {"schema": "karigor"}

    payment_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey('karigor.bookings.booking_id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum('pending', 'paid', 'failed', name='payment_status_enum'), default='pending')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    booking = relationship("Booking", back_populates="payments")
