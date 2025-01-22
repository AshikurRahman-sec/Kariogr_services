from sqlalchemy import Column, String, Integer, Enum, DateTime, Text
import uuid
from enum import Enum as pyEnum
from datetime import datetime
import json

import database

# Enum for Booking Type
class BookingType(pyEnum):
    WEEKLY = "one"
    MONTHLY = "two"

class Booking(database.Base):
    __tablename__ = "bookings"
    __table_args__ = {"schema": "karigor"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    service_area = Column(String, nullable=False)
    home_address = Column(String, nullable=False)
    worker_duration = Column(Integer, comment="Duration in hours")
    worker_count = Column(Integer)
    booking_type = Column(Enum(BookingType))
    dates = Column(Text, nullable=False, comment="Serialized JSON list of dates, e.g., ['18 week of 2024']")
    times = Column(Text, nullable=False, comment="Serialized JSON list of time slots, e.g., ['11pm-1am']")
    service_id = Column(String, nullable=False, comment="ID of the service from another service")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    
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
