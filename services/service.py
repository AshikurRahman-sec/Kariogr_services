from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from uuid import UUID

from models import *


def get_root_services(db: Session, offset: int, limit: int):
    """
    Fetch paginated root services and include second-level hierarchy with logo_data and is_leaf
    for the first root service.
    """
    # Query root services with logos
    root_services_query = (
        select(Service.id, Service.name, ServiceLogo.logo_data)
        .outerjoin(ServiceLogo, Service.id == ServiceLogo.service_id)
        .where(Service.parent_id == None)  # Root services have no parent
        .order_by(Service.created_at)
        .offset(offset)
        .limit(limit)
    )
    root_services = db.execute(root_services_query).fetchall()

    services_with_hierarchy = []

    for i, root_service in enumerate(root_services):
        # For the first root service in the pagination, fetch second-level data
        if i == 0:
            second_level_query = (
                select(Service.id, Service.name, ServiceLogo.logo_data, Service.is_leaf)
                .outerjoin(ServiceLogo, Service.id == ServiceLogo.service_id)
                .where(Service.parent_id == root_service.id)
            )
            second_level_data = db.execute(second_level_query).fetchall()
        else:
            second_level_data = []

        # Append the service with its data
        services_with_hierarchy.append({
            "service_id": root_service.id,
            "service_name": root_service.name,
            "logo_data": root_service.logo_data,
            "second_level_hierarchy": [
                {
                    "service_id": child.id,
                    "service_name": child.name,
                    "logo_data": child.logo_data,
                    "is_leaf": child.is_leaf,
                }
                for child in second_level_data
            ],
        })

    return services_with_hierarchy


def get_second_level_hierarchy(
    db: Session, root_service_id: UUID, offset: int, limit: int
):
    """
    Fetch paginated second-level hierarchy services for a specific root service.
    """
    # Query second-level services
    second_level_query = (
        select(Service.id, Service.name, ServiceLogo.logo_data, Service.is_leaf)
        .outerjoin(ServiceLogo, Service.id == ServiceLogo.service_id)
        .where(Service.parent_id == root_service_id)
        .order_by(Service.created_at)
        .offset(offset)
        .limit(limit)
    )
    second_level_data = db.execute(second_level_query).fetchall()

    # Count total second-level services
    total_count_query = select(func.count()).where(Service.parent_id == root_service_id)
    total_count = db.scalar(total_count_query)

    # Format response data
    formatted_data = [
        {
            "service_id": service.id,
            "service_name": service.name,
            "logo_data": service.logo_data,
            "is_leaf": service.is_leaf
        }
        for service in second_level_data
    ]

    return {
        "data": formatted_data,
        "total_count": total_count,
    }

def get_descendant_hierarchy(
    db: Session, service_id: UUID, offset: int, limit: int
):
    """
    Fetch paginated direct descendants of a service (first-level hierarchy),
    including up to 5 second-level descendants for each first-level descendant.
    """
    # Query first-level descendants
    first_level_query = (
        select(Service.id, Service.name, ServiceLogo.logo_data, Service.is_leaf, ServiceLogo.image_url)
        .outerjoin(ServiceLogo, Service.id == ServiceLogo.service_id)
        .where(Service.parent_id == service_id)
        .order_by(Service.created_at)
        .offset(offset)
        .limit(limit)
    )
    first_level_data = db.execute(first_level_query).fetchall()

    # Count total first-level descendants
    total_count_query = select(func.count()).where(Service.parent_id == service_id)
    total_count = db.scalar(total_count_query)

    # Fetch second-level descendants for each first-level descendant
    formatted_data = []
    for first_service in first_level_data:
        second_level_query = (
            select(Service.id, Service.name, ServiceLogo.logo_data, Service.is_leaf, ServiceLogo.image_url)
            .outerjoin(ServiceLogo, Service.id == ServiceLogo.service_id)
            .where(Service.parent_id == first_service.id)
            .order_by(Service.created_at)
            .limit(5)  # Limit to 5 second-level descendants
        )
        second_level_data = db.execute(second_level_query).fetchall()

        formatted_data.append({
            "service_id": first_service.id,
            "service_name": first_service.name,
            "logo_data": first_service.logo_data,
            "image_url": first_service.image_url,
            "is_leaf": first_service.is_leaf,
            "second_level_hierarchy": [
                {
                    "service_id": child.id,
                    "service_name": child.name,
                    "logo_data": child.logo_data,
                    "image_url": child.image_url,
                    "is_leaf": child.is_leaf,
                }
                for child in second_level_data
            ],
        })

    return {
        "data": formatted_data,
        "total_count": total_count,
    }


