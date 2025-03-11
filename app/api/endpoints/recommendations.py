from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from app.api.models import (
    SongRecommendationRequest,
    SongRecommendationResponse,
    TokenRequest,
    TokenResponse
)
from app.core.auth import verify_api_key, create_access_token
from app.services.recommendation_service import RecommendationService
from app.services.user_interaction_service import record_recommendation_request
from app.core.logging import logger

router = APIRouter(tags=["recommendations"])

# Tạo instance của service
recommendation_service = RecommendationService()


@router.post("/recommendations", response_model=SongRecommendationResponse)
async def get_song_recommendations(
        request: SongRecommendationRequest,
        authenticated_user_id: str = Depends(verify_api_key)
):
    """
    Lấy gợi ý bài hát dựa trên bài hát đầu vào và ngữ cảnh.

    - **song_id**: ID bài hát gốc để gợi ý
    - **user_id**: ID người dùng để cá nhân hóa (nếu không cung cấp sẽ dùng ID từ token)
    - **limit**: Số lượng bài hát gợi ý trả về (mặc định là 10)
    - **context**: Thông tin ngữ cảnh bổ sung để cải thiện gợi ý

    Trả về danh sách ID bài hát được gợi ý kèm thông tin chi tiết.
    """
    try:
        # Kiểm tra và sử dụng user_id từ token nếu không có trong request
        if not request.user_id:
            request.user_id = authenticated_user_id
        elif request.user_id != authenticated_user_id:
            # Nếu user_id trong request khác với token, ghi log cảnh báo
            # Trong trường hợp thực tế, có thể giới hạn truy cập hoặc kiểm tra quyền
            logger.warning(
                f"User ID mismatch: {request.user_id} in request vs {authenticated_user_id} in token"
            )

        # Ghi nhận yêu cầu gợi ý vào logs/db
        await record_recommendation_request(request)

        # Lấy gợi ý từ service
        recommendations = await recommendation_service.get_recommendations(
            song_id=request.song_id,
            user_id=request.user_id,
            limit=request.limit,
            context=request.context
        )

        return recommendations
    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    """
    Tạo token truy cập API.

    - **user_id**: ID người dùng cần tạo token

    Trả về token và thời gian hết hạn.

    Lưu ý: Trong môi trường thực tế, endpoint này nên được bảo vệ
    và chỉ cho phép các service nội bộ truy cập.
    """
    try:
        access_token = create_access_token(request.user_id)
        # Phân tích token để lấy timestamp hết hạn
        parts = access_token.split(":")
        timestamp = int(parts[1])
        expires_at = timestamp + (30 * 60)  # 30 phút

        return TokenResponse(
            access_token=access_token,
            expires_at=expires_at
        )
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate token: {str(e)}"
        )