from typing import List, Dict, Tuple, Optional, Any
from sqlalchemy import select, func, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import text

from app.db.models import Song, Genre, Artist, Album, UserInteraction
from app.db.session import get_session
from app.core.logging import logger
from app.core.config import settings
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class SongRepository:
    """Repository cho truy vấn và quản lý bài hát"""

    async def get_by_id(self, song_id: str) -> Optional[Dict]:
        """
        Lấy thông tin bài hát theo ID.

        Args:
            song_id: ID bài hát cần lấy

        Returns:
            Dict | None: Thông tin bài hát hoặc None nếu không tìm thấy
        """
        try:
            async with get_session() as session:
                query = select(Song).where(Song.id == song_id)
                result = await session.execute(query)
                song = result.scalars().first()

                if not song:
                    return None

                # Chuyển đổi ORM object sang dict
                return {
                    "id": song.id,
                    "name": song.name,
                    "description": song.description,
                    "duration": song.duration,
                    "storage_id": song.storage_id,
                    "storage_type": song.storage_type,
                    "artist_id": song.artist_id,
                    "album_id": song.album_id,
                    "genre_id": song.genre_id,
                    "release_year": song.release_year,
                    "created_at": song.created_at,
                    "updated_at": song.updated_at,
                    "tempo": song.tempo,
                    "danceability": song.danceability,
                    "energy": song.energy,
                    "valence": song.valence,
                    "acousticness": song.acousticness,
                    "instrumentalness": song.instrumentalness,
                    "liveness": song.liveness,
                    "key": song.key,
                    "mode": song.mode
                }

        except Exception as e:
            logger.error(f"Error getting song by ID: {str(e)}")
            return None

    async def get_with_details(self, song_id: str) -> Optional[Dict]:
        """
        Lấy thông tin chi tiết về bài hát kèm theo thông tin về nghệ sĩ, thể loại.

        Args:
            song_id: ID bài hát cần lấy

        Returns:
            Dict | None: Thông tin chi tiết bài hát hoặc None nếu không tìm thấy
        """
        try:
            async with get_session() as session:
                # Query bài hát kèm joins
                query = select(
                    Song, Artist, Genre
                ).outerjoin(
                    Artist, Song.artist_id == Artist.id
                ).outerjoin(
                    Genre, Song.genre_id == Genre.id
                ).where(
                    Song.id == song_id
                )

                result = await session.execute(query)
                row = result.first()

                if not row:
                    return None

                song, artist, genre = row

                # Lấy thông tin album nếu có
                album = None
                if song.album_id:
                    album_query = select(Album).where(Album.id == song.album_id)
                    album_result = await session.execute(album_query)
                    album = album_result.scalars().first()

                # Lấy các đặc trưng bổ sung
                features_query = text("""
                    SELECT feature_name, feature_value
                    FROM song_features
                    WHERE song_id = :song_id
                """)
                features_result = await session.execute(features_query, {"song_id": song_id})
                features = {row[0]: row[1] for row in features_result}

                # Tạo dict kết quả
                song_details = {
                    "id": song.id,
                    "name": song.name,
                    "description": song.description,
                    "duration": song.duration,
                    "artist_id": song.artist_id,
                    "artist_name": artist.name if artist else None,
                    "genre_id": song.genre_id,
                    "genre_name": genre.name if genre else None,
                    "genre_key": genre.key if genre else None,
                    "album_id": song.album_id,
                    "album_name": album.name if album else None,
                    "release_year": song.release_year,
                    "created_at": song.created_at,
                    "tempo": song.tempo,
                    "danceability": song.danceability,
                    "energy": song.energy,
                    "valence": song.valence,
                    "acousticness": song.acousticness,
                    "instrumentalness": song.instrumentalness,
                    "liveness": song.liveness,
                    "key": song.key,
                    "mode": song.mode,
                    # Thêm các đặc trưng bổ sung
                    **features
                }

                return song_details

        except Exception as e:
            logger.error(f"Error getting song with details: {str(e)}")
            return None

    async def get_audio_features(self, song_id: str) -> Optional[Dict[str, float]]:
        """
        Lấy các đặc trưng âm thanh của bài hát.

        Args:
            song_id: ID bài hát cần lấy

        Returns:
            Dict | None: Các đặc trưng âm thanh hoặc None nếu không tìm thấy
        """
        try:
            async with get_session() as session:
                query = select(Song).where(Song.id == song_id)
                result = await session.execute(query)
                song = result.scalars().first()

                if not song:
                    return None

                # Lấy các đặc trưng bổ sung
                features_query = text("""
                    SELECT feature_name, feature_value
                    FROM song_features
                    WHERE song_id = :song_id
                """)
                features_result = await session.execute(features_query, {"song_id": song_id})
                extra_features = {row[0]: row[1] for row in features_result}

                # Kết hợp đặc trưng chính và phụ
                audio_features = {
                    "tempo": song.tempo,
                    "danceability": song.danceability,
                    "energy": song.energy,
                    "valence": song.valence,
                    "acousticness": song.acousticness,
                    "instrumentalness": song.instrumentalness,
                    "liveness": song.liveness,
                    **extra_features
                }

                # Loại bỏ các giá trị None
                return {k: v for k, v in audio_features.items() if v is not None}

        except Exception as e:
            logger.error(f"Error getting audio features: {str(e)}")
            return None

    async def get_co_listened_songs(
            self,
            song_id: str,
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Lấy các bài hát thường được nghe cùng với bài hát này.

        Args:
            song_id: ID bài hát gốc
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số)
        """
        try:
            async with get_session() as session:
                # Query bài hát thường được nghe cùng
                query = text("""
                    SELECT s2.id, COUNT(*) as co_listen_count
                    FROM user_interactions ui1
                    JOIN user_interactions ui2 ON ui1.user_id = ui2.user_id 
                      AND DATE(ui1.created_at) = DATE(ui2.created_at)
                      AND ui1.song_id != ui2.song_id
                      AND ui1.interaction_type = 'play'
                      AND ui2.interaction_type = 'play'
                    JOIN songs s2 ON ui2.song_id = s2.id
                    WHERE ui1.song_id = :song_id
                    GROUP BY s2.id
                    ORDER BY co_listen_count DESC
                    LIMIT :limit
                """)

                result = await session.execute(query, {"song_id": song_id, "limit": limit})

                # Chuẩn hóa điểm số về khoảng [0, 1]
                co_listened_songs = [(row[0], row[1]) for row in result]

                if not co_listened_songs:
                    return []

                # Chuẩn hóa điểm số
                max_count = max([count for _, count in co_listened_songs])
                normalized_scores = [
                    (s_id, min(1.0, count / max_count))
                    for s_id, count in co_listened_songs
                ]

                return normalized_scores

        except Exception as e:
            logger.error(f"Error getting co-listened songs: {str(e)}")
            return []

    async def get_similar_songs(
            self,
            song_id: str,
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Lấy các bài hát tương tự dựa trên thể loại và nghệ sĩ.

        Args:
            song_id: ID bài hát gốc
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số)
        """
        try:
            # Lấy thông tin bài hát gốc
            song = await self.get_by_id(song_id)
            if not song:
                return []

            async with get_session() as session:
                # Query bài hát tương tự theo thể loại và nghệ sĩ
                query = text("""
                    SELECT s.id, 
                           CASE 
                             WHEN s.artist_id = :artist_id AND s.genre_id = :genre_id THEN 1.0
                             WHEN s.artist_id = :artist_id THEN 0.8
                             WHEN s.genre_id = :genre_id THEN 0.6
                             ELSE 0.4
                           END as similarity_score
                    FROM songs s
                    WHERE s.id != :song_id
                    ORDER BY similarity_score DESC, s.release_year DESC
                    LIMIT :limit
                """)

                result = await session.execute(
                    query,
                    {
                        "song_id": song_id,
                        "artist_id": song.get("artist_id"),
                        "genre_id": song.get("genre_id"),
                        "limit": limit
                    }
                )

                similar_songs = [(row[0], row[1]) for row in result]
                return similar_songs

        except Exception as e:
            logger.error(f"Error getting similar songs: {str(e)}")
            return []

    async def get_all_with_features(self) -> List[Dict]:
        """
        Lấy tất cả bài hát kèm đặc trưng cho việc xây dựng mô hình.

        Returns:
            List[Dict]: Danh sách bài hát với đặc trưng
        """
        try:
            async with get_session() as session:
                # Query tất cả bài hát
                query = select(
                    Song, Artist, Genre
                ).outerjoin(
                    Artist, Song.artist_id == Artist.id
                ).outerjoin(
                    Genre, Song.genre_id == Genre.id
                )

                result = await session.execute(query)
                rows = result.all()

                if not rows:
                    return []

                # Lấy tất cả đặc trưng bổ sung
                features_query = text("""
                    SELECT song_id, feature_name, feature_value
                    FROM song_features
                """)
                features_result = await session.execute(features_query)
                features_dict = {}

                for row in features_result:
                    song_id, name, value = row
                    if song_id not in features_dict:
                        features_dict[song_id] = {}
                    features_dict[song_id][name] = value

                # Tạo danh sách kết quả
                songs_with_features = []

                for row in rows:
                    song, artist, genre = row

                    # Tạo dict cho bài hát
                    song_dict = {
                        "id": song.id,
                        "name": song.name,
                        "artist_id": song.artist_id,
                        "artist": artist.name if artist else None,
                        "genre_id": song.genre_id,
                        "genre": genre.name if genre else None,
                        "album_id": song.album_id,
                        "release_year": song.release_year,
                        "tempo": song.tempo,
                        "danceability": song.danceability,
                        "energy": song.energy,
                        "valence": song.valence,
                        "acousticness": song.acousticness,
                        "instrumentalness": song.instrumentalness,
                        "liveness": song.liveness,
                        "key": song.key,
                        "mode": song.mode,
                        "duration": song.duration
                    }

                    # Thêm đặc trưng bổ sung nếu có
                    if song.id in features_dict:
                        song_dict.update(features_dict[song.id])

                    songs_with_features.append(song_dict)

                return songs_with_features

        except Exception as e:
            logger.error(f"Error getting all songs with features: {str(e)}")
            return []

    async def get_common_genres(
            self,
            seed_song_id: str,
            recommended_song_ids: List[str]
    ) -> List[str]:
        """
        Lấy các thể loại chung giữa bài hát gốc và các bài hát được gợi ý.

        Args:
            seed_song_id: ID bài hát gốc
            recommended_song_ids: Danh sách ID bài hát được gợi ý

        Returns:
            List[str]: Danh sách tên thể loại
        """
        try:
            async with get_session() as session:
                # Lấy thể loại của bài hát gốc
                seed_query = select(Genre.name).join(
                    Song, Song.genre_id == Genre.id
                ).where(
                    Song.id == seed_song_id
                )

                seed_result = await session.execute(seed_query)
                seed_genre = seed_result.scalar_one_or_none()

                if not seed_genre:
                    return []

                # Lấy thể loại của các bài hát được gợi ý
                reco_query = select(Genre.name).join(
                    Song, Song.genre_id == Genre.id
                ).where(
                    Song.id.in_(recommended_song_ids)
                ).group_by(
                    Genre.name
                )

                reco_result = await session.execute(reco_query)
                reco_genres = [row[0] for row in reco_result]

                # Lấy thể loại chung
                if seed_genre in reco_genres:
                    return [seed_genre]

                return []

        except Exception as e:
            logger.error(f"Error getting common genres: {str(e)}")
            return []

    async def get_common_artists(
            self,
            seed_song_id: str,
            recommended_song_ids: List[str]
    ) -> List[str]:
        """
        Lấy các nghệ sĩ chung giữa bài hát gốc và các bài hát được gợi ý.

        Args:
            seed_song_id: ID bài hát gốc
            recommended_song_ids: Danh sách ID bài hát được gợi ý

        Returns:
            List[str]: Danh sách tên nghệ sĩ
        """
        try:
            async with get_session() as session:
                # Lấy nghệ sĩ của bài hát gốc
                seed_query = select(Artist.name).join(
                    Song, Song.artist_id == Artist.id
                ).where(
                    Song.id == seed_song_id
                )

                seed_result = await session.execute(seed_query)
                seed_artist = seed_result.scalar_one_or_none()

                if not seed_artist:
                    return []

                # Lấy nghệ sĩ của các bài hát được gợi ý
                reco_query = select(Artist.name).join(
                    Song, Song.artist_id == Artist.id
                ).where(
                    Song.id.in_(recommended_song_ids)
                ).group_by(
                    Artist.name
                )

                reco_result = await session.execute(reco_query)
                reco_artists = [row[0] for row in reco_result]

                # Lấy nghệ sĩ chung
                if seed_artist in reco_artists:
                    return [seed_artist]

                return []

        except Exception as e:
            logger.error(f"Error getting common artists: {str(e)}")
            return []

    async def get_songs_by_feature_similarity(
            self,
            seed_features: Dict[str, float],
            feature_boosts: Dict[str, float],
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Lấy bài hát tương tự dựa trên đặc trưng âm thanh.

        Args:
            seed_features: Đặc trưng âm thanh của bài hát gốc
            feature_boosts: Các hệ số tăng cường cho từng đặc trưng
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số)
        """
        try:
            if not seed_features:
                return []

            # Lấy tất cả bài hát và đặc trưng
            all_songs = await self.get_all_with_features()
            if not all_songs:
                return []

            # Chuyển sang DataFrame để xử lý dễ dàng hơn
            songs_df = pd.DataFrame(all_songs)

            # Lọc các cột đặc trưng cần thiết
            feature_columns = []
            for feature in seed_features.keys():
                if feature in songs_df.columns:
                    feature_columns.append(feature)

            if not feature_columns:
                return []

            # Tạo ma trận đặc trưng
            features_df = songs_df[feature_columns].copy()

            # Xử lý các giá trị NaN
            features_df = features_df.fillna(0)

            # Tạo vector đặc trưng của bài hát gốc
            seed_vector = np.array([[seed_features.get(col, 0) for col in feature_columns]])

            # Áp dụng tăng cường đặc trưng
            feature_weights = np.array([feature_boosts.get(col, 1.0) for col in feature_columns])
            weighted_features = features_df.values * feature_weights
            weighted_seed = seed_vector * feature_weights

            # Tính toán cosine similarity
            similarities = cosine_similarity(weighted_seed, weighted_features)[0]

            # Kết hợp với ID bài hát
            similarity_scores = list(zip(songs_df['id'].values, similarities))

            # Sắp xếp theo điểm số giảm dần
            similarity_scores.sort(key=lambda x: x[1], reverse=True)

            # Lấy top N
            return similarity_scores[:limit]

        except Exception as e:
            logger.error(f"Error getting songs by feature similarity: {str(e)}")
            return []

    async def get_songs_by_genres_artists(
            self,
            genre_ids: List[str],
            artist_ids: List[str],
            exclude_song_id: str,
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Lấy bài hát theo thể loại và nghệ sĩ.

        Args:
            genre_ids: Danh sách ID thể loại
            artist_ids: Danh sách ID nghệ sĩ
            exclude_song_id: ID bài hát cần loại trừ
            limit: Số lượng bài hát cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số)
        """
        try:
            if not genre_ids and not artist_ids:
                return []

            async with get_session() as session:
                conditions = []
                if genre_ids:
                    conditions.append(Song.genre_id.in_(genre_ids))
                if artist_ids:
                    conditions.append(Song.artist_id.in_(artist_ids))

                # Query bài hát theo điều kiện
                query = select(Song).where(
                    and_(
                        or_(*conditions),
                        Song.id != exclude_song_id
                    )
                ).order_by(
                    Song.release_year.desc()
                ).limit(limit)

                result = await session.execute(query)
                songs = result.scalars().all()

                # Tính điểm số dựa trên match
                scores = []
                for song in songs:
                    score = 0.5  # Điểm cơ bản

                    # Tăng điểm nếu cả nghệ sĩ và thể loại match
                    if genre_ids and song.genre_id in genre_ids:
                        score += 0.25
                    if artist_ids and song.artist_id in artist_ids:
                        score += 0.25

                    scores.append((song.id, min(1.0, score)))

                return scores

        except Exception as e:
            logger.error(f"Error getting songs by genres/artists: {str(e)}")
            return []