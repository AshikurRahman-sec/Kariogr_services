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

async def get_workers_by_zone(db: _orm.Session, worker_id: str, district: str, size: int, page: int):
    """
    Fetch paginated workers for a given worker ID and working zone (district).
    """
    query = db.query(_model.WorkerProfile).join(_model.WorkerZone).filter(
        _model.WorkerProfile.worker_id == worker_id,
        _model.WorkerZone.district.ilike(district)
    )

    # Get total count before applying pagination
    total_workers = query.count()

    # Apply pagination
    workers = query.offset(page * size).limit(size).all()

    worker_list = []
    
    for worker in workers:
        worker_data = _schemas.WorkerDetailsOut(
            user=_schemas.UserProfileOut(
                profile_id=worker.user.profile_id,
                user_id=worker.user.user_id,
                first_name=worker.user.first_name,
                last_name=worker.user.last_name,
                phone_number=worker.user.phone_number,
                date_of_birth=worker.user.date_of_birth,
                profile_picture_url=worker.user.profile_picture_url,
            ),
            worker_profile=_schemas.WorkerProfileOut(
                worker_id=worker.worker_id,
                hourly_rate=worker.hourly_rate,
                availability_status=worker.availability_status,
                bio=worker.bio,
            ),
            skills=[
                _schemas.SkillOut(
                    skill_id=ws.skill.skill_id,
                    skill_name=ws.skill.skill_name,
                    category=ws.skill.category,
                    description=ws.skill.description
                ) for ws in worker.skills
            ],
            working_zone=_schemas.WorkerZoneOut(
                worker_zone_id=worker.working_zones[0].worker_zone_id,
                worker_id=worker.working_zones[0].worker_id,
                division=worker.working_zones[0].division,
                district=worker.working_zones[0].district,
                thana=worker.working_zones[0].thana,
                road_number=worker.working_zones[0].road_number,
                latitude=worker.working_zones[0].latitude,
                longitude=worker.working_zones[0].longitude
            ) if worker.working_zones else None
        )
        worker_list.append(worker_data)

    return worker_list, total_workers




