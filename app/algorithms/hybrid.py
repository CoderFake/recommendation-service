from typing import List, Dict, Tuple, Optional, Any
import numpy as np

from app.core.logging import logger
from app.algorithms.collaborative_filtering import CollaborativeFilteringRecommender
from app.algorithms.content_based import ContentBasedRecommender


class HybridRecommender:
    """
    Kết hợp nhiều phương pháp gợi ý với trọng số.

    Hybrid recommender kết hợp kết quả từ phương pháp lọc cộng tác
    và gợi ý dựa trên nội dung để tạo ra gợi ý tốt hơn.
    """

    def __init__(
            self,
            cf_recommender: CollaborativeFilteringRecommender,
            content_recommender: ContentBasedRecommender,
            cf_weight: float = 0.7,
            content_weight: float = 0.3
    ):
        """
        Khởi tạo hybrid recommender.

        Args:
            cf_recommender: Instance của CollaborativeFilteringRecommender
            content_recommender: Instance của ContentBasedRecommender
            cf_weight: Trọng số cho kết quả lọc cộng tác (0-1)
            content_weight: Trọng số cho kết quả content-based (0-1)
        """
        self.cf_recommender = cf_recommender
        self.content_recommender = content_recommender

        # Chuẩn hóa trọng số để tổng = 1
        total_weight = cf_weight + content_weight
        self.cf_weight = cf_weight / total_weight
        self.content_weight = content_weight / total_weight

    async def recommend(
            self,
            song_id: str,
            user_id: Optional[str] = None,
            song_details: Optional[Dict] = None,
            user_interactions: Optional[List[Dict]] = None,
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Đưa ra gợi ý kết hợp từ nhiều nguồn.

        Args:
            song_id: ID bài hát gốc
            user_id: ID người dùng (nếu có)
            song_details: Thông tin chi tiết về bài hát (nếu có)
            user_interactions: Dữ liệu tương tác của người dùng (nếu có)
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số) được gợi ý
        """
        try:
            # Kết quả của từng phương pháp
            cf_recommendations = []
            content_recommendations = []

            # Lấy gợi ý từ lọc cộng tác nếu có user_id
            if user_id:
                cf_recommendations = await self.cf_recommender.recommend(
                    song_id=song_id,
                    user_id=user_id,
                    user_interactions=user_interactions,
                    limit=limit * 2  # Lấy nhiều hơn để có không gian kết hợp
                )

            # Lấy gợi ý từ content-based
            content_recommendations = await self.content_recommender.recommend(
                song_id=song_id,
                song_details=song_details,
                limit=limit * 2  # Lấy nhiều hơn để có không gian kết hợp
            )

            # Kết hợp kết quả với trọng số
            return await self._combine_recommendations(
                cf_recommendations,
                content_recommendations,
                limit
            )

        except Exception as e:
            logger.error(f"Error in hybrid recommendation: {str(e)}")

            # Nếu có lỗi, thử lấy ít nhất một nguồn gợi ý nào đó
            if user_id:
                try:
                    return await self.cf_recommender.recommend(
                        song_id=song_id,
                        user_id=user_id,
                        user_interactions=user_interactions,
                        limit=limit
                    )
                except:
                    pass

            try:
                return await self.content_recommender.recommend(
                    song_id=song_id,
                    song_details=song_details,
                    limit=limit
                )
            except:
                return []

    async def _combine_recommendations(
            self,
            cf_recommendations: List[Tuple[str, float]],
            content_recommendations: List[Tuple[str, float]],
            limit: int
    ) -> List[Tuple[str, float]]:
        """
        Kết hợp kết quả gợi ý từ nhiều nguồn với trọng số.

        Args:
            cf_recommendations: Gợi ý từ phương pháp lọc cộng tác
            content_recommendations: Gợi ý từ phương pháp content-based
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số) kết hợp
        """
        try:
            # Chuyển danh sách thành dictionary để dễ xử lý
            cf_dict = {song_id: score for song_id, score in cf_recommendations}
            content_dict = {song_id: score for song_id, score in content_recommendations}

            # Tập hợp tất cả song_id từ cả hai nguồn
            all_song_ids = set(cf_dict.keys()).union(set(content_dict.keys()))

            # Tính điểm kết hợp cho mỗi bài hát
            combined_scores = {}
            for song_id in all_song_ids:
                cf_score = cf_dict.get(song_id, 0) * self.cf_weight
                content_score = content_dict.get(song_id, 0) * self.content_weight

                # Nếu bài hát xuất hiện trong cả hai phương pháp, tăng cường điểm số
                if song_id in cf_dict and song_id in content_dict:
                    # Sử dụng công thức kết hợp có tăng cường
                    combined_scores[song_id] = (cf_score + content_score) * 1.1
                else:
                    # Sử dụng công thức kết hợp thông thường
                    combined_scores[song_id] = cf_score + content_score

            # Sắp xếp và lấy top N
            sorted_recommendations = sorted(
                [(song_id, score) for song_id, score in combined_scores.items()],
                key=lambda x: x[1],
                reverse=True
            )[:limit]

            return sorted_recommendations

        except Exception as e:
            logger.error(f"Error combining recommendations: {str(e)}")

            # Nếu có lỗi khi kết hợp, trả về một trong hai nguồn theo ưu tiên
            if cf_recommendations:
                return cf_recommendations[:limit]
            else:
                return content_recommendations[:limit]