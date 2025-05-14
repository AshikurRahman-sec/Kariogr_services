from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import datetime
import uuid
import json

from models import Booking, BookingType, BookingWorker, BookingWorkerSkill, WorkerAddonService, AddToBag, Payment, Coupon, CouponUsage, OfferService
from schemas import BookingCreate, BookingResponse, WorkerSelection, AddToBagRequest, BookingConfirm, CreatePaymentRequest
from kafka_producer_consumer import kafka_payment_booking_service



async def create_booking(db: Session, booking_data: BookingCreate) -> BookingResponse:
    """Create booking in the database"""
    new_booking = Booking(
        service_area=booking_data.service_area,
        home_address=booking_data.home_address,
        worker_duration=booking_data.worker_duration,
        booking_type=BookingType(booking_data.booking_type).value,
        service_id=booking_data.service_id,
        user_id=booking_data.user_id,
        status='pending'
    )
    new_booking.set_dates(booking_data.dates)
    new_booking.set_times(booking_data.times)

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return BookingResponse.from_orm(new_booking)

async def get_booking(db: Session, booking_id: str) -> BookingResponse:
    """
    Retrieve a booking by its ID.
    """
    result = db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise ValueError(f"Booking with id {booking_id} not found.")
    return BookingResponse.from_orm(booking)  


