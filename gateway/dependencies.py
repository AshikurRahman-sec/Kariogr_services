import requests
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
import os

# Environment variables or settings file should store these
AUTH_SERVICE_BASE_URL = os.environ.get("AUTH_BASE_URL")  # Change to your actual auth service URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/gateway/login")

def verify_token(token: str = Security(oauth2_scheme)):
    """
    Verifies the token by calling the external Auth Service.
    Returns the user_id if valid, otherwise raises HTTPException.
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{AUTH_SERVICE_BASE_URL}/api/token/verify",
            headers=headers  # Send token in Authorization header
        )

        if response.status_code == 200:
            return response.json()  # Expected response: {"user_id": "<user-id>"}

        elif response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        else:
            raise HTTPException(status_code=500, detail="Auth service error")

    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Auth service unavailable")
