from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from datetime import datetime, timedelta
import pandas as pd

from app.api.models import RecommendationContext, ContextType
from app.core.logging import logger
from app.core.config import settings
from app.db.repositories.interaction_repository import InteractionRepository
from app.db.repositories.song_repository import SongRepository


class RealtimeProcessor:
    """
    Xử lý dữ liệu realtime để cải thiện gợi ý.

    Phân tích ngữ cảnh và dữ liệu realtime để điều chỉnh điểm số gợi ý
    dựa trên các yếu tố thời gian thực như thời điểm trong ngày, thiết bị,
    và xu hướng hiện tại.
    """

    def __init__(self):
        self.interaction_repo = InteractionRepository()
        self.song_repo = SongRepository()
        self.time_window = timedelta(hours=6)  # Cửa sổ thời gian để lấy dữ liệu realtime
        self.context_boost = {
            # Tăng cường theo từng loại ngữ cảnh
            ContextType.MORNING: {"energy": 1.3, "positive": 1.2},
            ContextType.AFTERNOON: {"energy": 1.1, "tempo": 1.1},
            ContextType.EVENING: {"acoustic": 1.2, "chill": 1.3},
            ContextType.NIGHT: {"acoustic": 1.4, "chill": 1.5},
            ContextType.WORKOUT: {"energy": 1.5, "tempo": 1.4, "danceability": 1.3},
            ContextType.STUDY: {"acoustic": 1.4, "instrumental": 1.5},
            ContextType.RELAX: {"acoustic": 1.3, "chill": 1.4, "instrumental": 1.2},
            ContextType.PARTY: {"energy": 1.4, "danceability": 1.5, "popular": 1.3}
        }
        self.device_boost = {
            # Tăng cường theo thiết bị
            "mobile": {"short_duration": 1.2},
            "desktop": {},
            "tablet": {},
            "speaker": {"acoustic": 1.2, "quality": 1.3},
            "tv": {"popular": 1.2},
            "other": {}
        }

    async def process(
            self,
            song_id: str,
            user_id: Optional[str],
            context: RecommendationContext,
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Xử lý dữ liệu realtime và ngữ cảnh để tạo gợi ý.

        Args:
            song_id: ID bài hát gốc
            user_id: ID người dùng (nếu có)
            context: Thông tin ngữ cảnh
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số) được gợi ý
        """
        try:
            # Lấy dữ liệu realtime
            current_time = datetime.now()
            since_time = current_time - self.time_window

            # Kết hợp nhiều nguồn dữ liệu realtime
            realtime_scores = {}

            # 1. Lấy các bài hát được nghe nhiều trong khung giờ hiện tại
            time_context = self._get_time_context(current_time)
            time_based_songs = await self._get_trending_by_time(time_context, limit * 2)

            # 2. Lấy bài hát phù hợp với mood/context
            context_based_songs = await self._get_context_recommendations(context, song_id, limit * 2)

            # 3. Lấy bài hát phù hợp với lịch sử gần đây của người dùng (nếu có)
            user_recent_songs = []
            if user_id:
                user_recent_songs = await self._get_user_recent_recommendations(
                    user_id, song_id, since_time, limit * 2
                )

            # Kết hợp các nguồn dữ liệu, ưu tiên theo thứ tự:
            # 1. Bài hát phù hợp ngữ cảnh + người dùng
            # 2. Bài hát phù hợp ngữ cảnh
            # 3. Bài hát phổ biến trong khung giờ
            all_sources = [
                (user_recent_songs, 1.3),  # Hệ số 1.3
                (context_based_songs, 1.2),  # Hệ số 1.2
                (time_based_songs, 1.0)  # Hệ số 1.0
            ]

            # Thêm tất cả các nguồn vào realtime_scores với hệ số tương ứng
            for source, weight in all_sources:
                for s_id, score in source:
                    if s_id in realtime_scores:
                        # Lấy điểm cao nhất giữa các nguồn * hệ số
                        realtime_scores[s_id] = max(realtime_scores[s_id], score * weight)
                    else:
                        realtime_scores[s_id] = score * weight

            # Loại bỏ bài hát gốc
            if song_id in realtime_scores:
                del realtime_scores[song_id]

            # Sắp xếp và lấy top N
            sorted_scores = sorted(
                [(s_id, score) for s_id, score in realtime_scores.items()],
                key=lambda x: x[1],
                reverse=True
            )[:limit]

            return sorted_scores

        except Exception as e:
            logger.error(f"Error in realtime processing: {str(e)}")
            return []

    def _get_time_context(self, current_time: datetime) -> ContextType:
        """
        Xác định ngữ cảnh thời gian dựa trên giờ hiện tại.

        Args:
            current_time: Thời gian hiện tại

        Returns:
            ContextType: Loại ngữ cảnh thời gian
        """
        hour = current_time.hour

        if 5 <= hour < 12:
            return ContextType.MORNING
        elif 12 <= hour < 17:
            return ContextType.AFTERNOON
        elif 17 <= hour < 22:
            return ContextType.EVENING
        else:
            return ContextType.NIGHT

    async def _get_trending_by_time(
            self,
            time_context: ContextType,
            limit: int
    ) -> List[Tuple[str, float]]:
        """
        Lấy các bài hát xu hướng theo khung giờ.

        Args:
            time_context: Loại ngữ cảnh thời gian
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số)
        """
        try:
            # Lấy xu hướng từ repository
            trending_songs = await self.interaction_repo.get_trending_by_time_context(
                time_context, limit
            )

            return trending_songs
        except Exception as e:
            logger.error(f"Error getting time-based trending: {str(e)}")
            return []

    async def _get_context_recommendations(
            self,
            context: RecommendationContext,
            seed_song_id: str,
            limit: int
    ) -> List[Tuple[str, float]]:
        """
        Lấy gợi ý dựa trên ngữ cảnh hiện tại.

        Args:
            context: Thông tin ngữ cảnh
            seed_song_id: ID bài hát gốc
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số)
        """
        try:
            # Nếu không có context, trả về list trống
            if not context:
                return []

            # Lấy các đặc trưng từ bài hát gốc
            seed_features = await self.song_repo.get_audio_features(seed_song_id)
            if not seed_features:
                return []

            # Áp dụng tăng cường theo ngữ cảnh
            feature_boosts = {}

            # Tăng cường theo time_of_day
            if context.time_of_day and context.time_of_day in self.context_boost:
                for feature, boost in self.context_boost[context.time_of_day].items():
                    feature_boosts[feature] = boost

            # Tăng cường theo thiết bị
            if context.device and context.device in self.device_boost:
                for feature, boost in self.device_boost[context.device].items():
                    if feature in feature_boosts:
                        feature_boosts[feature] *= boost
                    else:
                        feature_boosts[feature] = boost

            # Lấy bài hát tương tự từ repository với bộ tăng cường
            similar_songs = await self.song_repo.get_songs_by_feature_similarity(
                seed_features, feature_boosts, limit
            )

            return similar_songs
        except Exception as e:
            logger.error(f"Error getting context recommendations: {str(e)}")
            return []

    async def _get_user_recent_recommendations(
            self,
            user_id: str,
            seed_song_id: str,
            since_time: datetime,
            limit: int
    ) -> List[Tuple[str, float]]:
        """
        Lấy gợi ý dựa trên hoạt động gần đây của người dùng.

        Args:
            user_id: ID người dùng
            seed_song_id: ID bài hát gốc
            since_time: Thời điểm bắt đầu xem xét
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số)
        """
        try:
            # Lấy các bài hát người dùng đã tương tác gần đây
            recent_interactions = await self.interaction_repo.get_user_recent_interactions(
                user_id, since_time
            )

            # Nếu không có tương tác gần đây, trả về list trống
            if not recent_interactions:
                return []

            # Lấy thông tin về các thể loại, nghệ sĩ người dùng thích gần đây
            recent_genres = set()
            recent_artists = set()

            for interaction in recent_interactions:
                if "genre" in interaction and interaction["genre"]:
                    recent_genres.add(interaction["genre"])
                if "artist_id" in interaction and interaction["artist_id"]:
                    recent_artists.add(interaction["artist_id"])

            # Lấy bài hát tương tự dựa trên thể loại và nghệ sĩ gần đây
            similar_songs = await self.song_repo.get_songs_by_genres_artists(
                list(recent_genres), list(recent_artists), seed_song_id, limit
            )

            return similar_songs
        except Exception as e:
            logger.error(f"Error getting user recent recommendations: {str(e)}")
            return []