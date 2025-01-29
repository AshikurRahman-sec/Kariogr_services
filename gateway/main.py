from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import logging



app = FastAPI()

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)


app.mount("/static", StaticFiles(directory="static"), name="static")

from routers.auth_rout import router as auth_router
from routers.frontpage_rout import router as frontpage_router


app.include_router(auth_router, prefix="/oauth")
app.include_router(frontpage_router, prefix="/api", tags=["Frontpage Data"])