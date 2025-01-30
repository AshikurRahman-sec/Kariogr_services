from fastapi import APIRouter, Query, Depends, HTTPException
import requests, os
from typing import Union
from fastapi.security import OAuth2PasswordRequestForm

from schemas import auth_schemas as _schemas
from utils.response_builder import build_response


AUTH_BASE_URL = os.environ.get("AUTH_BASE_URL")
#AUTH_SERVICE_BASE_URL = os.environ.get("AUTH_BASE_URL")

router = APIRouter()

@router.post(
    "/signup",
    tags=["Auth"],
    response_model=Union[_schemas.UserAuthResponse, _schemas.ErrorResponse],  # Specify the response model
)
async def signup_gateway(
    request_data: _schemas.UserAuthRequestBody,
):
    """
    Gateway API to forward the `signup` request to the corresponding microservice.
    """
    try:
        # Extract user details from the request body
        user_data = request_data.body.dict()

        # Forward the signup request to the microservice
        response = requests.post(f"{AUTH_BASE_URL}/api/signup", json=user_data)

        # Handle the microservice response
        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Signup successful",
                code="200",
            )
        else:
            return build_response(
                data = {},
                request_id=request_data.header.requestId,
                message=response.json().get("detail"),
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            data = {},
            message="Auth service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            data = {},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/login",
    tags=["Auth"],
    response_model=Union[_schemas.UserAuthLoginResponse,_schemas.ErrorResponse]  # Specify the response model
)
async def login_gateway(
    request_data: _schemas.UserAuthLoginRequestBody,
    # form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Gateway API to forward the `login` request to the corresponding microservice.
    """
    try:
        # Extract user details from the request body
        user_data = request_data.body.dict()
        # user_data = {"email": form_data.username, "password": form_data.password}

        # Forward the login request to the microservice
        response = requests.post(f"{AUTH_BASE_URL}/api/login", json=user_data)
        
    #     if response.status_code == 200:
    #             response_data = response.json()
    #             return response_data  # Return token response directly
    #     else:
    #         return {"detail": response.json().get("detail", "Login failed")}

    # except requests.exceptions.ConnectionError:
    #     raise HTTPException(status_code=503, detail="Auth service unavailable")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

        # Handle the microservice response
        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Login successful",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail"),
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            data={},
            message="Auth service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/users/generate_otp",
    tags=["Auth"],
    response_model=Union[_schemas.GenerateOtpResponse,_schemas.ErrorResponse]
)
async def send_otp_mail_gateway(
    request_data: _schemas.GenerateOtpRequestBody,
):
    """
    Gateway API to forward the `send_otp_mail` request to the corresponding microservice.
    """
    try:
        # Extract user email from the request body
        otp_data = request_data.body.dict()

        # Forward the request to the microservice
        response = requests.post(f"{AUTH_BASE_URL}/api/users/generate_otp", json=otp_data)

        # Handle the microservice response
        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="OTP sent successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            data={},
            message="Auth service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )
    
@router.post(
    "/users/verify_otp",
    tags=["Auth"],
    response_model=Union[_schemas.VerifyOtpResponse,_schemas.ErrorResponse]
)
async def verify_otp_gateway(
    request_data: _schemas.VerifyOtpRequestBody,
):
    """
    Gateway API to forward the `verify_otp` request to the corresponding microservice.
    """
    try:
        # Extract user data from the request body
        otp_data = request_data.body.dict()

        # Forward the request to the microservice
        response = requests.post(f"{AUTH_BASE_URL}/api/users/verify_otp", json=otp_data)

        # Handle the microservice response
        if response.status_code == 200:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message="OTP verified successfully",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            data={},
            message="Auth service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )
    
@router.post(
    "/firebase",
    response_model=Union[_schemas.FirebaseAuthGatewayResponse,_schemas.ErrorResponse],
    tags=["Firebase Auth"],
)
async def firebase_auth_gateway(request_data: _schemas.FirebaseAuthGatewayRequest):
    """
    Gateway API to forward the Firebase authentication request to the microservice.
    """
    try:
        # Extract request body and forward to the microservice
        firebase_data = request_data.body.dict()
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            f"{AUTH_BASE_URL}/api/auth/firebase",
            json=firebase_data,
            headers=headers,
        )

        # Handle response from the microservice
        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Firebase authentication successful",
                code="200"
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message="Error from microservice",
                code=str(response.status_code)
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            data={},
            message="Firebase authentication service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )