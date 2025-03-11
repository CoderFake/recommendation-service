from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.sql.expression import text

from app.db.models import User, UserInteraction, UserGenrePreference, UserArtistPreference, Song, Artist, Genre
from app.db.session import get_session
from app.core.logging import logger


class UserRepository:
    """Repository cho truy vấn và quản lý người dùng"""

    async def get_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Lấy thông tin người dùng theo ID.

        Args:
            user_id: ID người dùng cần lấy

        Returns:
            Dict | None: Thông tin người dùng hoặc None nếu không tìm thấy
        """
        try:
            async with get_session() as session:
                query = select(User).where(User.id == user_id)
                result = await session.execute(query)
                user = result.scalars().first()

                if not user:
                    return None

                # Chuyển đổi ORM object sang dict
                return {
                    "id": user.id,
                    "name": user.name,
                    "gender": user.gender,
                    "dob": user.dob,
                    "country_iso2": user.country_iso2,
                    "language": user.language,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }

        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Lấy thông tin sở thích của người dùng.

        Args:
            user_id: ID người dùng

        Returns:
            Dict: Thông tin sở thích của người dùng
        """
        try:
            async with get_session() as session:
                # Lấy sở thích thể loại
                genre_query = select(
                    UserGenrePreference.genre_id,
                    UserGenrePreference.score,
                    Genre.name
                ).join(
                    Genre, UserGenrePreference.genre_id == Genre.id
                ).where(
                    UserGenrePreference.user_id == user_id
                ).order_by(
                    desc(UserGenrePreference.score)
                )

                genre_result = await session.execute(genre_query)
                genre_preferences = [
                    {"genre_id": row[0], "score": row[1], "name": row[2]}
                    for row in genre_result
                ]

                # Lấy sở thích nghệ sĩ
                artist_query = select(
                    UserArtistPreference.artist_id,
                    UserArtistPreference.score,
                    UserArtistPreference.follows,
                    Artist.name
                ).join(
                    Artist, UserArtistPreference.artist_id == Artist.id
                ).where(
                    UserArtistPreference.user_id == user_id
                ).order_by(
                    desc(UserArtistPreference.score)
                )

                artist_result = await session.execute(artist_query)
                artist_preferences = [
                    {
                        "artist_id": row[0],
                        "score": row[1],
                        "follows": row[2],
                        "name": row[3]
                    }
                    for row in artist_result
                ]

                return {
                    "genre_preferences": genre_preferences,
                    "artist_preferences": artist_preferences
                }

        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            return {"genre_preferences": [], "artist_preferences": []}

    async def get_recently_played_songs(
            self,
            user_id: str,
            limit: int = 10
    ) -> List[Dict]:
        """
        Lấy danh sách bài hát gần đây mà người dùng đã nghe.

        Args:
            user_id: ID người dùng
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Dict]: Danh sách bài hát gần đây
        """
        try:
            async with get_session() as session:
                query = select(
                    Song.id,
                    Song.name,
                    Song.artist_id,
                    Artist.name.label("artist_name"),
                    UserInteraction.created_at,
                    UserInteraction.play_count,
                    UserInteraction.liked
                ).join(
                    UserInteraction, Song.id == UserInteraction.song_id
                ).outerjoin(
                    Artist, Song.artist_id == Artist.id
                ).where(
                    UserInteraction.user_id == user_id,
                    UserInteraction.interaction_type == "play"
                ).order_by(
                    desc(UserInteraction.created_at)
                ).limit(limit)

                result = await session.execute(query)

                recently_played = []
                for row in result:
                    recently_played.append({
                        "song_id": row[0],
                        "song_name": row[1],
                        "artist_id": row[2],
                        "artist_name": row[3],
                        "played_at": row[4],
                        "play_count": row[5],
                        "liked": row[6]
                    })

                return recently_played

        except Exception as e:
            logger.error(f"Error getting recently played songs: {str(e)}")
            return []

    async def update_user_preferences(
            self,
            user_id: str,
            genre_id: Optional[str] = None,
            artist_id: Optional[str] = None,
            action: str = "increase"
    ) -> bool:
        """
        Cập nhật sở thích của người dùng dựa trên hành động.

        Args:
            user_id: ID người dùng
            genre_id: ID thể loại (nếu có)
            artist_id: ID nghệ sĩ (nếu có)
            action: Hành động (increase/decrease)

        Returns:
            bool: True nếu cập nhật thành công, False nếu có lỗi
        """
        try:
            increment = 0.1 if action == "increase" else -0.05

            async with get_session() as session:
                if genre_id:
                    # Kiểm tra xem đã có bản ghi chưa
                    genre_pref_query = select(UserGenrePreference).where(
                        UserGenrePreference.user_id == user_id,
                        UserGenrePreference.genre_id == genre_id
                    )
                    genre_pref_result = await session.execute(genre_pref_query)
                    genre_pref = genre_pref_result.scalars().first()

                    if genre_pref:
                        # Cập nhật điểm số
                        genre_pref.score = max(0, min(1.0, genre_pref.score + increment))
                    else:
                        # Tạo mới
                        new_score = 0.5 if action == "increase" else 0.0
                        new_genre_pref = UserGenrePreference(
                            user_id=user_id,
                            genre_id=genre_id,
                            score=max(0, min(1.0, new_score))
                        )
                        session.add(new_genre_pref)

                if artist_id:
                    # Kiểm tra xem đã có bản ghi chưa
                    artist_pref_query = select(UserArtistPreference).where(
                        UserArtistPreference.user_id == user_id,
                        UserArtistPreference.artist_id == artist_id
                    )
                    artist_pref_result = await session.execute(artist_pref_query)
                    artist_pref = artist_pref_result.scalars().first()

                    if artist_pref:
                        # Cập nhật điểm số
                        artist_pref.score = max(0, min(1.0, artist_pref.score + increment))
                    else:
                        # Tạo mới
                        new_score = 0.5 if action == "increase" else 0.0
                        new_artist_pref = UserArtistPreference(
                            user_id=user_id,
                            artist_id=artist_id,
                            score=max(0, min(1.0, new_score)),
                            follows=False
                        )
                        session.add(new_artist_pref)

                await session.commit()
                return True

        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            return False

    async def get_user_genres(self, user_id: str) -> List[str]:
        """
        Lấy các thể loại mà người dùng thích.

        Args:
            user_id: ID người dùng

        Returns:
            List[str]: Danh sách ID thể loại
        """
        try:
            async with get_session() as session:
                # Query lấy thể loại từ sở thích
                explicit_query = select(UserGenrePreference.genre_id).where(
                    UserGenrePreference.user_id == user_id,
                    UserGenrePreference.score > 0.5
                )

                # Query lấy thể loại từ bài hát đã nghe
                implicit_query = text("""
                    SELECT DISTINCT s.genre_id
                    FROM user_interactions ui
                    JOIN songs s ON ui.song_id = s.id
                    WHERE ui.user_id = :user_id
                    AND s.genre_id IS NOT NULL
                    AND ui.play_count > 0
                """)

                explicit_result = await session.execute(explicit_query)
                implicit_result = await session.execute(implicit_query, {"user_id": user_id})

                explicit_genres = [row[0] for row in explicit_result if row[0]]
                implicit_genres = [row[0] for row in implicit_result if row[0]]

                # Kết hợp và loại bỏ trùng lặp
                return list(set(explicit_genres + implicit_genres))

        except Exception as e:
            logger.error(f"Error getting user genres: {str(e)}")
            return []

    async def get_user_artists(self, user_id: str) -> List[str]:
        """
        Lấy các nghệ sĩ mà người dùng thích.

        Args:
            user_id: ID người dùng

        Returns:
            List[str]: Danh sách ID nghệ sĩ
        """
        try:
            async with get_session() as session:
                # Query lấy nghệ sĩ từ sở thích
                explicit_query = select(UserArtistPreference.artist_id).where(
                    UserArtistPreference.user_id == user_id,
                    or_(
                        UserArtistPreference.score > 0.5,
                        UserArtistPreference.follows == True
                    )
                )

                # Query lấy nghệ sĩ từ bài hát đã nghe
                implicit_query = text("""
                    SELECT DISTINCT s.artist_id
                    FROM user_interactions ui
                    JOIN songs s ON ui.song_id = s.id
                    WHERE ui.user_id = :user_id
                    AND s.artist_id IS NOT NULL
                    AND ui.play_count > 1
                """)

                explicit_result = await session.execute(explicit_query)
                implicit_result = await session.execute(implicit_query, {"user_id": user_id})

                explicit_artists = [row[0] for row in explicit_result if row[0]]
                implicit_artists = [row[0] for row in implicit_result if row[0]]

                # Kết hợp và loại bỏ trùng lặp
                return list(set(explicit_artists + implicit_artists))

        except Exception as e:
            logger.error(f"Error getting user artists: {str(e)}")
            return []

    async def calculate_similarity_with_users(
            self,
            user_id: str,
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Tính toán độ tương đồng với người dùng khác.

        Args:
            user_id: ID người dùng cần so sánh
            limit: Số lượng người dùng tương đồng cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (user_id, điểm tương đồng)
        """
        try:
            async with get_session() as session:
                # Lấy sở thích của người dùng hiện tại
                user_genres = await self.get_user_genres(user_id)
                user_artists = await self.get_user_artists(user_id)

                if not user_genres and not user_artists:
                    return []

                # Query người dùng có cùng sở thích
                similar_users_query = text("""
                    WITH user_genres AS (
                        SELECT :genre_ids AS genre_ids
                    ), user_artists AS (
                        SELECT :artist_ids AS artist_ids
                    )

                    SELECT 
                        u.id,
                        (
                            COALESCE(
                                (
                                    SELECT COUNT(*)
                                    FROM user_genre_preferences ugp
                                    WHERE ugp.user_id = u.id
                                    AND ugp.genre_id = ANY(ARRAY(SELECT unnest(genre_ids) FROM user_genres))
                                ), 0
                            ) * 0.5 +
                            COALESCE(
                                (
                                    SELECT COUNT(*)
                                    FROM user_artist_preferences uap
                                    WHERE uap.user_id = u.id
                                    AND uap.artist_id = ANY(ARRAY(SELECT unnest(artist_ids) FROM user_artists))
                                ), 0
                            ) * 0.8
                        ) AS similarity_score
                    FROM users u
                    WHERE u.id != :user_id
                    AND (
                        EXISTS (
                            SELECT 1
                            FROM user_genre_preferences ugp
                            WHERE ugp.user_id = u.id
                            AND ugp.genre_id = ANY(ARRAY(SELECT unnest(genre_ids) FROM user_genres))
                        )
                        OR
                        EXISTS (
                            SELECT 1
                            FROM user_artist_preferences uap
                            WHERE uap.user_id = u.id
                            AND uap.artist_id = ANY(ARRAY(SELECT unnest(artist_ids) FROM user_artists))
                        )
                    )
                    ORDER BY similarity_score DESC
                    LIMIT :limit
                """)

                similar_users_result = await session.execute(
                    similar_users_query,
                    {
                        "user_id": user_id,
                        "genre_ids": user_genres,
                        "artist_ids": user_artists,
                        "limit": limit
                    }
                )

                similar_users = [(row[0], row[1]) for row in similar_users_result]

                # Chuẩn hóa điểm số về khoảng [0, 1]
                if similar_users:
                    max_score = max([score for _, score in similar_users])
                    if max_score > 0:
                        similar_users = [(u_id, min(1.0, score / max_score)) for u_id, score in similar_users]

                return similar_users

        except Exception as e:
            logger.error(f"Error calculating user similarity: {str(e)}")
            return []