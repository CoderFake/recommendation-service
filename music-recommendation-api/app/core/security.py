from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.firebase import firebase_client

security = HTTPBearer()


class FirebaseError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 401):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"{code}: {message}")


def get_auth_exceptions() -> Dict[str, HTTPException]:
    return {
        "token_missing": HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing",
            headers={"WWW-Authenticate": "Bearer"},
        ),
        "token_invalid": HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ),
        "token_expired": HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token expired",
            headers={"WWW-Authenticate": "Bearer"},
        ),
        "permission_denied": HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        ),
    }


async def get_current_user_data(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    exceptions = get_auth_exceptions()

    token = credentials.credentials
    if not token:
        raise exceptions["token_missing"]

    try:
        decoded_token = await firebase_client.verify_token(token)
        return decoded_token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )