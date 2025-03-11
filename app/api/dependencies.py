from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional

from app.core.auth import verify_api_key
from app.core.logging import logger
from app.db.session import get_session
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.song_repository import SongRepository

# Header cho API key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user_id(api_key: str = Depends(api_key_header)) -> str:
    """
    Dependency để lấy ID người dùng hiện tại từ API key.

    Args:
        api_key: API key từ header request

    Returns:
        str: ID người dùng

    Raises:
        HTTPException: Nếu API key không hợp lệ
    """
    try:
        return verify_api_key(api_key)
    except HTTPException as e:
        logger.warning(f"Invalid API key attempt: {str(e)}")
        raise


async def get_user_repository() -> UserRepository:
    """
    Dependency để lấy instance của UserRepository.

    Returns:
        UserRepository: Instance của repository
    """
    return UserRepository()


async def get_song_repository() -> SongRepository:
    """
    Dependency để lấy instance của SongRepository.

    Returns:
        SongRepository: Instance của repository
    """
    return SongRepository()


async def validate_song_exists(
        song_id: str,
        song_repo: SongRepository = Depends(get_song_repository)
) -> bool:
    """
    Dependency để kiểm tra bài hát tồn tại.

    Args:
        song_id: ID bài hát cần kiểm tra
        song_repo: Instance của SongRepository

    Returns:
        bool: True nếu bài hát tồn tại

    Raises:
        HTTPException: Nếu bài hát không tồn tại
    """
    song = await song_repo.get_by_id(song_id)
    if not song:
        logger.warning(f"Attempt to access non-existent song: {song_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID {song_id} not found"
        )
    return True


async def validate_user_exists(
        user_id: str,
        user_repo: UserRepository = Depends(get_user_repository)
) -> bool:
    """
    Dependency để kiểm tra người dùng tồn tại.

    Args:
        user_id: ID người dùng cần kiểm tra
        user_repo: Instance của UserRepository

    Returns:
        bool: True nếu người dùng tồn tại

    Raises:
        HTTPException: Nếu người dùng không tồn tại
    """
    user = await user_repo.get_by_id(user_id)
    if not user:
        logger.warning(f"Attempt to access non-existent user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return True