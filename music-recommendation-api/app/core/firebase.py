import json
import logging
from typing import Dict, Any, Optional

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class FirebaseClient:

    def __init__(self):
        self.app = None
        self.initialized = False
        self._initialize_firebase()

    def _initialize_firebase(self):
        try:
            if settings.FIREBASE_AUTH_ENABLED:
                if settings.FIREBASE_SERVICE_ACCOUNT_KEY:
                    try:
                        cred_dict = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_KEY)
                        cred = credentials.Certificate(cred_dict)
                    except json.JSONDecodeError:
                        logger.error("Invalid Firebase service account key JSON")
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Firebase initialization error: Invalid service account key"
                        )
                else:
                    cred = credentials.Certificate({
                        "type": "service_account",
                        "project_id": settings.FIREBASE_PROJECT_ID,
                        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                        "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
                        "client_email": settings.FIREBASE_CLIENT_EMAIL,
                        "client_id": settings.FIREBASE_CLIENT_ID,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": settings.FIREBASE_CLIENT_CERT_URL
                    })

                self.app = firebase_admin.initialize_app(cred)
                self.initialized = True
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                logger.info("Firebase authentication is disabled")
        except Exception as e:
            logger.error(f"Firebase initialization error: {str(e)}")

    async def verify_token(self, id_token: str) -> Dict[str, Any]:

        if not self.initialized:
            logger.error("Firebase not initialized, cannot verify token")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase authentication not configured"
            )

        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except auth.ExpiredIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except auth.InvalidIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except auth.RevokedIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )

    async def get_user(self, uid: str) -> Dict[str, Any]:
        if not self.initialized:
            logger.error("Firebase not initialized, cannot get user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase authentication not configured"
            )

        try:
            user = auth.get_user(uid)
            return {
                "uid": user.uid,
                "email": user.email,
                "email_verified": user.email_verified,
                "display_name": user.display_name,
                "photo_url": user.photo_url,
                "disabled": user.disabled,
                "provider_data": [
                    {"provider_id": p.provider_id, "uid": p.uid}
                    for p in user.provider_data
                ]
            }
        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {uid} not found"
            )
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user: {str(e)}"
            )


# Create a global instance
firebase_client = FirebaseClient()