from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import *
import database as _database

from rout import router as service_router
# from kafka_producer import kafka_producer_service


app = FastAPI()

async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "detail": exc.detail}
    )

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    _database.create_database()
#     await kafka_producer_service.start()

# @app.on_event("shutdown")
# async def shutdown_event():
#     await kafka_producer_service.stop()

# Endpoint to check if the API is live
@app.get("/check_api")
async def check_api():
    return {"status": "Connected to API Successfully"}

app.include_router(service_router, prefix="/api", tags=["Services"])