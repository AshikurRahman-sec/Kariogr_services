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
    Retrieve workers who have a specific skill and are operating in a specific district.
    """

    workers = (
        db.query(_model.WorkerProfile)
        .filter(
            _model.WorkerProfile.user.has(_model.UserProfile.profile_id.isnot(None)),  # Filter users correctly
            _model.WorkerProfile.skills.any(_model.WorkerSkill.skill_id == skill_id),  # Filter by skill
            _model.WorkerProfile.working_zones.any(func.lower(_model.WorkerZone.district) == district.lower())  # Filter by district
        )
        .options(
            _orm.joinedload(_model.WorkerProfile.user),  # Load user data without join
            _orm.joinedload(_model.WorkerProfile.skills),  # Load skills efficiently
            _orm.joinedload(_model.WorkerProfile.working_zones)  # Load working zones efficiently
        )
        .distinct()
        .all()
    )

    return [
    {
        "user": worker.user,
        "worker_profile": worker,
        "skills": [
            _schemas.SkillOut(
                skill_id=worker_skill.skill.skill_id,
                skill_name=worker_skill.skill.skill_name,
                category=worker_skill.skill.category,
                description=worker_skill.skill.description,
            )
            for worker_skill in worker.skills
        ],
        "worker_zone": worker.working_zones,  # List of zones
    }
    for worker in workers
]