def get_service_details(db: Session, service_id: UUID):
    """
    Fetch details of a specific service, including image_path and description.
    """
    # Query the service details
    service_query = (
        select(
            Service.id,
            Service.name,
            ServiceLogo.image_url.label("image_path"),
            ServiceDescription.description,
            
        )
        .outerjoin(ServiceLogo, Service.id == ServiceLogo.service_id)
        .outerjoin(ServiceDescription, Service.id == ServiceDescription.service_id)
        .where(Service.id == service_id)
    )
    service_details = db.execute(service_query).fetchone()

    if not service_details:
        return None

    # Format the result as a dictionary
    return {
        "service_id": service_details.id,
        "service_name": service_details.name,
        "service_description": service_details.description,
        "image_url": service_details.image_path,
    }

def get_special_services(db: Session, offset: int, limit: int):
    """
    Fetch paginated services that are leaf nodes (services with no children).
    """
    # Query leaf services
    leaf_services_query = (
        select(Service.id, Service.name, ServiceLogo.image_url)
        .outerjoin(ServiceLogo, Service.id == ServiceLogo.service_id)
        .where(Service.is_leaf == True)  # Only leaf services
        .order_by(Service.created_at)
        .offset(offset)
        .limit(limit)
    )
    leaf_services = db.execute(leaf_services_query).fetchall()

    # Count total leaf services
    total_count_query = select(func.count()).where(Service.is_leaf == True)
    total_count = db.scalar(total_count_query)

    # Format the data
    formatted_data = [
        {
            "service_id": service.id,
            "service_name": service.name,
            "image_url": service.image_url,
            
        }
        for service in leaf_services
    ]

    return {
        "data": formatted_data,
        "total_count": total_count,
    }

def get_search_services(db: Session, offset: int, limit: int):
    """
    Fetch paginated services that are leaf nodes (services with no children).
    """
    # Query leaf services
    leaf_services_query = (
        select(Service.id, Service.name)
        .where(Service.is_leaf == True)  # Only leaf services
        .order_by(Service.created_at)
        .offset(offset)
        .limit(limit)
    )
    leaf_services = db.execute(leaf_services_query).fetchall()

    # Count total leaf services
    total_count_query = select(func.count()).where(Service.is_leaf == True)
    total_count = db.scalar(total_count_query)

    # Format the data
    formatted_data = [
        {
            "service_id": service.id,
            "service_name": service.name,  
        }
        for service in leaf_services
    ]

    return {
        "data": formatted_data,
        "total_count": total_count,
    }

async def get_booking_inputs_by_service(db: Session, service_id: str):
    booking_inputs = (
        db.query(BookingInput)
        .filter(BookingInput.service_id == service_id)
        .all()
    )
    # Ensure options are converted correctly using the model method
    for input in booking_inputs:
        input.options = input.get_options()  # Use model's method

    return booking_inputs

async def get_service_relatives(db: Session, service_id: str, limit: int = 10, offset: int = 0):
    # Fetch the given service
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return None

    # Fetch parent service ID (if exists)
    parent_id = service.parent.id if service.parent else None

    # Paginated children ordered by updated_at DESC
    children = (
        db.query(Service)
        .filter(Service.parent_id == parent_id)
        .order_by(desc(Service.updated_at))
        .limit(limit)
        .offset(offset)
        .all()
    )

    # Extract only required fields
    def get_logo(service):
        return service.logo[0].image_url if service.logo else None

    return {
        "parent_id": parent_id,
        "children": [
            {
                "id": child.id,
                "parent_id": child.parent_id,
                "image_url": get_logo(child),
            }
            for child in children
        ]
    }

async def get_all_second_level_services(db: Session, limit: int = 10, offset: int = 0):
    # Find paginated 2nd-level services
    second_level_services = (
        db.query(Service)
        .filter(Service.level == 2)
        .order_by(desc(Service.updated_at))
        .limit(limit)
        .offset(offset)
        .all()
    )

    # Get up to 5 children for each 2nd-level service
    second_level_with_children = []
    for service in second_level_services:
        children = (
            db.query(Service)
            .filter(Service.parent_id == service.id)
            .order_by(desc(Service.updated_at))
            .limit(5)
            .all()
        )

        second_level_with_children.append({
            "id": service.id,
            "name": service.name,
            "is_leaf": service.is_leaf,
            "children": [
                {
                    "id": child.id,
                    "name": child.name,
                    "is_leaf": child.is_leaf,
                    "image_url": child.logo[0].image_url if child.logo else None
                }
                for child in children
            ]
        })

    return second_level_with_children
