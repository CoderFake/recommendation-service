from typing import Dict, Any, Optional
import json
from datetime import datetime

from app.api.models import SongRecommendationRequest, DeviceType, ContextType
from app.db.repositories.interaction_repository import InteractionRepository
from app.db.models import InteractionType, TimeContext
from app.core.logging import logger
from app.core.config import settings


async def record_recommendation_request(request: SongRecommendationRequest) -> bool:
    """
    Ghi nhận yêu cầu gợi ý để phân tích và cải thiện thuật toán.

    Args:
        request: Thông tin yêu cầu gợi ý

    Returns:
        bool: True nếu ghi nhận thành công, False nếu có lỗi
    """
    try:
        from app.db.models import RecommendationRequest
        from app.db.session import get_session

        # Chuyển đổi context sang JSON
        context_json = None
        if request.context:
            context_dict = request.context.dict(exclude_none=True)
            context_json = json.dumps(context_dict)

        # Xác định device_type và time_context nếu có
        device_type = None
        time_context = None

        if request.context:
            if request.context.device:
                device_type = request.context.device.value

            if request.context.time_of_day:
                time_context = request.context.time_of_day.value

        # Tạo bản ghi mới
        recommendation_request = RecommendationRequest(
            user_id=request.user_id,
            song_id=request.song_id,
            device_type=device_type,
            time_context=time_context,
            request_json=context_json,
            created_at=datetime.utcnow()
        )

        # Lưu vào database
        async with get_session() as session:
            session.add(recommendation_request)
            await session.commit()

        logger.info(f"Recorded recommendation request for user {request.user_id}, song {request.song_id}")
        return True

    except Exception as e:
        logger.error(f"Error recording recommendation request: {str(e)}")
        return False


async def record_recommendation_result(
        request_id: int,
        recommended_songs: Dict[str, Any],
        algorithm_type: str
) -> bool:
    """
    Ghi nhận kết quả gợi ý để phân tích và cải thiện thuật toán.

    Args:
        request_id: ID của yêu cầu gợi ý
        recommended_songs: Danh sách bài hát được gợi ý với điểm số
        algorithm_type: Loại thuật toán sử dụng

    Returns:
        bool: True nếu ghi nhận thành công, False nếu có lỗi
    """
    try:
        from app.db.models import RecommendationResult
        from app.db.session import get_session

        # Tạo danh sách bản ghi
        recommendation_results = []
        for rank, (song_id, score) in enumerate(recommended_songs):
            result = RecommendationResult(
                request_id=request_id,
                song_id=song_id,
                score=score,
                algorithm_type=algorithm_type,
                rank_position=rank,
                created_at=datetime.utcnow()
            )
            recommendation_results.append(result)

        # Lưu vào database
        async with get_session() as session:
            session.add_all(recommendation_results)
            await session.commit()

        logger.info(f"Recorded {len(recommendation_results)} recommendation results for request {request_id}")
        return True

    except Exception as e:
        logger.error(f"Error recording recommendation results: {str(e)}")
        return False


async def record_user_song_interaction(
        user_id: str,
        song_id: str,
        interaction_type: str,
        device_type: Optional[str] = None,
        context: Optional[Dict] = None,
        play_duration: Optional[int] = None
) -> bool:
    """
    Ghi nhận tương tác của người dùng với bài hát.

    Args:
        user_id: ID người dùng
        song_id: ID bài hát
        interaction_type: Loại tương tác (play, like, skip, ...)
        device_type: Loại thiết bị
        context: Thông tin ngữ cảnh bổ sung
        play_duration: Thời gian phát (giây)

    Returns:
        bool: True nếu ghi nhận thành công, False nếu có lỗi
    """
    try:
        repo = InteractionRepository()

        # Chuyển đổi interaction_type sang enum
        interaction_enum = None
        try:
            interaction_enum = InteractionType(interaction_type)
        except ValueError:
            interaction_enum = InteractionType.PLAY

        # Xác định các thông số
        play_count = 1 if interaction_enum == InteractionType.PLAY else 0
        liked = True if interaction_enum == InteractionType.LIKE else False

        # Xác định time_context
        time_context = None
        if context and 'time_of_day' in context:
            try:
                time_context = TimeContext(context['time_of_day'])
            except ValueError:
                time_context = None

        # Ghi nhận tương tác
        success = await repo.record_user_interaction(
            user_id=user_id,
            song_id=song_id,
            interaction_type=interaction_enum,
            play_count=play_count,
            play_duration=play_duration or 0,
            liked=liked,
            device_type=device_type,
            time_context=time_context,
            location=context.get('location') if context else None
        )

        if success:
            logger.info(f"Recorded {interaction_type} interaction for user {user_id}, song {song_id}")

        return success

    except Exception as e:
        logger.error(f"Error recording user song interaction: {str(e)}")
        return False