from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from fastapi.responses import FileResponse
import base64
import os

from models import App



async def get_app_service_data(db: Session):
    
    # with open('services/Cleaning.png', 'rb') as file:
    #     file_data = file.read()

    #     # sql_query = text("INSERT INTO karigor.apps (name, description, logo, created_at, updated_at) \
    #     #         VALUES ('My Application', 'This is a description of the app.', :logo, NOW(), NOW())")
        
    #     # db.execute(sql_query, {'logo': file_data})
        
    #     # db.commit()

    #     sql_query = text("INSERT INTO karigor.services (app_id, name, description, logo, image_path, created_at, updated_at)\
    #                      VALUES(22, 'Cleaning', '', :logo, '', NOW(), NOW())")
        
    #     db.execute(sql_query, {'logo': file_data})
        
    #     db.commit()

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
    


async def get_image(image_name: str):
    # Construct the full file path
    file_path = os.path.join("static/images", image_name)
    
    # Serve the image file
    return FileResponse(file_path, media_type="image/png")
  
