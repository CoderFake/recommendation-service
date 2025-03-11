import asyncio
import time
from typing import Dict, List, Any, Optional
import datetime
from sqlalchemy import text
import threading

from app.db.session import get_session
from app.core.logging import logger
from app.core.config import settings
from app.db.models import Song, Artist, Genre, Album, User, Base


class DataSyncService:
    """
    Service đồng bộ dữ liệu từ database chính vào database của service recommendation.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.last_sync_time = {}
        for table in ["songs", "artists", "genres", "albums", "users"]:
            self.last_sync_time[table] = datetime.datetime.now() - datetime.timedelta(days=30)

        self._initialized = True
        self._running = False
        self._sync_interval = settings.SYNC_INTERVAL_MINUTES * 60  # Chuyển đổi phút sang giây

    async def sync_data(self):
        """
        Đồng bộ dữ liệu từ CSDL chính vào CSDL recommendation.

        Hàm này được gọi định kỳ để cập nhật dữ liệu từ database chính vào
        database của recommendation service.
        """
        try:
            logger.info("Starting data synchronization...")

            # Gọi các hàm đồng bộ cho từng loại dữ liệu
            await self.sync_songs()
            await self.sync_artists()
            await self.sync_genres()
            await self.sync_albums()
            await self.sync_users()

            logger.info("Data synchronization completed successfully")

        except Exception as e:
            logger.error(f"Error during data synchronization: {str(e)}")

    async def sync_artists(self):
        """
        Đồng bộ dữ liệu nghệ sĩ từ CSDL chính.
        """
        try:
            # Lấy bản ghi đã được cập nhật kể từ lần đồng bộ cuối
            last_sync = self.last_sync_time["artists"]

            # Kết nối đến CSDL gốc
            main_db_query = f"""
                SELECT 
                    id, name, genre_id, created_at, updated_at
                FROM artists 
                WHERE updated_at > '{last_sync.isoformat()}'
                ORDER BY updated_at ASC
                LIMIT 500
            """

            async with get_session() as session:
                result = await session.execute(text(main_db_query))
                artists_data = result.fetchall()

                # Cập nhật hoặc thêm mới từng bản ghi
                for row in artists_data:
                    # Kiểm tra xem bản ghi đã tồn tại chưa
                    artist_query = text("SELECT id FROM artists WHERE id = :id")
                    artist_result = await session.execute(artist_query, {"id": row[0]})
                    artist_exists = artist_result.first() is not None

                    if artist_exists:
                        # Cập nhật bản ghi hiện có
                        update_query = text("""
                            UPDATE artists
                            SET 
                                name = :name,
                                genre_id = :genre_id,
                                updated_at = :updated_at
                            WHERE id = :id
                        """)
                    else:
                        # Thêm bản ghi mới
                        update_query = text("""
                            INSERT INTO artists (
                                id, name, genre_id, created_at, updated_at
                            ) VALUES (
                                :id, :name, :genre_id, :created_at, :updated_at
                            )
                        """)

                    # Thực thi truy vấn với các tham số
                    await session.execute(
                        update_query,
                        {
                            "id": row[0],
                            "name": row[1],
                            "genre_id": row[2],
                            "created_at": row[3],
                            "updated_at": row[4]
                        }
                    )

                # Commit các thay đổi
                await session.commit()

            # Cập nhật thời gian đồng bộ cuối cùng
            if artists_data:
                self.last_sync_time["artists"] = datetime.datetime.now()

            logger.info(f"Synchronized {len(artists_data)} artists")

        except Exception as e:
            logger.error(f"Error synchronizing artists: {str(e)}")

    async def sync_genres(self):
        """
        Đồng bộ dữ liệu thể loại từ CSDL chính.
        """
        try:
            # Lấy bản ghi đã được cập nhật kể từ lần đồng bộ cuối
            last_sync = self.last_sync_time["genres"]

            # Kết nối đến CSDL gốc
            main_db_query = f"""
                SELECT 
                    id, name, key, created_at
                FROM genres 
                WHERE created_at > '{last_sync.isoformat()}'
                ORDER BY created_at ASC
                LIMIT 200
            """

            async with get_session() as session:
                result = await session.execute(text(main_db_query))
                genres_data = result.fetchall()

                # Cập nhật hoặc thêm mới từng bản ghi
                for row in genres_data:
                    # Kiểm tra xem bản ghi đã tồn tại chưa
                    genre_query = text("SELECT id FROM genres WHERE id = :id")
                    genre_result = await session.execute(genre_query, {"id": row[0]})
                    genre_exists = genre_result.first() is not None

                    if genre_exists:
                        # Cập nhật bản ghi hiện có
                        update_query = text("""
                            UPDATE genres
                            SET 
                                name = :name,
                                key = :key
                            WHERE id = :id
                        """)
                    else:
                        # Thêm bản ghi mới
                        update_query = text("""
                            INSERT INTO genres (
                                id, name, key, created_at
                            ) VALUES (
                                :id, :name, :key, :created_at
                            )
                        """)

                    # Thực thi truy vấn với các tham số
                    await session.execute(
                        update_query,
                        {
                            "id": row[0],
                            "name": row[1],
                            "key": row[2],
                            "created_at": row[3]
                        }
                    )

                # Commit các thay đổi
                await session.commit()

            # Cập nhật thời gian đồng bộ cuối cùng
            if genres_data:
                self.last_sync_time["genres"] = datetime.datetime.now()

            logger.info(f"Synchronized {len(genres_data)} genres")

        except Exception as e:
            logger.error(f"Error synchronizing genres: {str(e)}")

    async def sync_albums(self):
        """
        Đồng bộ dữ liệu album từ CSDL chính.
        """
        try:
            # Lấy bản ghi đã được cập nhật kể từ lần đồng bộ cuối
            last_sync = self.last_sync_time["albums"]

            # Kết nối đến CSDL gốc
            main_db_query = f"""
                SELECT 
                    id, name, description, artist_id, release_year, created_at, updated_at
                FROM albums 
                WHERE updated_at > '{last_sync.isoformat()}'
                ORDER BY updated_at ASC
                LIMIT 300
            """

            async with get_session() as session:
                result = await session.execute(text(main_db_query))
                albums_data = result.fetchall()

                # Cập nhật hoặc thêm mới từng bản ghi
                for row in albums_data:
                    # Kiểm tra xem bản ghi đã tồn tại chưa
                    album_query = text("SELECT id FROM albums WHERE id = :id")
                    album_result = await session.execute(album_query, {"id": row[0]})
                    album_exists = album_result.first() is not None

                    if album_exists:
                        # Cập nhật bản ghi hiện có
                        update_query = text("""
                            UPDATE albums
                            SET 
                                name = :name,
                                description = :description,
                                artist_id = :artist_id,
                                release_year = :release_year,
                                updated_at = :updated_at
                            WHERE id = :id
                        """)
                    else:
                        # Thêm bản ghi mới
                        update_query = text("""
                            INSERT INTO albums (
                                id, name, description, artist_id, release_year, created_at, updated_at
                            ) VALUES (
                                :id, :name, :description, :artist_id, :release_year, :created_at, :updated_at
                            )
                        """)

                    # Thực thi truy vấn với các tham số
                    await session.execute(
                        update_query,
                        {
                            "id": row[0],
                            "name": row[1],
                            "description": row[2],
                            "artist_id": row[3],
                            "release_year": row[4],
                            "created_at": row[5],
                            "updated_at": row[6]
                        }
                    )

                # Commit các thay đổi
                await session.commit()

            # Cập nhật thời gian đồng bộ cuối cùng
            if albums_data:
                self.last_sync_time["albums"] = datetime.datetime.now()

            logger.info(f"Synchronized {len(albums_data)} albums")

        except Exception as e:
            logger.error(f"Error synchronizing albums: {str(e)}")

    async def sync_users(self):
        """
        Đồng bộ dữ liệu người dùng từ CSDL chính.
        """
        try:
            # Lấy bản ghi đã được cập nhật kể từ lần đồng bộ cuối
            last_sync = self.last_sync_time["users"]

            # Kết nối đến CSDL gốc
            main_db_query = f"""
                SELECT 
                    id, name, gender, dob, country_iso2, language, created_at, updated_at
                FROM users 
                WHERE updated_at > '{last_sync.isoformat()}'
                ORDER BY updated_at ASC
                LIMIT 500
            """

            async with get_session() as session:
                result = await session.execute(text(main_db_query))
                users_data = result.fetchall()

                # Cập nhật hoặc thêm mới từng bản ghi
                for row in users_data:
                    # Kiểm tra xem bản ghi đã tồn tại chưa
                    user_query = text("SELECT id FROM users WHERE id = :id")
                    user_result = await session.execute(user_query, {"id": row[0]})
                    user_exists = user_result.first() is not None

                    if user_exists:
                        # Cập nhật bản ghi hiện có
                        update_query = text("""
                            UPDATE users
                            SET 
                                name = :name,
                                gender = :gender,
                                dob = :dob,
                                country_iso2 = :country_iso2,
                                language = :language,
                                updated_at = :updated_at
                            WHERE id = :id
                        """)
                    else:
                        # Thêm bản ghi mới
                        update_query = text("""
                            INSERT INTO users (
                                id, name, gender, dob, country_iso2, language, created_at, updated_at
                            ) VALUES (
                                :id, :name, :gender, :dob, :country_iso2, :language, :created_at, :updated_at
                            )
                        """)

                    # Thực thi truy vấn với các tham số
                    await session.execute(
                        update_query,
                        {
                            "id": row[0],
                            "name": row[1],
                            "gender": row[2],
                            "dob": row[3],
                            "country_iso2": row[4],
                            "language": row[5],
                            "created_at": row[6],
                            "updated_at": row[7]
                        }
                    )

                # Commit các thay đổi
                await session.commit()

            # Cập nhật thời gian đồng bộ cuối cùng
            if users_data:
                self.last_sync_time["users"] = datetime.datetime.now()

            logger.info(f"Synchronized {len(users_data)} users")

        except Exception as e:
            logger.error(f"Error synchronizing users: {str(e)}")

    async def _sync_loop(self):
        """
        Vòng lặp chạy đồng bộ dữ liệu định kỳ.
        """
        self._running = True
        while self._running:
            try:
                logger.info(f"Running scheduled data sync (interval: {self._sync_interval} seconds)")
                await self.sync_data()

                # Chờ đến kỳ đồng bộ tiếp theo
                await asyncio.sleep(self._sync_interval)

            except asyncio.CancelledError:
                logger.info("Data sync loop cancelled")
                self._running = False
                break
            except Exception as e:
                logger.error(f"Error in sync loop: {str(e)}")
                # Nếu có lỗi, chờ 60 giây và thử lại
                await asyncio.sleep(60)

    def start(self):
        """
        Bắt đầu quá trình đồng bộ dữ liệu theo lịch.
        """
        if not self._running:
            # Tạo task đồng bộ chạy nền
            asyncio.create_task(self._sync_loop())
            logger.info(f"Data sync service started with interval {self._sync_interval} seconds")
        else:
            logger.warning("Data sync service is already running")

    def stop(self):
        """
        Dừng quá trình đồng bộ dữ liệu.
        """
        self._running = False
        logger.info("Data sync service stopped")

    async def get_sync_status(self):
        """
        Lấy thông tin trạng thái đồng bộ.

        Returns:
            Dict: Thông tin về trạng thái đồng bộ
        """
        return {
            "running": self._running,
            "sync_interval_minutes": settings.SYNC_INTERVAL_MINUTES,
            "last_sync_time": {k: v.isoformat() for k, v in self.last_sync_time.items()}
        }


# Instance toàn cục của DataSyncService
data_sync_service = DataSyncService()


def start_sync_scheduler():
    """
    Khởi động scheduler đồng bộ dữ liệu.

    Hàm này được gọi khi ứng dụng khởi động.
    """
    if settings.REAL_TIME_SYNC_ENABLED:
        data_sync_service.start()

        # Đồng bộ ngay lập tức khi khởi động
        asyncio.create_task(data_sync_service.sync_data())

        logger.info("Data sync scheduler started")
    else:
        logger.info("Real-time data sync is disabled in settings")

    async def sync_songs(self):
        """
        Đồng bộ dữ liệu bài hát từ CSDL chính.
        """
        try:
            # Lấy bản ghi đã được cập nhật kể từ lần đồng bộ cuối
            last_sync = self.last_sync_time["songs"]

            # Kết nối đến CSDL gốc
            main_db_query = f"""
                SELECT 
                    id, name, description, duration, storage_id, storage_type, 
                    artist_id, album_id, genre_id, release_year, created_at, updated_at,
                    tempo, danceability, energy, valence, acousticness, 
                    instrumentalness, liveness, key, mode
                FROM songs 
                WHERE updated_at > '{last_sync.isoformat()}'
                ORDER BY updated_at ASC
                LIMIT 1000
            """

            # Kết nối đến DB chính (trong triển khai thực tế, sẽ cần kết nối đến DB riêng)
            async with get_session() as session:
                # Lấy dữ liệu từ DB chính
                # Trong triển khai thực tế, bạn sẽ cần kết nối đến DB chính thay vì sử dụng cùng DB
                # Ở đây chúng ta giả định rằng dữ liệu được lấy từ DB chính
                result = await session.execute(text(main_db_query))
                songs_data = result.fetchall()

                # Cập nhật hoặc thêm mới từng bản ghi
                for row in songs_data:
                    # Kiểm tra xem bản ghi đã tồn tại chưa
                    song_query = text("SELECT id FROM songs WHERE id = :id")
                    song_result = await session.execute(song_query, {"id": row[0]})
                    song_exists = song_result.first() is not None

                    if song_exists:
                        # Cập nhật bản ghi hiện có
                        update_query = text("""
                            UPDATE songs
                            SET 
                                name = :name,
                                description = :description,
                                duration = :duration,
                                storage_id = :storage_id,
                                storage_type = :storage_type,
                                artist_id = :artist_id,
                                album_id = :album_id,
                                genre_id = :genre_id,
                                release_year = :release_year,
                                updated_at = :updated_at,
                                tempo = :tempo,
                                danceability = :danceability,
                                energy = :energy,
                                valence = :valence,
                                acousticness = :acousticness,
                                instrumentalness = :instrumentalness,
                                liveness = :liveness,
                                key = :key,
                                mode = :mode
                            WHERE id = :id
                        """)
                    else:
                        # Thêm bản ghi mới
                        update_query = text("""
                            INSERT INTO songs (
                                id, name, description, duration, storage_id, storage_type, 
                                artist_id, album_id, genre_id, release_year, created_at, updated_at,
                                tempo, danceability, energy, valence, acousticness, 
                                instrumentalness, liveness, key, mode
                            ) VALUES (
                                :id, :name, :description, :duration, :storage_id, :storage_type, 
                                :artist_id, :album_id, :genre_id, :release_year, :created_at, :updated_at,
                                :tempo, :danceability, :energy, :valence, :acousticness, 
                                :instrumentalness, :liveness, :key, :mode
                            )
                        """)

                    # Thực thi truy vấn với các tham số
                    await session.execute(
                        update_query,
                        {
                            "id": row[0],
                            "name": row[1],
                            "description": row[2],
                            "duration": row[3],
                            "storage_id": row[4],
                            "storage_type": row[5],
                            "artist_id": row[6],
                            "album_id": row[7],
                            "genre_id": row[8],
                            "release_year": row[9],
                            "created_at": row[10],
                            "updated_at": row[11],
                            "tempo": row[12],
                            "danceability": row[13],
                            "energy": row[14],
                            "valence": row[15],
                            "acousticness": row[16],
                            "instrumentalness": row[17],
                            "liveness": row[18],
                            "key": row[19],
                            "mode": row[20]
                        }
                    )

                # Commit các thay đổi
                await session.commit()

            # Cập nhật thời gian đồng bộ cuối cùng
            if songs_data:
                self.last_sync_time["songs"] = datetime.datetime.now()

            logger.info(f"Synchronized {len(songs_data)} songs")

        except Exception as e:
            logger.error(f"Error synchronizing songs: {str(e)}")