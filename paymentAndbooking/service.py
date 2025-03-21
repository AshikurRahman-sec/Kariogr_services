from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import HTTPException, status
import uuid
import json

from models import Booking, BookingType, BookingWorker, BookingWorkerSkill, WorkerAddonService
from schemas import BookingCreate, BookingResponse, WorkerSelection
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
            #for addon_id in worker_selection.addons[worker_id]:
                # addon_service = db.query(AddonService).filter(AddonService.id == addon_id).first()
                # if not addon_service:
                #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Addon service {addon_id} not found")

                worker_addon = WorkerAddonService(
                    booking_worker_id=booking_worker.id,
                    addon_service_id=worker.skill_id,
                    quantity=1,  # Default quantity
                    #charge_amount=addon_service.charge_amount
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

    workers = db.query(BookingWorker).filter(BookingWorker.booking_id == booking_id).all()
    workers_list = []

    for worker in workers:
        skills = db.query(BookingWorkerSkill).filter(BookingWorkerSkill.booking_worker_id == worker.id).all()
        addons = db.query(WorkerAddonService).filter(WorkerAddonService.booking_worker_id == worker.id).all()

        workers_list.append({
            "worker_id": worker.worker_id,
            "skills": [{
                "skill_id": skill.skill_id,
                "charge_amount": skill.charge_amount,
                "charge_unit": skill.charge_unit if skill.charge_unit else None
            } for skill in skills],
            "addons": [{
                "addon_service_id": addon.addon_service_id,
                "addon_worker_id": addon.booking_worker_id,
                "quantity": addon.quantity,
                "charge_amount": addon.charge_amount
            } for addon in addons]
        })

    return {
        "booking_id": booking.booking_id,
        "user_id": booking.user_id,
        "service_id": booking.service_id,
        "booking_time": booking.get_times(),  # Returns list of booking times
        "workers": workers_list,
        "total_charge": booking.total_charge
    }