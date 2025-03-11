from typing import List, Optional, Dict, Any
import asyncio
from app.api.models import (
    SongRecommendationRequest,
    SongRecommendationResponse,
    SongRecommendation,
    RecommendationType,
    RecommendationContext
)
from app.core.config import settings
from app.core.logging import logger
from app.db.repositories.song_repository import SongRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.interaction_repository import InteractionRepository
from app.algorithms.collaborative_filtering import CollaborativeFilteringRecommender
from app.algorithms.content_based import ContentBasedRecommender
from app.algorithms.hybrid import HybridRecommender
from app.algorithms.realtime_processor import RealtimeProcessor


class RecommendationService:
    """Service xử lý gợi ý bài hát dựa trên nhiều thuật toán khác nhau"""

    def __init__(self):
        # Repositories
        self.song_repo = SongRepository()
        self.user_repo = UserRepository()
        self.interaction_repo = InteractionRepository()

        # Algorithms
        self.cf_recommender = CollaborativeFilteringRecommender()
        self.content_recommender = ContentBasedRecommender()
        self.hybrid_recommender = HybridRecommender(
            self.cf_recommender,
            self.content_recommender,
            cf_weight=settings.COLLABORATIVE_WEIGHT,
            content_weight=settings.CONTENT_BASED_WEIGHT
        )
        self.realtime_processor = RealtimeProcessor()

    async def get_recommendations(
            self,
            song_id: str,
            user_id: Optional[str] = None,
            limit: int = 10,
            context: Optional[RecommendationContext] = None
    ) -> SongRecommendationResponse:
        """
        Lấy gợi ý bài hát dựa trên bài hát gốc và ngữ cảnh.

        Args:
            song_id: ID bài hát gốc làm seed cho gợi ý
            user_id: ID người dùng cho gợi ý cá nhân hóa
            limit: Số lượng gợi ý trả về
            context: Thông tin ngữ cảnh bổ sung

        Returns:
            SongRecommendationResponse: Danh sách bài hát gợi ý và thông tin kèm theo
        """
        try:
            # Kiểm tra bài hát đầu vào tồn tại
            song = await self.song_repo.get_by_id(song_id)
            if not song:
                logger.error(f"Song with ID {song_id} not found")
                raise ValueError(f"Song with ID {song_id} not found")

            # Lấy dữ liệu theo từng phương pháp song song
            tasks = []

            # 1. Lấy gợi ý dựa trên lọc cộng tác nếu có user_id
            if user_id:
                tasks.append(self._get_collaborative_recommendations(song_id, user_id, limit))

            # 2. Lấy gợi ý dựa trên nội dung bài hát
            tasks.append(self._get_content_based_recommendations(song_id, limit))

            # 3. Lấy gợi ý dựa trên xu hướng hiện tại
            tasks.append(self._get_trending_recommendations(song_id, limit))

            # 4. Xử lý dữ liệu realtime
            tasks.append(self._get_realtime_recommendations(song_id, user_id, limit, context))

            # Chạy các tasks song song để tối ưu thời gian
            results = await asyncio.gather(*tasks)

            # Tổng hợp kết quả từ các phương pháp
            # Mỗi kết quả là một dictionary {song_id: score, ...}
            all_recommendations = {}

            # Ghép nối kết quả từ tất cả nguồn
            for result_set in results:
                if result_set:
                    for song_id, score, rec_type in result_set:
                        if song_id in all_recommendations:
                            # Nếu đã tồn tại, lấy điểm cao nhất
                            existing_score = all_recommendations[song_id]["score"]
                            if score > existing_score:
                                all_recommendations[song_id]["score"] = score
                                all_recommendations[song_id]["recommendation_type"] = rec_type
                        else:
                            all_recommendations[song_id] = {
                                "score": score,
                                "recommendation_type": rec_type
                            }

            # Sắp xếp kết quả theo điểm số và lấy top N
            sorted_recommendations = sorted(
                all_recommendations.items(),
                key=lambda x: x[1]["score"],
                reverse=True
            )[:limit]

            # Chuyển đổi thành response model
            recommendations_list = []
            song_ids_only = []

            for song_id, data in sorted_recommendations:
                song_ids_only.append(song_id)
                recommendations_list.append(
                    SongRecommendation(
                        song_id=song_id,
                        score=data["score"],
                        recommendation_type=data["recommendation_type"]
                    )
                )

            # Lấy thông tin bổ sung về lý do gợi ý
            reason = await self._generate_recommendation_reason(song_id, song_ids_only)

            return SongRecommendationResponse(
                recommended_songs=song_ids_only,
                detailed_recommendations=recommendations_list,
                based_on_song_id=song_id,
                recommendation_reason=reason
            )

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise

    async def _get_collaborative_recommendations(
            self,
            song_id: str,
            user_id: str,
            limit: int
    ) -> List[tuple]:
        """
        Lấy gợi ý dựa trên lọc cộng tác (hành vi của người dùng khác).

        Args:
            song_id: ID bài hát gốc
            user_id: ID người dùng
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[tuple]: Danh sách (song_id, score, recommendation_type)
        """
        logger.info(f"Getting collaborative recommendations for user {user_id}, song {song_id}")

        try:
            # Lấy lịch sử tương tác của người dùng
            user_interactions = await self.interaction_repo.get_user_interactions(user_id)

            # Chạy thuật toán lọc cộng tác
            recommendations = await self.cf_recommender.recommend(
                song_id=song_id,
                user_id=user_id,
                user_interactions=user_interactions,
                limit=limit
            )

            # Chuyển đổi format kết quả
            result = [
                (rec_song_id, score, RecommendationType.COLLABORATIVE)
                for rec_song_id, score in recommendations
            ]

            return result
        except Exception as e:
            logger.error(f"Error in collaborative recommendations: {str(e)}")
            return []

    async def _get_content_based_recommendations(
            self,
            song_id: str,
            limit: int
    ) -> List[tuple]:
        """
        Lấy gợi ý dựa trên nội dung (thể loại, nghệ sĩ, đặc điểm âm nhạc).

        Args:
            song_id: ID bài hát gốc
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[tuple]: Danh sách (song_id, score, recommendation_type)
        """
        logger.info(f"Getting content-based recommendations for song {song_id}")

        try:
            # Lấy thông tin chi tiết về bài hát
            song_details = await self.song_repo.get_with_details(song_id)

            # Chạy thuật toán gợi ý theo nội dung
            recommendations = await self.content_recommender.recommend(
                song_id=song_id,
                song_details=song_details,
                limit=limit
            )

            # Chuyển đổi format kết quả
            result = [
                (rec_song_id, score, RecommendationType.CONTENT_BASED)
                for rec_song_id, score in recommendations
            ]

            return result
        except Exception as e:
            logger.error(f"Error in content-based recommendations: {str(e)}")
            return []

    async def _get_trending_recommendations(
            self,
            song_id: str,
            limit: int
    ) -> List[tuple]:
        """
        Lấy gợi ý dựa trên xu hướng hiện tại (bài hát đang hot).

        Args:
            song_id: ID bài hát gốc (để loại trừ)
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[tuple]: Danh sách (song_id, score, recommendation_type)
        """
        logger.info(f"Getting trending recommendations excluding song {song_id}")

        try:
            # Lấy danh sách bài hát đang trending
            trending_songs = await self.interaction_repo.get_trending_songs(limit=limit * 2)

            # Loại bỏ bài hát gốc nếu có trong danh sách
            trending_songs = [
                                 (s_id, score) for s_id, score in trending_songs if s_id != song_id
                             ][:limit]

            # Chuyển đổi format kết quả
            result = [
                (rec_song_id, score, RecommendationType.TRENDING)
                for rec_song_id, score in trending_songs
            ]

            return result
        except Exception as e:
            logger.error(f"Error in trending recommendations: {str(e)}")
            return []

    async def _get_realtime_recommendations(
            self,
            song_id: str,
            user_id: Optional[str],
            limit: int,
            context: Optional[RecommendationContext]
    ) -> List[tuple]:
        """
        Lấy gợi ý dựa trên dữ liệu realtime.

        Args:
            song_id: ID bài hát gốc
            user_id: ID người dùng
            limit: Số lượng gợi ý cần lấy
            context: Thông tin ngữ cảnh

        Returns:
            List[tuple]: Danh sách (song_id, score, recommendation_type)
        """
        logger.info(f"Getting realtime recommendations for song {song_id}")

        try:
            if not context:
                return []

            # Xử lý dữ liệu realtime
            realtime_recommendations = await self.realtime_processor.process(
                song_id=song_id,
                user_id=user_id,
                context=context,
                limit=limit
            )

            # Tăng cường điểm số lên để ưu tiên gợi ý realtime
            result = [
                (rec_song_id, score * settings.REAL_TIME_BOOST_FACTOR, RecommendationType.REAL_TIME)
                for rec_song_id, score in realtime_recommendations
            ]

            return result
        except Exception as e:
            logger.error(f"Error in realtime recommendations: {str(e)}")
            return []

    async def _generate_recommendation_reason(
            self,
            seed_song_id: str,
            recommended_song_ids: List[str]
    ) -> str:
        """
        Tạo lý do gợi ý để giải thích kết quả cho người dùng.

        Args:
            seed_song_id: ID bài hát gốc
            recommended_song_ids: Danh sách ID bài hát được gợi ý

        Returns:
            str: Lý do gợi ý
        """
        try:
            if not recommended_song_ids:
                return "Không có bài hát phù hợp để gợi ý."

            # Lấy thông tin bài hát gốc
            seed_song = await self.song_repo.get_by_id(seed_song_id)

            # Lấy chung thể loại, nghệ sĩ giữa bài hát gốc và gợi ý
            common_genres = await self.song_repo.get_common_genres(seed_song_id, recommended_song_ids)
            common_artists = await self.song_repo.get_common_artists(seed_song_id, recommended_song_ids)

            # Tạo lý do dựa trên thông tin đã thu thập
            reason_parts = []

            if common_genres:
                genres_str = ", ".join(common_genres[:3])  # Lấy tối đa 3 thể loại
                reason_parts.append(f"thể loại tương tự ({genres_str})")

            if common_artists:
                artists_str = ", ".join(common_artists[:2])  # Lấy tối đa 2 nghệ sĩ
                reason_parts.append(f"cùng nghệ sĩ hoặc nghệ sĩ tương tự ({artists_str})")

            reason_parts.append("mẫu nghe của người dùng khác")

            if len(reason_parts) > 1:
                reason = f"Dựa trên {', '.join(reason_parts[:-1])} và {reason_parts[-1]}."
            else:
                reason = f"Dựa trên {reason_parts[0]}."

            return reason
        except Exception as e:
            logger.error(f"Error generating recommendation reason: {str(e)}")
            return "Các bài hát phù hợp với sở thích của bạn."