from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

from routers.auth_rout import router as auth_router
from routers.frontpage_rout import router as frontpage_router
from routers.services_rout import router as service_router
from routers.userAndsettings_rout import router as user_settings_router
from routers.paymentAndbooking_rout import router as payment_booking_router

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization"],  # Ensure Authorization is allowed
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router, prefix="/auth/gateway")
app.include_router(frontpage_router, prefix="/api", tags=["Frontpage Data"])
app.include_router(service_router, prefix="/service/gateway", tags=["Service"])
app.include_router(user_settings_router, prefix="/user-settings/gateway", tags=["User And Settings"])
app.include_router(payment_booking_router, prefix="/payment-booking/gateway", tags=["Payment And Booking"])