async def add_workers_to_booking(db: Session, worker_selection: WorkerSelection):
    booking = db.query(Booking).filter(Booking.booking_id == worker_selection.booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add workers to this booking")

    for worker in worker_selection.workers:
        # worker_service = kafka_payment_booking_service.get_worker_details('user_request', worker.worker_id, worker.skill_id)
        # worker_service = db.query(WorkerService).filter(WorkerService.worker_id == worker_id).first()
        # if not worker_service:
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Worker {worker_id} service details not found")

        booking_worker = BookingWorker(
            booking_id=booking.booking_id,
            worker_id=worker.worker_id,
        )
        db.add(booking_worker)
        db.commit()
        db.refresh(booking_worker)

        # Store service charge and charge unit
        worker_skill = BookingWorkerSkill(
            booking_worker_id=booking_worker.id,
            skill_id=worker.skill_id,
            charge_amount=worker.charge_amount,
            charge_unit=worker.charge_unit
        )
        db.add(worker_skill)

        # Adding add-ons if provided
        if worker in worker_selection.addons:
            #for addon_id in worker_selection.addonsworker_id]:
                # addon_service = db.query(AddonService).filter(AddonService.id == addon_id).first()
                # if not addon_service:
                #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Addon service {addon_id} not found")

                worker_addon = WorkerAddonService(
                    booking_worker_id=booking_worker.id,
                    addon_service_id=worker.skill_id,
                    quantity=1,  # Default quantity
                    charge_amount=worker.charge_amount,
                    charge_unit = worker.charge_unit
                )
                db.add(worker_addon)

    booking.status = "worker_selected"
    db.commit()

    return {"message": "Workers added successfully", "booking_id": booking.booking_id}

async def get_booking_summary(db: Session, booking_id: str):
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        return {"error": "Booking not found"}

    user_details = await kafka_payment_booking_service.get_user_details('user_request', booking.user_id)

    workers = db.query(BookingWorker).filter(BookingWorker.booking_id == booking_id).all()
    workers_list = []

    for worker in workers:
        skills = db.query(BookingWorkerSkill).filter(BookingWorkerSkill.booking_worker_id == worker.id).all()
        addons = db.query(WorkerAddonService).filter(WorkerAddonService.booking_worker_id == worker.id).all()

        worker_details = await kafka_payment_booking_service.get_worker_details('user_request', worker.worker_id)

        skills_list = []
        for skill in skills:
            service_details = await kafka_payment_booking_service.get_service_details('service_request', skill.skill_id)
            #print("here",service_details)
            skills_list.append(
                {
                "skill_id": skill.skill_id,
                "skill_name": service_details['service_data']["service_name"],
                "charge_amount": skill.charge_amount,
                "charge_unit": skill.charge_unit or None
                })
        

        # 🔧 Assemble addon info
        addons_list = []
        for addon in addons:
            service_details = await kafka_payment_booking_service.get_service_details('service_request', addon.addon_service_id)
            worker_details = await kafka_payment_booking_service.get_worker_details('user_request', addon.booking_worker_id)
            addons_list.append(
                {
                    "addon_service_id": addon.addon_service_id,
                    "skill_name": service_details['service_data']["service_name"],
                    "addon_worker_id": addon.booking_worker_id,
                    "addon_worker_name": f"{worker_details['worker_data']['user_profile']['first_name']} {worker_details['worker_data']['user_profile']['last_name']}",
                    "quantity": addon.quantity,
                    "charge_amount": addon.charge_amount
                })


        # 👷 Append worker info
        workers_list.append({
            "worker_id": worker.worker_id,
            "worker_name": f"{worker_details['worker_data']['user_profile']['first_name']} {worker_details['worker_data']['user_profile']['last_name']}",
            "skills": skills_list,
            "addons": addons_list
        })

    return {
        "booking_id": booking.booking_id,
        "user_id": booking.user_id,
        "user_name": f"{user_details['user_data']['first_name']} {user_details['user_data']['last_name']}",
        "service_id": booking.service_id,
        "booking_time": booking.get_times(),  # assuming this returns a list
        "workers": workers_list,
        "total_charge": booking.total_charge
    }

async def add_to_bag(db: Session, data: AddToBagRequest) -> AddToBag:
    bag_item = AddToBag(
        service_id=data.service_id,
        user_id=data.user_id,
        unregistered_address_id=data.unregistered_address_id,
        quantity=data.quantity
    )
    db.add(bag_item)
    db.commit()
    db.refresh(bag_item)
    return bag_item

async def remove_from_bag(db: Session, bag_id: str):
    item = db.query(AddToBag).filter(AddToBag.bag_id == bag_id).first()
    if item:
        db.delete(item)
        db.commit()
    return item

async def get_bag_items_by_user(db: Session, user_id: str, unregistered_address_id: str):
    data = []
    query = db.query(AddToBag)
    if user_id:
        bag_items = query.filter(AddToBag.user_id == user_id).all()
    elif unregistered_address_id:
        bag_items = query.filter(AddToBag.unregistered_address_id == unregistered_address_id).all()
    
    for item in bag_items:
        service_details = await kafka_payment_booking_service.get_service_details('service_request', item.service_id)
        data.append(
                    {
            "quantity": item.quantity,
            "bag_id": item.bag_id,
            "unregistered_address_id": item.unregistered_address_id,
            "service_id": item.service_id,
            "service_name": service_details['service_data']["service_name"],
            "user_id": item.user_id,
            "added_at": item.added_at,
            }
                
        )

    return data


def confirm_booking(db: Session, confirm_data: BookingConfirm):
    booking = db.query(Booking).filter(Booking.booking_id == confirm_data.booking_id).first()
    if booking:
        booking.status = "confirmed"
        db.commit()
        return {"message": "Booking confirmed"}
    return {"error": "Booking not found"}

def calculate_discount(amount: Decimal, discount_type: str, value: Decimal) -> Decimal:
    if discount_type == "percentage":
        return (amount * value) / 100
    elif discount_type == "fixed_amount":
        return min(amount, value)
    return Decimal("0.00")

def create_payment(db: Session, data: CreatePaymentRequest):
    discount = Decimal("0.00")
    coupon_usage_id = None

    # Handle coupon
    if data.coupon_code:
        coupon = db.query(Coupon).filter(Coupon.code == data.coupon_code, Coupon.is_active == True).first()
        if not coupon:
            raise ValueError("Invalid or inactive coupon.")

        if coupon.expiry_date < datetime.utcnow():
            raise ValueError("Coupon expired.")

        if coupon.used_count >= coupon.max_usage:
            raise ValueError("Coupon usage limit reached.")

        discount = calculate_discount(data.amount, coupon.discount_type.value, coupon.discount_value)

        # Create CouponUsage record
        coupon_usage = CouponUsage(
            id=str(uuid.uuid4()),
            user_id=data.user_id,
            booking_id=data.booking_id,
            coupon_id=coupon.id,
            discount_applied=discount,
            created_at=datetime.utcnow()
        )
        db.add(coupon_usage)
        db.flush()  # to get ID before commit
        coupon_usage_id = coupon_usage.id

        # Increment coupon usage
        coupon.used_count += 1

    # Handle offer
    if data.offer_id:
        offer = db.query(OfferService).filter(OfferService.offer_id == data.offer_id).first()
        if offer and offer.status == "active" and offer.start_date <= datetime.utcnow() <= offer.end_date:
            offer_discount = calculate_discount(data.amount, offer.discount_type.value, offer.discount_value)
            discount += offer_discount

    final_price = max(data.amount - discount, Decimal("0.00"))

    payment = Payment(
        id=str(uuid.uuid4()),
        booking_id=data.booking_id,
        user_id=data.user_id,
        amount=data.amount,
        discount_price=discount,
        final_price=final_price,
        method=data.method,
        status="pending",
        transaction_id=data.transaction_id,
        coupon_usage_id=coupon_usage_id
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment