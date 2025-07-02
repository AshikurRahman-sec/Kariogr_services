import sqlalchemy.orm as _orm
from sqlalchemy import select, func
from uuid import UUID

from schemas import user_schemas as _schemas
from models import user_model as _model
from fastapi.encoders import jsonable_encoder


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
        .distinct(_model.WorkerZone.division)
        .all()
    )
    return worker_zones

async def get_workers_by_skill_and_district(db: _orm.Session, skill_id: str, district: str, size: int, page: int):
    """
    Retrieve workers who have a specific skill and operate in specific districts with pagination,
    including average worker skill ratings.
    """
    subquery = (
        db.query(
            _model.WorkerSkillRating.worker_id,
            _model.WorkerSkillRating.skill_id,
            func.avg(_model.WorkerSkillRating.rating).label("average_rating"),
            func.count(_model.WorkerSkillRating.rating).label("rating_count")
        )
        .group_by(_model.WorkerSkillRating.worker_id, _model.WorkerSkillRating.skill_id)
        .subquery()
    )

    query = (
        db.query(_model.WorkerSkillZone, subquery.c.average_rating, subquery.c.rating_count)
        .join(_model.WorkerZone, _model.WorkerSkillZone.worker_zone_id == _model.WorkerZone.worker_zone_id)
        .outerjoin(
            subquery,
            (_model.WorkerSkillZone.worker_id == subquery.c.worker_id) &
            (_model.WorkerSkillZone.skill_id == subquery.c.skill_id)
        )
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

    total_services = query.count()
    worker_skill_zones = query.offset(page).limit(size).all()

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
                    service_charge=ws.service_charge,
                    charge_unit=ws.charge_unit,
                    discount=ws.discount
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
            "rating": {
                "average": float(avg_rating) if avg_rating is not None else None,
                "count": int(rating_count) if rating_count is not None else 0
            }
        }
        for ws, avg_rating, rating_count in worker_skill_zones
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
                    description=ws.skill.description,
                    service_charge=ws.service_charge,
                    charge_unit= ws.charge_unit,
                    discount= ws.discount
                ) for ws in worker.skill_zones
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


async def get_user_profile_by_user_id(user_id: str, db: _orm.Session):
    from kafka_producer_consumer import kafka_user_settings_service
    user_profile = (
        db.query(_model.UserProfile)
        .options(
            _orm.joinedload(_model.UserProfile.address),
            _orm.joinedload(_model.UserProfile.worker_profile)
        )
        .filter(_model.UserProfile.user_id == user_id)
        .first()
    )
    user_auth_info = await kafka_user_settings_service.get_user_auth_info('auth_info', user_id)
    return {
            "user_profile": jsonable_encoder(user_profile),
            "user_auth_info": jsonable_encoder(user_auth_info)
        }

async def get_worker_details_by_worker_id(worker_id: str, db: _orm.Session):
    worker = (
    db.query(_model.WorkerProfile, _model.UserProfile)
    .join(_model.UserProfile, _model.UserProfile.profile_id == _model.WorkerProfile.worker_id)
    .filter(_model.WorkerProfile.worker_id == worker_id)
    .first()
)   
    worker_profile, user_profile = worker
    #user_auth_info = await UserAndSettingsService.get_user_auth_info('auth_info', user_profile.user_id)

    return {
        "worker_profile": jsonable_encoder(worker_profile),
        "user_profile": jsonable_encoder(user_profile),
        #"user_auth_info": jsonable_encoder(user_auth_info)
    }

async def create_or_update_worker_skill_rating(db: _orm.Session, request: _schemas.CreateWorkerSkillRatingRequest):
    # Check for existing rating
    existing_rating = db.query(_model.WorkerSkillRating).filter_by(
        worker_id=request.worker_id,
        skill_id=request.skill_id,
        user_id=request.user_id
    ).first()

    if existing_rating:
        existing_rating.rating = request.rating
        existing_rating.review_text = request.review_text
        db.commit()
        db.refresh(existing_rating)
        rating_obj = existing_rating
    else:
        rating_obj = _model.WorkerSkillRating(
            worker_id=request.worker_id,
            skill_id=request.skill_id,
            user_id=request.user_id,
            rating=request.rating,
            review_text=request.review_text
        )
        db.add(rating_obj)
        db.commit()
        db.refresh(rating_obj)

    # Calculate updated average rating
    result = db.query(
        func.avg(_model.WorkerSkillRating.rating).label("average_rating"),
        func.count(_model.WorkerSkillRating.rating).label("total_ratings")
    ).filter(
        _model.WorkerSkillRating.worker_id == request.worker_id,
        _model.WorkerSkillRating.skill_id == request.skill_id
    ).one()

    average_rating = float(result.average_rating or 0.0)
    total_ratings = result.total_ratings or 0

    rating_response = _schemas.WorkerSkillRatingResponse.from_orm(rating_obj)

    return _schemas.CreateWorkerSkillRatingResponse(
        rating=rating_response,
        average_rating=round(average_rating, 2),
        total_ratings=total_ratings
    )
 
async def get_worker_details_by_worker_and_skill(db: _orm.Session, worker_id: str, skill_id: str) -> _schemas.WorkerWithSkillsAndZonesOut | None:
    # Step 1: Get WorkerSkillZone (to include zone + skill data)
    ws_zone = (
        db.query(_model.WorkerSkillZone)
        .options(
            _orm.joinedload(_model.WorkerSkillZone.worker).joinedload(_model.WorkerProfile.user),
            _orm.joinedload(_model.WorkerSkillZone.skill),
            _orm.joinedload(_model.WorkerSkillZone.worker_zone),
        )
        .filter(
            _model.WorkerSkillZone.worker_id == worker_id,
            _model.WorkerSkillZone.skill_id == skill_id
        )
        .first()
    )

    if not ws_zone:
        return None

    # Step 2: Get average rating and count
    avg_rating_result = (
        db.query(
            func.avg(_model.WorkerSkillRating.rating).label("average"),
            func.count(_model.WorkerSkillRating.rating).label("count")
        )
        .filter(
            _model.WorkerSkillRating.worker_id == worker_id,
            _model.WorkerSkillRating.skill_id == skill_id
        )
        .first()
    )

    avg_rating = float(avg_rating_result.average) if avg_rating_result.average else 0.0
    rating_count = avg_rating_result.count or 0

    # Step 3: Construct response
    return _schemas.WorkerWithSkillsAndZonesOut(
    user=_schemas.UserProfileOut.from_orm(ws_zone.worker.user),
    worker_profile=_schemas.WorkerProfileOut.from_orm(ws_zone.worker),
    skill_with_zone=_schemas.SkillWithZoneOut(
        skill=_schemas.SkillOut(
            skill_id=ws_zone.skill.skill_id,
            skill_name=ws_zone.skill.skill_name,
            category=ws_zone.skill.category,
            description=ws_zone.skill.description,
            service_charge=float(ws_zone.service_charge),
            charge_unit=ws_zone.charge_unit,
            discount=float(ws_zone.discount or 0.0),
        ),
        worker_zone=_schemas.WorkerZoneOut.from_orm(ws_zone.worker_zone),
    ),
    rating=_schemas.RatingOut(average=avg_rating, count=rating_count)
)


async def create_comment(db: _orm.Session, comment_data: _schemas.CreateComment):
    parent_comment = None
    depth = 0

    if comment_data.parent_comment_id:
        parent_comment = db.query(_model.WorkerSkillComment).filter_by(comment_id=comment_data.parent_comment_id).first()
        if not parent_comment:
            raise ValueError("Parent comment not found.")
        depth = parent_comment.depth + 1
        # if depth > 3:
        #     raise ValueError("Max reply depth exceeded.")

    user_profiel_id = db.query(_model.UserProfile).filter_by(user_id=comment_data.user_id).first()
    comment = _model.WorkerSkillComment(
        user_id=user_profiel_id,
        worker_id=comment_data.worker_id,
        skill_id=comment_data.skill_id,
        comment_text=comment_data.comment_text,
        parent_comment_id=comment_data.parent_comment_id,
        depth=depth
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_top_level_comments(db: _orm.Session, worker_id: str, skill_id: str, limit: int, offset: int):
    comments = db.query(_model.WorkerSkillComment)\
        .filter_by(worker_id=worker_id, skill_id=skill_id, parent_comment_id=None)\
        .order_by(_model.WorkerSkillComment.created_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()

    return [{
        "comment_id": c.comment_id,
        "user_id": c.user_id,
        "comment_text": c.comment_text,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
        "depth": c.depth,
        "reactions": [{"reaction_type": r.reaction_type} for r in c.reactions],
        "replies": []  # load replies lazily
    } for c in comments]

def get_replies(db: _orm.Session, parent_comment_id: str, limit: int, offset: int):
    replies = db.query(_model.WorkerSkillComment)\
        .filter_by(parent_comment_id=parent_comment_id)\
        .order_by(_model.WorkerSkillComment.created_at.asc())\
        .offset(offset)\
        .limit(limit)\
        .all()

    return [{
        "comment_id": r.comment_id,
        "user_id": r.user_id,
        "comment_text": r.comment_text,
        "created_at": r.created_at,
        "updated_at": r.updated_at,
        "depth": r.depth,
        "reactions": [{"reaction_type": rc.reaction_type} for rc in r.reactions],
        "replies": []  # nested replies can be added if needed
    } for r in replies]

def create_reaction(db: _orm.Session, user_id: str, reaction_data: _schemas.CreateReaction):
    # Check if the user already reacted to this comment
    existing = db.query(_model.CommentReaction).filter_by(
        comment_id=str(reaction_data.comment_id),
        user_id=user_id
    ).first()

    if existing:
        # If same type, return; if different, update
        if existing.reaction_type == reaction_data.reaction_type:
            return existing
        existing.reaction_type = reaction_data.reaction_type
        db.commit()
        db.refresh(existing)
        return existing

    # Create new reaction
    new_reaction = _model.CommentReaction(
        comment_id=str(reaction_data.comment_id),
        user_id=user_id,
        reaction_type=reaction_data.reaction_type
    )
    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)
    return new_reaction