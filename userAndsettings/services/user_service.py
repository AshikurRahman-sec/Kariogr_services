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

async def get_workers_by_skill_and_district(db: _orm.Session, skill_id: str, district: str):
    """
    Retrieve workers who have a specific skill and are operating in a specific district,
    ensuring skills are paired with the correct worker zones.
    """
    workers = (
        db.query(_model.WorkerProfile)
        .join(_model.WorkerSkillZone, _model.WorkerProfile.worker_id == _model.WorkerSkillZone.worker_id)
        .join(_model.WorkerZone, _model.WorkerSkillZone.worker_zone_id == _model.WorkerZone.worker_zone_id)
        .filter(
            _model.WorkerProfile.user.has(_model.UserProfile.profile_id.isnot(None)),  # Ensure worker is valid
            _model.WorkerProfile.skills.any(_model.WorkerSkill.skill_id == skill_id),  # Ensure worker has skill
            _model.WorkerZone.district.ilike(f"%{district}%")  # Ensure skill is available in correct zone
        )
        .options(
            _orm.joinedload(_model.WorkerProfile.user),
            _orm.joinedload(_model.WorkerProfile.skills),
            _orm.joinedload(_model.WorkerProfile.working_zones),
            _orm.joinedload(_model.WorkerProfile.skill_zones).joinedload(_model.WorkerSkillZone.worker_zone)  # Ensure skill zones are loaded properly
        )
        .distinct()
        .all()
    )

    return [
        {
            "user": worker.user,
            "worker_profile": worker,
            "skill_with_zone": [
                _schemas.SkillWithZoneOut(
                    skill=_schemas.SkillOut(
                        skill_id=worker_skill.skill.skill_id,
                        skill_name=worker_skill.skill.skill_name,
                        category=worker_skill.skill.category,
                        description=worker_skill.skill.description,
                    ),
                    worker_zone=_schemas.WorkerZoneOut(
                        worker_zone_id=zone.worker_zone.worker_zone_id,
                        worker_id=zone.worker_zone.worker_id,
                        division=zone.worker_zone.division,
                        district=zone.worker_zone.district,
                        thana=zone.worker_zone.thana,
                        road_number=zone.worker_zone.road_number,
                        latitude=zone.worker_zone.latitude,
                        longitude=zone.worker_zone.longitude,
                    )
                )
                for worker_skill in worker.skills
                for zone in worker.skill_zones  # Ensuring only skill zones that match the query
                if zone.worker_zone.district.lower() == district.lower()
            ],
        }
        for worker in workers
    ]

