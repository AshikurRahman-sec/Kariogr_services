import sqlalchemy.orm as _orm
from sqlalchemy import select, func
from uuid import UUID

from schemas import user_schemas as _schemas
from models import user_model as _model


def update_user_profile(db: _orm.Session, user_id: str, profile_data: _schemas.UserProfileUpdate):
    db_profile = db.query(_model.UserProfile).filter(_model.UserProfile.user_id == user_id).first()
    for key, value in profile_data.dict(exclude_unset=True).items():
        setattr(db_profile, key, value)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def update_worker_profile(db: _orm.Session, user_id: str, profile_data: _schemas.WorkerProfileUpdate):
    db_worker = db.query(_model.WorkerProfile).filter(_model.WorkerProfile.user_id == user_id).first()
    for key, value in profile_data.dict(exclude_unset=True).items():
        setattr(db_worker, key, value)
    db.commit()
    db.refresh(db_worker)
    return db_worker

async def create_address(db: _orm.Session, address: _schemas.UnregisteredUserAddressCreate):
    db_address = _model.UnregisteredUserAddress(
        mobile_id=address.mobile_id,
        street_address=address.street_address,
        division=address.division,
        district=address.district,
        thana=address.thana,
        latitude=address.latitude,
        longitude=address.longitude
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

async def get_worker_zones_by_skill(db: _orm.Session, service_id: str):
    worker_zones = (
        db.query(_model.WorkerZone)
        .join(_model.WorkerProfile, _model.WorkerZone.worker_id == _model.WorkerProfile.worker_id)
        .join(_model.WorkerSkill, _model.WorkerProfile.worker_id == _model.WorkerSkill.worker_id)
        .filter(_model.WorkerSkill.skill_id == service_id)
        .all()
    )
    return worker_zones

async def get_workers_by_skill_and_district(db: _orm.Session, skill_id: str, district: list[str], size: int, page: int):
    """
    Retrieve workers who have a specific skill and operate in specific districts with pagination.
    """
    query = (
        db.query(_model.WorkerSkillZone)
        .join(_model.WorkerZone, _model.WorkerSkillZone.worker_zone_id == _model.WorkerZone.worker_zone_id)
        .filter(
            _model.WorkerSkillZone.skill_id == skill_id,
            _model.WorkerZone.district.ilike(district)
        )
        .options(
            _orm.joinedload(_model.WorkerSkillZone.worker).joinedload(_model.WorkerProfile.user), 
            _orm.joinedload(_model.WorkerSkillZone.skill),  
            _orm.joinedload(_model.WorkerSkillZone.worker_zone),  
        )
    )

    total_services = query.count()  # Get total count before applying limit & offset

    worker_skill_zones = query.offset(page).limit(size).all()  # Apply pagination

    data = [
        {
            "user": ws.worker.user,
            "worker_profile": ws.worker,
            "skill_with_zone": {
                "skill": _schemas.SkillOut(
                    skill_id=ws.skill.skill_id,
                    skill_name=ws.skill.skill_name,
                    category=ws.skill.category,
                    description=ws.skill.description,
                ),
                "worker_zone": _schemas.WorkerZoneOut(
                    worker_zone_id=ws.worker_zone.worker_zone_id,
                    worker_id=ws.worker_zone.worker_id,
                    division=ws.worker_zone.division,
                    district=ws.worker_zone.district,
                    thana=ws.worker_zone.thana,
                    road_number=ws.worker_zone.road_number,
                    latitude=ws.worker_zone.latitude,
                    longitude=ws.worker_zone.longitude,
                ),
            },
        }
        for ws in worker_skill_zones
    ]

    return {
        "data": data,
        "page": (page // size) + 1,
        "size": size,
        "total_services": total_services
    }


