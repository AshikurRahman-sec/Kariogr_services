from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID

from models import Service, ServiceLogo,  ServiceDescription


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
        select(Service.id, Service.name, ServiceLogo.logo_data)
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
            "is_leaf": service.is_leaf,
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
        select(Service.id, Service.name, ServiceLogo.logo_data, Service.is_leaf)
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
            select(Service.id, Service.name, ServiceLogo.logo_data, Service.is_leaf)
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
            "is_leaf": first_service.is_leaf,
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
        "image_path": service_details.image_path,
    }