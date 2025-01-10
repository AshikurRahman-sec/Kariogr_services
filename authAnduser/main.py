from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from models.fastapi_auth_model import *
from models.google_login_model import *
from models.oauth_model import *
import database as _database


from router.oauth_rout import router as oauth_router
from router.google_login_rout import router as google_login_router
from router.fastapi_auth_rout import router as fastapi_auth_router
from kafka_producer import kafka_producer_service


app = FastAPI()


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "detail": exc.detail}
    )

app.include_router(oauth_router, prefix="/api", tags=["OAuth Service"])
app.include_router(fastapi_auth_router, prefix="/api", tags=["Fastapi Auth"])


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

