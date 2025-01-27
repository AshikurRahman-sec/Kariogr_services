from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import requests
from pydantic import BaseModel
from datetime import datetime



# Define the base URL for the service
SERVICE_BASE_URL = "http://service-url"  # Replace with the actual service base URL

router = APIRouter()

@router.post("/signup/")
async def signup_gateway(
    request_header: RequestHeader,
    email: str,
    password: str,
):
    """
    Gateway API to forward the `signup` request to the service.
    """
    try:
        payload = {"email": email, "password": password}
        response = requests.post(f"{SERVICE_BASE_URL}/signup/", json=payload)
        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_header.requestId,
                message="Signup successful",
                code="200",
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            message="Service is unavailable",
            code="503",
            request_id=request_header.requestId,
        )
    except Exception as e:
        return build_response(
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_header.requestId,
        )

@router.post("/login/")
async def login_gateway(
    request_header: RequestHeader,
    email: str,
    password: str,
):
    """
    Gateway API to forward the `login` request to the service.
    """
    try:
        payload = {"email": email, "password": password}
        response = requests.post(f"{SERVICE_BASE_URL}/login/", json=payload)
        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_header.requestId,
                message="Login successful",
                code="200",
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            message="Service is unavailable",
            code="503",
            request_id=request_header.requestId,
        )
    except Exception as e:
        return build_response(
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_header.requestId,
        )

@router.post("/token/refresh/")
async def refresh_token_gateway(
    request_header: RequestHeader,
    refresh_token: str,
):
    """
    Gateway API to forward the `refresh_token` request to the service.
    """
    try:
        payload = {"refresh_token": refresh_token}
        response = requests.post(f"{SERVICE_BASE_URL}/token/refresh/", json=payload)
        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_header.requestId,
                message="Token refresh successful",
                code="200",
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            message="Service is unavailable",
            code="503",
            request_id=request_header.requestId,
        )
    except Exception as e:
        return build_response(
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_header.requestId,
        )
