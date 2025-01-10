from sqlalchemy.orm import Session, joinedload
import fastapi as _fastapi
import base64


from models import App
# from kafka_producer import kafka_producer_service


async def get_app_service_data(db: Session):
    
    

    result = db.execute(
        db.query(App)
        .options(joinedload(App.service))  
    )
    apps = result.scalars().all()

    response = []
    for app in apps:
        response.append({
            "id": app.id,
            "name": app.name,
            "description": app.description,
            "logo": base64.b64encode(app.logo).decode('utf-8') if app.logo else None,
            "created_at": app.created_at.isoformat() if app.created_at else None,
            "updated_at": app.updated_at.isoformat() if app.updated_at else None,
            "services": [
                {
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "logo": base64.b64encode(service.logo).decode('utf-8') if service.logo else None,
                    "image_path": service.image_path,
                    "created_at": service.created_at.isoformat() if service.created_at else None,
                    "updated_at": service.updated_at.isoformat() if service.updated_at else None,
                }
                for service in app.service  
            ]
        })

    return response