from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.sql.expression import text
from datetime import datetime, timedelta

from app.db.models import UserInteraction, Song, User, Artist, Genre, DeviceType, TimeContext, InteractionType
from app.db.session import get_session
from app.core.logging import logger


class InteractionRepository:
    """Repository cho truy vấn và quản lý tương tác người dùng"""

    async def get_user_interactions(self, user_id: str) -> List[Dict]:
        """
        Lấy tất cả tương tác của người dùng.

        Args:
            user_id: ID người dùng

        Returns:
            List[Dict]: Danh sách tương tác của người dùng
        """
        try:
            async with get_session() as session:
                query = select(
                    UserInteraction.song_id,
                    UserInteraction.interaction_type,
                    UserInteraction.play_count,
                    UserInteraction.play_duration,
                    UserInteraction.liked,
                    UserInteraction.created_at,
                    UserInteraction.updated_at,
                    Song.artist_id,
                    Song.genre_id
                ).join(
                    Song, UserInteraction.song_id == Song.id
                ).where(
                    UserInteraction.user_id == user_id
                )

                result = await session.execute(query)

                interactions = []
                for row in result:
                    interactions.append({
                        "song_id": row[0],
                        "interaction_type": row[1].value if row[1] else None,
                        "play_count": row[2],
                        "play_duration": row[3],
                        "liked": row[4],
                        "created_at": row[5],
                        "updated_at": row[6],
                        "artist_id": row[7],
                        "genre_id": row[8]
                    })

                return interactions

        except Exception as e:
            logger.error(f"Error getting user interactions: {str(e)}")
            return []

    async def get_user_recent_interactions(
            self,
            user_id: str,
            since_time: datetime
    ) -> List[Dict]:
        """
        Lấy tương tác gần đây của người dùng.

        Args:
            user_id: ID người dùng
            since_time: Thời điểm bắt đầu xem xét

        Returns:
            List[Dict]: Danh sách tương tác gần đây
        """
        try:
            async with get_session() as session:
                query = select(
                    UserInteraction.song_id,
                    UserInteraction.interaction_type,
                    UserInteraction.play_count,
                    UserInteraction.liked,
                    UserInteraction.created_at,
                    Song.artist_id,
                    Song.genre_id,
                    Artist.name.label("artist_name"),
                    Genre.name.label("genre_name")
                ).join(
                    Song, UserInteraction.song_id == Song.id
                ).outerjoin(
                    Artist, Song.artist_id == Artist.id
                ).outerjoin(
                    Genre, Song.genre_id == Genre.id
                ).where(
                    UserInteraction.user_id == user_id,
                    UserInteraction.created_at >= since_time
                ).order_by(
                    desc(UserInteraction.created_at)
                )

                result = await session.execute(query)

                recent_interactions = []
                for row in result:
                    recent_interactions.append({
                        "song_id": row[0],
                        "interaction_type": row[1].value if row[1] else None,
                        "play_count": row[2],
                        "liked": row[3],
                        "timestamp": row[4],
                        "artist_id": row[5],
                        "genre_id": row[6],
                        "artist_name": row[7],
                        "genre_name": row[8]
                    })

                return recent_interactions

        except Exception as e:
            logger.error(f"Error getting user recent interactions: {str(e)}")
            return []

    async def get_trending_songs(self, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Lấy danh sách bài hát đang trending.

        Args:
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, score)
        """
        try:
            # Lấy ngày hiện tại
            now = datetime.now()
            week_ago = now - timedelta(days=7)

            async with get_session() as session:
                # Query bài hát trending trong 7 ngày qua
                query = text("""
                    SELECT 
                        s.id, 
                        COUNT(DISTINCT ui.user_id) * 0.7 + SUM(ui.play_count) * 0.2 + SUM(CASE WHEN ui.liked THEN 1 ELSE 0 END) * 0.1 AS trend_score
                    FROM user_interactions ui
                    JOIN songs s ON ui.song_id = s.id
                    WHERE ui.created_at >= :week_ago
                    GROUP BY s.id
                    ORDER BY trend_score DESC
                    LIMIT :limit
                """)

                result = await session.execute(query, {"week_ago": week_ago, "limit": limit})

                trending_songs = [(row[0], float(row[1])) for row in result]

                # Chuẩn hóa điểm số về khoảng [0, 1]
                if trending_songs:
                    max_score = max([score for _, score in trending_songs])
                    if max_score > 0:
                        trending_songs = [(s_id, min(1.0, score / max_score)) for s_id, score in trending_songs]

                return trending_songs

        except Exception as e:
            logger.error(f"Error getting trending songs: {str(e)}")
            return []

    async def get_trending_by_time_context(
            self,
            time_context: str,
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Lấy danh sách bài hát trending theo ngữ cảnh thời gian.

        Args:
            time_context: Ngữ cảnh thời gian (morning, afternoon, evening, night)
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, score)
        """
        try:
            # Lấy ngày hiện tại
            now = datetime.now()
            month_ago = now - timedelta(days=30)

            async with get_session() as session:
                # Query bài hát trending trong ngữ cảnh thời gian cụ thể
                query = text("""
                    SELECT 
                        s.id, 
                        COUNT(DISTINCT ui.user_id) * 0.5 + SUM(ui.play_count) * 0.5 AS trend_score
                    FROM user_interactions ui
                    JOIN songs s ON ui.song_id = s.id
                    WHERE ui.created_at >= :month_ago
                    AND ui.time_context = :time_context
                    GROUP BY s.id
                    ORDER BY trend_score DESC
                    LIMIT :limit
                """)

                result = await session.execute(
                    query,
                    {
                        "month_ago": month_ago,
                        "time_context": time_context,
                        "limit": limit
                    }
                )

                trending_songs = [(row[0], float(row[1])) for row in result]

                # Chuẩn hóa điểm số về khoảng [0, 1]
                if trending_songs:
                    max_score = max([score for _, score in trending_songs])
                    if max_score > 0:
                        trending_songs = [(s_id, min(1.0, score / max_score)) for s_id, score in trending_songs]

                return trending_songs

        except Exception as e:
            logger.error(f"Error getting trending songs by time context: {str(e)}")
            return []

    async def record_user_interaction(
            self,
            user_id: str,
            song_id: str,
            interaction_type: InteractionType,
            play_count: int = 0,
            play_duration: int = 0,
            liked: bool = False,
            device_type: Optional[str] = None,
            time_context: Optional[TimeContext] = None,
            location: Optional[str] = None
    ) -> bool:
        """
        Ghi nhận tương tác của người dùng với bài hát.

        Args:
            user_id: ID người dùng
            song_id: ID bài hát
            interaction_type: Loại tương tác
            play_count: Số lần phát
            play_duration: Thời gian phát (giây)
            liked: Đã thích chưa
            device_type: Loại thiết bị
            time_context: Ngữ cảnh thời gian
            location: Vị trí

        Returns:
            bool: True nếu ghi nhận thành công
        """
        try:
            async with get_session() as session:
                # Kiểm tra xem đã có bản ghi chưa
                query = select(UserInteraction).where(
                    UserInteraction.user_id == user_id,
                    UserInteraction.song_id == song_id
                )
                result = await session.execute(query)
                interaction = result.scalars().first()

                now = datetime.now()

                if interaction:
                    # Cập nhật bản ghi hiện có
                    if interaction_type == InteractionType.PLAY:
                        interaction.play_count += play_count
                        interaction.play_duration += play_duration
                    elif interaction_type == InteractionType.LIKE:
                        interaction.liked = liked

                    interaction.interaction_type = interaction_type
                    interaction.updated_at = now

                    # Cập nhật thông tin bổ sung nếu có
                    if device_type:
                        interaction.device_type = device_type
                    if time_context:
                        interaction.time_context = time_context
                    if location:
                        interaction.location = location
                else:
                    # Tạo bản ghi mới
                    new_interaction = UserInteraction(
                        user_id=user_id,
                        song_id=song_id,
                        interaction_type=interaction_type,
                        play_count=play_count,
                        play_duration=play_duration,
                        liked=liked,
                        device_type=device_type,
                        time_context=time_context,
                        location=location,
                        created_at=now,
                        updated_at=now
                    )
                    session.add(new_interaction)

                # Commit thay đổi
                await session.commit()
                return True

        except Exception as e:
            logger.error(f"Error recording user interaction: {str(e)}")
            return False

    async def get_similar_users_interactions(
            self,
            similar_users: List[str],
            limit: int = 100
    ) -> List[Dict]:
        """
        Lấy tương tác từ những người dùng tương tự.

        Args:
            similar_users: Danh sách ID người dùng tương tự
            limit: Số lượng tương tác cần lấy

        Returns:
            List[Dict]: Danh sách tương tác
        """
        try:
            if not similar_users:
                return []

            async with get_session() as session:
                query = text("""
                    SELECT 
                        ui.user_id,
                        ui.song_id,
                        ui.interaction_type,
                        ui.play_count,
                        ui.liked,
                        s.artist_id,
                        s.genre_id
                    FROM user_interactions ui
                    JOIN songs s ON ui.song_id = s.id
                    WHERE ui.user_id = ANY(:similar_users)
                    AND ui.play_count > 0
                    ORDER BY ui.created_at DESC
                    LIMIT :limit
                """)

                result = await session.execute(
                    query,
                    {
                        "similar_users": similar_users,
                        "limit": limit
                    }
                )

                interactions = []
                for row in result:
                    interactions.append({
                        "user_id": row[0],
                        "song_id": row[1],
                        "interaction_type": row[2],
                        "play_count": row[3],
                        "liked": row[4],
                        "artist_id": row[5],
                        "genre_id": row[6]
                    })

                return interactions

        except Exception as e:
            logger.error(f"Error getting similar users interactions: {str(e)}")
            return []

    async def get_interaction_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê tương tác trong hệ thống.

        Returns:
            Dict[str, Any]: Các thống kê về tương tác
        """
        try:
            async with get_session() as session:
                # Tổng số tương tác
                count_query = select(func.count()).select_from(UserInteraction)
                count_result = await session.execute(count_query)
                total_interactions = count_result.scalar()

                # Số người dùng có tương tác
                users_query = select(func.count(UserInteraction.user_id.distinct()))
                users_result = await session.execute(users_query)
                total_users = users_result.scalar()

                # Số bài hát có tương tác
                songs_query = select(func.count(UserInteraction.song_id.distinct()))
                songs_result = await session.execute(songs_query)
                total_songs = songs_result.scalar()

                # Thống kê theo loại tương tác
                type_query = text("""
                    SELECT interaction_type, COUNT(*) 
                    FROM user_interactions 
                    GROUP BY interaction_type
                """)
                type_result = await session.execute(type_query)
                type_stats = {str(row[0]): row[1] for row in type_result}

                # Thống kê theo thiết bị
                device_query = text("""
                    SELECT device_type, COUNT(*) 
                    FROM user_interactions 
                    WHERE device_type IS NOT NULL
                    GROUP BY device_type
                """)
                device_result = await session.execute(device_query)
                device_stats = {str(row[0]): row[1] for row in device_result}

                # Thống kê theo thời gian
                time_query = text("""
                    SELECT time_context, COUNT(*) 
                    FROM user_interactions 
                    WHERE time_context IS NOT NULL
                    GROUP BY time_context
                """)
                time_result = await session.execute(time_query)
                time_stats = {str(row[0]): row[1] for row in time_result}

                return {
                    "total_interactions": total_interactions,
                    "total_active_users": total_users,
                    "total_songs_played": total_songs,
                    "interaction_type_stats": type_stats,
                    "device_type_stats": device_stats,
                    "time_context_stats": time_stats
                }

        except Exception as e:
            logger.error(f"Error getting interaction stats: {str(e)}")
            return {
                "total_interactions": 0,
                "total_active_users": 0,
                "total_songs_played": 0,
                "interaction_type_stats": {},
                "device_type_stats": {},
                "time_context_stats": {}
            }