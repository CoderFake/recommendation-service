from typing import AsyncGenerator, Dict, Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_current_user_data
from app.core.firebase import firebase_client
from app.db.session import get_db
from app.models.user import User
from app.services.spotify import SpotifyClient
from app.services.recommender import RecommenderService

security = HTTPBearer()


async def get_current_user(
        firebase_data: Dict[str, Any] = Depends(get_current_user_data),
        db: AsyncSession = Depends(get_db)
) -> User:
    firebase_uid = firebase_data.get("uid")

    stmt = select(User).where(User.firebase_uid == firebase_uid)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    return current_user


async def get_firebase_user(
        firebase_data: Dict[str, Any] = Depends(get_current_user_data)
) -> Dict[str, Any]:
    try:
        user_info = await firebase_client.get_user(firebase_data["uid"])
        return user_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user information: {str(e)}"
        )


async def get_spotify_client() -> SpotifyClient:
    from app.services.spotify import SpotifyClient
    return SpotifyClient()


async def get_recommender_service(db: AsyncSession = Depends(get_db)) -> RecommenderService:
    from app.services.recommender import RecommenderService
    return RecommenderService(db)