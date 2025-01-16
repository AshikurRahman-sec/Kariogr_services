from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID

from models import Service, ServiceLogo


def get_root_services(db: Session, offset: int, limit: int):
    """
    Fetch paginated root services and include second-level hierarchy only for the first root service.
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
                select(Service.id, Service.name)
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
                {"service_id": child.id, "service_name": child.name}
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
        }
        for service in second_level_data
    ]

    return {
        "data": formatted_data,
        "total_count": total_count,
    }

def get_second_and_third_level_hierarchy(
    db: Session, root_service_id: UUID, offset: int, limit: int
):
    """
    Fetch paginated second-level hierarchy services for a specific root service,
    including up to 5 third-level services for each second-level service.
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

    # Fetch third-level services for each second-level service
    formatted_data = []
    for second_service in second_level_data:
        third_level_query = (
            select(Service.id, Service.name, ServiceLogo.logo_data)
            .outerjoin(ServiceLogo, Service.id == ServiceLogo.service_id)
            .where(Service.parent_id == second_service.id)
            .order_by(Service.created_at)
            .limit(5)  # Limit to 5 third-level services
        )
        third_level_data = db.execute(third_level_query).fetchall()

        formatted_data.append({
            "service_id": second_service.id,
            "service_name": second_service.name,
            "logo_data": second_service.logo_data,
            "third_level_hierarchy": [
                {"service_id": child.id, "service_name": child.name, "logo_data": child.logo_data}
                for child in third_level_data
            ],
        })

    return {
        "data": formatted_data,
        "total_count": total_count,
    }


