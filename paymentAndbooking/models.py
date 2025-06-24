from sqlalchemy import Column, String, Integer, Enum, DateTime, Text, Numeric, ForeignKey, func, TIMESTAMP, Boolean, JSON
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
    ONETIME = "onetime"

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
    charge_unit = Column(Enum('hourly', 'daily', 'per job', name='charge_unit_enum'))
    tools_required = Column(Boolean, nullable=False, default=False)
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
    charge_unit = Column(Enum('hourly', 'daily', 'per job', name='charge_unit_enum'))
    tools_required = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    booking_worker = relationship("BookingWorker", back_populates="addons")

class PaymentStatus(pyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# Enum for Payment Method
class PaymentMethod(pyEnum):
    CARD = "card"
    MOBILE_BANKING = "mobile_banking"
    CASH_ON_DELIVERY = "cash_on_delivery"

class Payment(database.Base):
    __tablename__ = "payments"
    __table_args__ = {"schema": "karigor"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    booking_id = Column(String, ForeignKey("karigor.bookings.booking_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, nullable=False, comment="User ID from userandsettings service")
    amount = Column(Numeric(10, 2), nullable=False, comment="Total amount paid")
    discount_price = Column(Numeric(10, 2), nullable=True, comment="Discount applied")
    final_price = Column(Numeric(10, 2), nullable=False, comment="Final amount after discount")
    method = Column(Enum(PaymentMethod, values_callable=lambda x: [e.value for e in x], name="payment_method_enum"), 
                    nullable=False)
    status = Column(Enum(PaymentStatus, values_callable=lambda x: [e.value for e in x], name="payment_status_enum"), 
                    default=PaymentStatus.PENDING, nullable=False)
    transaction_id = Column(String, unique=True, nullable=True, comment="Transaction ID from payment gateway")
    #offer_id = Column(String, ForeignKey("karigor.offer_services.offer_id"), nullable=True, comment="Offer applied")
    coupon_usage_id = Column(String, ForeignKey("karigor.coupon_usage.id"), nullable=True, comment="Applied coupon usage")

    notes = Column(String(255), nullable=True, comment="Optional field for any notes (e.g., refund reason)")
    gateway_response = Column(JSON, nullable=True, comment="Raw response from payment gateway")
    
    coupon_usage = relationship("CouponUsage", backref="payment")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    booking = relationship("Booking", back_populates="payments")


class CouponType(pyEnum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"

class Coupon(database.Base):
    __tablename__ = "coupons"
    __table_args__ = {"schema": "karigor"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False, comment="Coupon Code")
    discount_type = Column(Enum(CouponType, values_callable=lambda x: [e.value for e in x], name="coupon_type_enum"))
    discount_value = Column(Numeric(10, 2), nullable=False, comment="Discount amount or percentage")
    max_usage = Column(Integer, nullable=False, default=1, comment="Max number of times a coupon can be used")
    used_count = Column(Integer, nullable=False, default=0, comment="Number of times the coupon has been used")
    expiry_date = Column(DateTime, nullable=False, comment="Coupon expiry date")
    is_active = Column(Boolean, nullable=False, default=True, comment="Coupon validity status")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def is_valid(self):
        return self.is_active and self.used_count < self.max_usage and datetime.utcnow() < self.expiry_date

class CouponUsage(database.Base):
    __tablename__ = "coupon_usage"
    __table_args__ = {"schema": "karigor"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = Column(String, nullable=False, comment="User ID from userandsettings service")
    booking_id = Column(String, ForeignKey("karigor.bookings.booking_id", ondelete="CASCADE"), nullable=False)
    coupon_id = Column(String, ForeignKey("karigor.coupons.id", ondelete="CASCADE"), nullable=False)
    discount_applied = Column(Numeric(10, 2), nullable=False, comment="Discount applied to this booking")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    booking = relationship("Booking", backref="coupon_usages")
    coupon = relationship("Coupon", backref="usages")

class OfferService(database.Base):
    __tablename__ = 'offer_services'
    __table_args__ = {"schema": "karigor"}

    offer_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, index=True)
    service_id = Column(String, nullable=False, index=True)
    image_url = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    title = Column(String(100), nullable=True, comment="Offer title")
    description = Column(Text, nullable=True, comment="Offer description")
    discount_type = Column(Enum(CouponType, values_callable=lambda x: [e.value for e in x]), nullable=True)
    discount_value = Column(Numeric(10, 2), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Refund(database.Base):
    __tablename__ = "refunds"
    __table_args__ = {"schema": "karigor"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    payment_id = Column(String, ForeignKey("karigor.payments.id", ondelete="CASCADE"))
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    payment = relationship("Payment", backref="refunds")


class AddToBag(database.Base):
    __tablename__ = 'add_to_bag'
    __table_args__ = {"schema": "karigor"}

    bag_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    service_id = Column(String(36), nullable=False)

    user_id = Column(String(36), nullable=True)
    unregistered_address_id = Column(String(36), nullable=True)

    quantity = Column(Integer, default=1)
    added_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)