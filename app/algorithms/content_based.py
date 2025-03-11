from typing import List, Dict, Tuple, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

from app.core.logging import logger
from app.db.repositories.song_repository import SongRepository


class ContentBasedRecommender:
    """
    Gợi ý dựa trên nội dung (Content-Based Filtering).

    Thuật toán này sử dụng đặc điểm của bài hát như thể loại, nghệ sĩ,
    và các đặc điểm âm nhạc để tìm những bài hát tương tự.
    """

    def __init__(self):
        self.song_repo = SongRepository()
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.song_features = None
        self.song_ids = None
        self.feature_matrix = None
        self.genre_importance = 1.5  # Hệ số quan trọng cho thể loại
        self.artist_importance = 1.3  # Hệ số quan trọng cho nghệ sĩ
        self.audio_importance = 1.0  # Hệ số quan trọng cho đặc điểm âm thanh

    async def recommend(
            self,
            song_id: str,
            song_details: Dict,
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Đưa ra gợi ý bài hát dựa trên nội dung tương tự.

        Args:
            song_id: ID bài hát gốc
            song_details: Thông tin chi tiết về bài hát
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số tương đồng)
        """
        try:
            # Nếu không có song_details, lấy từ repository
            if not song_details:
                song_details = await self.song_repo.get_with_details(song_id)
                if not song_details:
                    logger.error(f"Song {song_id} not found or has no details")
                    return []

            # Kiểm tra feature matrix đã được xây dựng chưa
            if self.feature_matrix is None:
                await self._build_feature_matrix()

            # Lấy song_idx của bài hát gốc trong model
            if song_id not in self.song_ids:
                # Nếu bài hát gốc không có trong model, thêm nó vào và rebuild model
                await self._add_song_to_model(song_id, song_details)

            # Lấy tất cả similarites cho song_id
            song_idx = self.song_ids.index(song_id)
            song_vector = self.feature_matrix[song_idx].reshape(1, -1)

            # Tính cosine similarity
            similarities = cosine_similarity(song_vector, self.feature_matrix)[0]

            # Lấy top N bài hát tương tự nhất (loại trừ bài hát gốc)
            song_scores = [(self.song_ids[i], float(similarities[i]))
                           for i in range(len(self.song_ids)) if i != song_idx]

            # Sắp xếp theo điểm số giảm dần
            song_scores.sort(key=lambda x: x[1], reverse=True)

            # Lấy top N
            recommendations = song_scores[:limit]

            return recommendations

        except Exception as e:
            logger.error(f"Error in content-based recommendation: {str(e)}")
            return []

    async def _build_feature_matrix(self):
        """
        Xây dựng ma trận đặc trưng cho tất cả bài hát.
        Ma trận này bao gồm thông tin về thể loại, nghệ sĩ, và đặc điểm âm thanh.
        """
        try:
            # Lấy tất cả bài hát và đặc điểm từ DB
            all_songs = await self.song_repo.get_all_with_features()
            if not all_songs:
                logger.warning("No songs found to build content model")
                return

            logger.info(f"Building content-based model with {len(all_songs)} songs")

            # Tạo DataFrame từ dữ liệu
            df = pd.DataFrame(all_songs)

            # Lưu danh sách song_ids
            self.song_ids = df['id'].tolist()

            # Tạo feature text cho từng bài hát
            df['features'] = df.apply(self._create_feature_text, axis=1)

            # Vectorize đặc trưng văn bản
            self.vectorizer.fit(df['features'])
            text_features = self.vectorizer.transform(df['features']).toarray()

            # Thêm đặc trưng số học
            numeric_features = self._extract_numeric_features(df)

            # Kết hợp đặc trưng văn bản và số học
            if numeric_features.size > 0:
                # Chuẩn hóa numeric_features
                numeric_features = (numeric_features - numeric_features.min(axis=0)) / (
                        numeric_features.max(axis=0) - numeric_features.min(axis=0) + 1e-10
                )

                # Ghép đặc trưng
                self.feature_matrix = np.hstack((text_features, numeric_features))
            else:
                self.feature_matrix = text_features

            logger.info(f"Content-based model built with feature matrix shape: {self.feature_matrix.shape}")

        except Exception as e:
            logger.error(f"Error building feature matrix: {str(e)}")
            self.feature_matrix = None

    def _create_feature_text(self, row):
        """
        Tạo văn bản đặc trưng cho một bài hát bao gồm thể loại, nghệ sĩ, v.v.

        Args:
            row: DataFrame row chứa thông tin bài hát

        Returns:
            str: Văn bản đặc trưng
        """
        features = []

        # Thêm genre với trọng số cao hơn
        if 'genre' in row and row['genre']:
            genre = row['genre'].lower()
            # Thêm nhiều lần để tăng trọng số
            for _ in range(int(self.genre_importance * 10)):
                features.append(f"genre_{genre}")

        # Thêm artist với trọng số cao
        if 'artist' in row and row['artist']:
            artist = row['artist'].lower()
            # Thêm nhiều lần để tăng trọng số
            for _ in range(int(self.artist_importance * 10)):
                features.append(f"artist_{artist}")

        # Thêm album
        if 'album' in row and row['album']:
            album = row['album'].lower()
            features.append(f"album_{album}")

        # Thêm năm
        if 'release_year' in row and row['release_year']:
            release_year = str(row['release_year'])
            features.append(f"year_{release_year}")

        # Thêm tempo (nếu có)
        if 'tempo' in row and row['tempo']:
            tempo_category = self._categorize_tempo(row['tempo'])
            features.append(f"tempo_{tempo_category}")

        # Thêm thời lượng
        if 'duration' in row and row['duration']:
            duration_category = self._categorize_duration(row['duration'])
            features.append(f"duration_{duration_category}")

        # Thêm key và mood nếu có
        if 'key' in row and row['key']:
            features.append(f"key_{row['key'].lower()}")

        if 'mood' in row and row['mood']:
            features.append(f"mood_{row['mood'].lower()}")

        # Kết hợp tất cả đặc điểm
        return ' '.join(features)

    def _extract_numeric_features(self, df):
        """
        Trích xuất các đặc trưng số từ DataFrame.

        Args:
            df: DataFrame chứa thông tin bài hát

        Returns:
            np.array: Ma trận đặc trưng số
        """
        numeric_features = []

        # Các đặc trưng số muốn trích xuất
        numeric_columns = ['duration', 'tempo', 'danceability', 'energy', 'valence']

        # Chỉ lấy các cột tồn tại trong df
        available_columns = [col for col in numeric_columns if col in df.columns]

        if available_columns:
            # Chuyển đổi các cột sang kiểu số
            for col in available_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Lấy ma trận đặc trưng số
            numeric_features = df[available_columns].values

            # Thay thế NaN bằng giá trị trung bình của cột
            for i, col in enumerate(available_columns):
                mean_val = np.nanmean(numeric_features[:, i])
                numeric_features[:, i] = np.nan_to_num(numeric_features[:, i], nan=mean_val)

            return numeric_features

        return np.array([])

    def _categorize_tempo(self, tempo):
        """
        Phân loại tempo thành các nhóm.

        Args:
            tempo: Giá trị tempo (BPM)

        Returns:
            str: Nhóm tempo
        """
        if tempo < 70:
            return "slow"
        elif tempo < 110:
            return "medium"
        elif tempo < 140:
            return "fast"
        else:
            return "very_fast"

    def _categorize_duration(self, duration):
        """
        Phân loại thời lượng thành các nhóm.

        Args:
            duration: Thời lượng bài hát (giây)

        Returns:
            str: Nhóm thời lượng
        """
        if duration < 180:  # <3 phút
            return "short"
        elif duration < 240:  # 3-4 phút
            return "medium"
        elif duration < 300:  # 4-5 phút
            return "long"
        else:  # >5 phút
            return "very_long"

    async def _add_song_to_model(self, song_id, song_details):
        """
        Thêm bài hát mới vào mô hình.

        Args:
            song_id: ID bài hát cần thêm
            song_details: Thông tin chi tiết về bài hát
        """
        try:
            if not self.feature_matrix or not self.song_ids:
                # Nếu model chưa được xây dựng, xây dựng lại
                await self._build_feature_matrix()
                return

            # Tạo DataFrame với một dòng cho bài hát mới
            song_df = pd.DataFrame([song_details])
            song_df['id'] = song_id

            # Tạo feature text
            song_df['features'] = song_df.apply(self._create_feature_text, axis=1)

            # Vectorize text features
            new_text_features = self.vectorizer.transform(song_df['features']).toarray()

            # Thêm đặc trưng số học nếu có
            numeric_features = self._extract_numeric_features(song_df)

            # Kết hợp đặc trưng
            if numeric_features.size > 0 and self.feature_matrix.shape[1] > new_text_features.shape[1]:
                numeric_features = (numeric_features - numeric_features.min(axis=0)) / (
                        numeric_features.max(axis=0) - numeric_features.min(axis=0) + 1e-10
                )
                new_features = np.hstack((new_text_features, numeric_features))
            else:
                new_features = new_text_features

            # Thêm vào model
            self.song_ids.append(song_id)

            # Đảm bảo kích thước phù hợp cho việc ghép nối
            if new_features.shape[1] != self.feature_matrix.shape[1]:
                # Xử lý trường hợp khác kích thước
                logger.warning(
                    f"New features dimension mismatch: {new_features.shape[1]} vs {self.feature_matrix.shape[1]}")
                # Trong trường hợp này, xây dựng lại model
                await self._build_feature_matrix()
            else:
                self.feature_matrix = np.vstack((self.feature_matrix, new_features))

            logger.info(f"Added song {song_id} to content-based model")

        except Exception as e:
            logger.error(f"Error adding song to content model: {str(e)}")
            # Trong trường hợp lỗi, xây dựng lại model
            await self._build_feature_matrix()