from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from model.auth_model import *
import database as _database


#from router.oauth_rout import router as oauth_router
from router.auth_rout import router as auth_router
from auth.kafka_producer_consumer import kafka_producer_service


app = FastAPI()


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "detail": exc.detail}
    )
app.add_exception_handler(HTTPException, custom_http_exception_handler)


#app.include_router(oauth_router, prefix="/api", tags=["Custom OAuth"])
app.include_router(auth_router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    _database.create_database()
    await kafka_producer_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    await kafka_producer_service.stop()

# Endpoint to check if the API is live
@app.get("/check_api")
async def check_api():
    return {"status": "Connected to API Successfully"}

