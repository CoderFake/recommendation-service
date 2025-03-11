from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import time

from app.db.session import get_session
from app.core.logging import logger
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Kiểm tra trạng thái hệ thống")
async def health_check(session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
    """
    Kiểm tra trạng thái hệ thống và kết nối đến cơ sở dữ liệu.

    Endpoint này trả về trạng thái hoạt động của các thành phần chính trong hệ thống,
    bao gồm cơ sở dữ liệu và các thông số hiệu suất cơ bản.

    Returns:
        Dict[str, Any]: Thông tin trạng thái của hệ thống
    """
    start_time = time.time()

    # Kiểm tra kết nối database
    db_status = "healthy"
    db_error = None
    try:
        # Kiểm tra kết nối đến DB bằng một truy vấn đơn giản
        await session.execute("SELECT 1")
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
        logger.error(f"Database health check failed: {e}")

    # Tính toán thời gian phản hồi
    response_time = time.time() - start_time

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": "1.0.0",
        "timestamp": time.time(),
        "uptime": time.time(),  # Trong triển khai thực tế, đây sẽ là thời gian process đã chạy
        "components": {
            "database": {
                "status": db_status,
                "error": db_error,
                "responseTime": response_time
            },
            "recommendation_service": {
                "status": "healthy",
                "config": {
                    "collaborative_weight": settings.COLLABORATIVE_WEIGHT,
                    "content_based_weight": settings.CONTENT_BASED_WEIGHT,
                    "real_time_sync": settings.REAL_TIME_SYNC_ENABLED
                }
            }
        }
    }


@router.get("/ping", summary="Kiểm tra kết nối đơn giản")
async def ping() -> Dict[str, str]:
    """
    Endpoint đơn giản để kiểm tra xem API có đang hoạt động không.

    Returns:
        Dict[str, str]: Thông báo "pong" nếu API hoạt động
    """
    return {"message": "pong"}