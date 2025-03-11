from typing import List, Dict, Tuple, Any, Optional
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
import pandas as pd
import threading
from datetime import datetime
import time

from app.core.logging import logger
from app.core.config import settings
from app.algorithms.ncf import ncf_recommender


class CollaborativeFilteringRecommender:
    """
    Lọc cộng tác (Collaborative Filtering) sử dụng ma trận SVD và Neural Collaborative Filtering (NCF).

    Thuật toán này kết hợp cả SVD và NCF để gợi ý bài hát, cho phép:
    - SVD: Phân tích mẫu nghe của người dùng và tìm kiếm người dùng tương tự
    - NCF: Sử dụng deep learning để nắm bắt các mối quan hệ phức tạp hơn
    - Incremental learning: Cập nhật mô hình liên tục khi có tương tác mới
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

        # SVD model components
        self.model = None
        self.user_mapping = {}  # map user_id -> array index
        self.song_mapping = {}  # map song_id -> array index
        self.reverse_user_mapping = {}  # map array index -> user_id
        self.reverse_song_mapping = {}  # map array index -> song_id
        self.user_factors = None
        self.song_factors = None

        # Tracking model freshness
        self.last_training_time = None
        self.last_incremental_update = None
        self.model_version = 0

        # Model update parameters
        self.use_ncf = settings.USE_NCF
        self.use_incremental = settings.USE_INCREMENTAL_LEARNING
        self.update_interval = settings.MODEL_UPDATE_INTERVAL_MINUTES * 60  # seconds

        # Thread control
        self.update_thread_running = False

        # Start update thread if incremental learning is enabled
        if self.use_incremental:
            self._start_update_thread()

        self._initialized = True

    async def recommend(
            self,
            song_id: str,
            user_id: str,
            user_interactions: List[Dict],
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Đưa ra gợi ý bài hát dựa trên bài hát đầu vào và hành vi người dùng.

        Args:
            song_id: ID bài hát gốc
            user_id: ID người dùng
            user_interactions: Dữ liệu tương tác lịch sử của người dùng
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số tương đồng)
        """
        try:
            # Nếu dùng NCF và có đủ tương tác, ưu tiên NCF
            if self.use_ncf and user_interactions and len(user_interactions) >= 5:
                # Lấy tất cả bài hát trong hệ thống
                candidate_songs = list(self.song_mapping.keys()) if self.model is not None else []

                # Thêm các bài hát từ tương tác người dùng để đảm bảo coverage
                if user_interactions:
                    for interaction in user_interactions:
                        if "song_id" in interaction and interaction["song_id"] not in candidate_songs:
                            candidate_songs.append(interaction["song_id"])

                # Loại bỏ bài hát gốc khỏi danh sách ứng viên
                if song_id in candidate_songs:
                    candidate_songs.remove(song_id)

                # Gọi mô hình NCF để lấy gợi ý
                ncf_recommendations = ncf_recommender.recommend(
                    song_id=song_id,
                    user_id=user_id,
                    candidate_songs=candidate_songs,
                    limit=limit
                )

                # Nếu NCF trả về kết quả, sử dụng nó
                if ncf_recommendations:
                    logger.info(f"Sử dụng NCF để gợi ý cho user {user_id}")

                    # Ghi lại tương tác cho incremental learning nếu cần
                    if self.use_incremental:
                        for interaction in user_interactions:
                            ncf_recommender.add_interaction(interaction)

                    return ncf_recommendations

            # Nếu không dùng NCF hoặc NCF không có kết quả, sử dụng SVD
            logger.info(f"Sử dụng SVD để gợi ý cho user {user_id}")

            # Nếu người dùng không có đủ dữ liệu tương tác, sử dụng song similarity
            if not user_interactions or len(user_interactions) < 5:
                logger.info(f"User {user_id} has insufficient interactions. Using song similarity instead.")
                return await self._item_based_recommendation(song_id, limit)

            # Kiểm tra model đã được training chưa
            if self.model is None:
                logger.info("Collaborative filtering model not trained. Training now...")
                await self._train_model()

            # Nếu model vẫn là None sau khi train, có lỗi train
            if self.model is None:
                logger.error("Failed to train collaborative filtering model")
                return []

            # Lấy song_idx trong mô hình
            if song_id not in self.song_mapping:
                logger.warning(f"Song {song_id} not found in collaborative model")
                return await self._item_based_recommendation(song_id, limit)

            song_idx = self.song_mapping[song_id]

            # User-based collaborative filtering
            # Kiểm tra xem user_id đã có trong model chưa
            if user_id in self.user_mapping:
                # Lấy gợi ý dựa trên người dùng hiện tại
                user_idx = self.user_mapping[user_id]
                recommendations = await self._user_based_recommendation(user_idx, song_id, limit)
            else:
                # Nếu người dùng mới, dùng tính năng của bài hát
                recommendations = await self._feature_based_recommendation(song_idx, limit)

            return recommendations

        except Exception as e:
            logger.error(f"Error in collaborative filtering: {str(e)}")
            return []

    def _start_update_thread(self):
        """Bắt đầu thread cập nhật mô hình định kỳ."""

        def update_loop():
            self.update_thread_running = True
            while self.update_thread_running:
                # Kiểm tra xem đã đến lúc cập nhật chưa
                current_time = time.time()
                if self.last_incremental_update is None or (
                        current_time - self.last_incremental_update) > self.update_interval:
                    try:
                        # Chạy cập nhật mô hình
                        self._update_models_async()
                        self.last_incremental_update = current_time
                    except Exception as e:
                        logger.error(f"Lỗi trong thread cập nhật mô hình: {str(e)}")

                # Ngủ một khoảng thời gian ngắn
                time.sleep(30)

        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        logger.info("Đã bắt đầu thread cập nhật mô hình collaborative filtering")

    async def _update_models_async(self):
        """Cập nhật bất đồng bộ các mô hình."""
        try:
            # Lấy dữ liệu tương tác mới từ repository
            from app.db.repositories.interaction_repository import InteractionRepository
            interaction_repo = InteractionRepository()

            # Lấy tương tác mới kể từ lần cập nhật cuối
            since_time = self.last_training_time or datetime.now().replace(year=datetime.now().year - 1)
            interactions = await interaction_repo.get_interactions_since(since_time)

            if not interactions:
                logger.info("Không có dữ liệu tương tác mới để cập nhật mô hình")
                return

            logger.info(f"Đang cập nhật mô hình với {len(interactions)} tương tác mới")

            # Chỉ cập nhật NCF incremental nếu được bật
            if self.use_ncf and self.use_incremental:
                # Chuyển đổi định dạng dữ liệu
                ncf_interactions = []
                for interaction in interactions:
                    ncf_interaction = {
                        "user_id": interaction["user_id"],
                        "song_id": interaction["song_id"],
                        "play_count": interaction.get("play_count", 0),
                        "liked": interaction.get("liked", False)
                    }
                    ncf_interactions.append(ncf_interaction)

                    # Cập nhật mô hình NCF theo dạng incremental
                    ncf_recommender.add_interaction(ncf_interaction)

            # Cập nhật mô hình SVD
            self._update_svd_model(interactions)

            # Cập nhật thời gian training
            self.last_training_time = datetime.now()
            self.model_version += 1

            logger.info(f"Đã cập nhật mô hình collaborative filtering (version {self.model_version})")

        except Exception as e:
            logger.error(f"Lỗi cập nhật mô hình: {str(e)}")

    def _update_svd_model(self, new_interactions):
        """
        Cập nhật mô hình SVD với dữ liệu mới.

        Args:
            new_interactions: Dữ liệu tương tác mới
        """
        try:
            # Nếu chưa có mô hình, huấn luyện từ đầu
            if self.model is None:
                return self._train_model_internal(new_interactions)

            # Cập nhật ma trận user-item
            df = pd.DataFrame(new_interactions)

            # Thêm user_id và song_id mới vào mapping
            for user_id in df['user_id'].unique():
                if user_id not in self.user_mapping:
                    new_idx = len(self.user_mapping)
                    self.user_mapping[user_id] = new_idx
                    self.reverse_user_mapping[new_idx] = user_id

            for song_id in df['song_id'].unique():
                if song_id not in self.song_mapping:
                    new_idx = len(self.song_mapping)
                    self.song_mapping[song_id] = new_idx
                    self.reverse_song_mapping[new_idx] = song_id

            # Cập nhật user-item matrix
            n_users = len(self.user_mapping)
            n_songs = len(self.song_mapping)

            # Nếu kích thước ma trận đã thay đổi, huấn luyện lại
            if n_users > self.user_factors.shape[0] or n_songs > self.song_factors.shape[0]:
                logger.info("Kích thước ma trận đã thay đổi, đang huấn luyện lại mô hình SVD...")
                return self._train_model_internal(new_interactions, full_retrain=True)

            # Nếu không có quá nhiều dữ liệu mới, chỉ cập nhật trọng số
            # (Trong triển khai thực tế, sẽ cần thuật toán incremental SVD
            # hoặc Alternating Least Squares (ALS) với Coordinate Descent)
            if len(new_interactions) < 1000:
                logger.info("Dữ liệu cập nhật nhỏ, bỏ qua cập nhật SVD incremental")
                return

            # Với dữ liệu lớn, huấn luyện lại mô hình
            return self._train_model_internal(new_interactions, full_retrain=True)

        except Exception as e:
            logger.error(f"Lỗi cập nhật mô hình SVD: {str(e)}")

    async def recommend(
            self,
            song_id: str,
            user_id: str,
            user_interactions: List[Dict],
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Đưa ra gợi ý bài hát dựa trên bài hát đầu vào và hành vi người dùng.

        Args:
            song_id: ID bài hát gốc
            user_id: ID người dùng
            user_interactions: Dữ liệu tương tác lịch sử của người dùng
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số tương đồng)
        """
        try:
            # Thử sử dụng NCF nếu được bật
            if self.use_ncf:
                recommendations = await self._recommend_with_ncf(song_id, user_id, user_interactions, limit)
                if recommendations:
                    return recommendations
                logger.info("Không thể gợi ý với NCF, chuyển sang SVD...")

            # Nếu người dùng không có đủ dữ liệu tương tác, sử dụng song similarity
            if not user_interactions or len(user_interactions) < 5:
                logger.info(f"User {user_id} has insufficient interactions. Using song similarity instead.")
                return await self._item_based_recommendation(song_id, limit)

            # Kiểm tra model đã được training chưa
            if self.model is None:
                logger.info("Collaborative filtering model not trained. Training now...")
                await self._train_model()

            # Nếu model vẫn là None sau khi train, có lỗi train
            if self.model is None:
                logger.error("Failed to train collaborative filtering model")
                return []

            # Lấy song_idx trong mô hình
            if song_id not in self.song_mapping:
                logger.warning(f"Song {song_id} not found in collaborative model")
                return await self._item_based_recommendation(song_id, limit)

            song_idx = self.song_mapping[song_id]

            # User-based collaborative filtering
            # Kiểm tra xem user_id đã có trong model chưa
            if user_id in self.user_mapping:
                # Lấy gợi ý dựa trên người dùng hiện tại
                user_idx = self.user_mapping[user_id]
                recommendations = await self._user_based_recommendation(user_idx, song_id, limit)
            else:
                # Nếu người dùng mới, dùng tính năng của bài hát
                recommendations = await self._feature_based_recommendation(song_idx, limit)

            return recommendations

        except Exception as e:
            logger.error(f"Error in collaborative filtering: {str(e)}")
            return []

    async def _recommend_with_ncf(
            self,
            song_id: str,
            user_id: str,
            user_interactions: List[Dict],
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Đưa ra gợi ý sử dụng Neural Collaborative Filtering.

        Args:
            song_id: ID bài hát gốc
            user_id: ID người dùng
            user_interactions: Dữ liệu tương tác lịch sử
            limit: Số lượng gợi ý cần lấy

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số)
        """
        try:
            # Cập nhật tương tác người dùng hiện tại vào mô hình
            if user_interactions and self.use_incremental:
                for interaction in user_interactions:
                    # Chuẩn bị dữ liệu cho NCF
                    ncf_interaction = {
                        "user_id": interaction["user_id"],
                        "song_id": interaction["song_id"],
                        "play_count": interaction.get("play_count", 0),
                        "liked": interaction.get("liked", False)
                    }
                    # Thêm vào buffer của NCF
                    ncf_recommender.add_interaction(ncf_interaction)

            # Lấy danh sách bài hát ứng viên
            from app.db.repositories.song_repository import SongRepository
            song_repo = SongRepository()

            # Lấy bài hát tương tự dựa trên thể loại và nghệ sĩ
            candidate_songs = await song_repo.get_similar_songs(song_id, limit * 3)
            candidate_ids = [s_id for s_id, _ in candidate_songs]

            # Thêm bài hát trending nếu cần
            if len(candidate_ids) < limit * 3:
                from app.db.repositories.interaction_repository import InteractionRepository
                interaction_repo = InteractionRepository()
                trending_songs = await interaction_repo.get_trending_songs(limit * 2)
                for s_id, _ in trending_songs:
                    if s_id not in candidate_ids and s_id != song_id:
                        candidate_ids.append(s_id)

            # Đảm bảo bài hát gốc không nằm trong ứng viên
            if song_id in candidate_ids:
                candidate_ids.remove(song_id)

            # Gọi hàm gợi ý từ NCF
            recommendations = ncf_recommender.recommend(
                song_id=song_id,
                user_id=user_id,
                candidate_songs=candidate_ids,
                limit=limit
            )

            return recommendations

        except Exception as e:
            logger.error(f"Lỗi trong gợi ý NCF: {str(e)}")
            return []

    async def _train_model(self, n_factors: int = 20):
        """
        Huấn luyện mô hình SVD dựa trên dữ liệu tương tác hiện có.

        Args:
            n_factors: Số lượng nhân tố ẩn trong SVD
        """
        try:
            # Lấy tất cả dữ liệu tương tác từ DB
            from app.db.repositories.interaction_repository import InteractionRepository
            interaction_repo = InteractionRepository()

            interactions = await interaction_repo.get_all_interactions()
            if not interactions:
                logger.warning("No interactions found to train model")
                return

            # Gọi hàm huấn luyện nội bộ
            self._train_model_internal(interactions, n_factors)

            # Cập nhật thời gian train
            self.last_training_time = datetime.now()
            self.model_version = 1

            logger.info(f"Collaborative filtering model trained successfully (version {self.model_version})")

            # Huấn luyện mô hình NCF nếu được bật
            if self.use_ncf:
                try:
                    logger.info("Đang huấn luyện mô hình NCF...")
                    # Chuẩn bị dữ liệu cho NCF
                    ncf_interactions = []
                    for interaction in interactions:
                        ncf_interaction = {
                            "user_id": interaction["user_id"],
                            "song_id": interaction["song_id"],
                            "play_count": interaction.get("play_count", 0),
                            "liked": interaction.get("liked", False)
                        }
                        ncf_interactions.append(ncf_interaction)

                    # Huấn luyện mô hình NCF
                    ncf_recommender.bulk_train(ncf_interactions)
                    logger.info("Đã huấn luyện xong mô hình NCF")
                except Exception as e:
                    logger.error(f"Lỗi khi huấn luyện mô hình NCF: {str(e)}")

        except Exception as e:
            logger.error(f"Error training collaborative filtering model: {str(e)}")
            self.model = None

    def _train_model_internal(self, interactions, n_factors: int = 20, full_retrain: bool = False):
        """
        Huấn luyện mô hình SVD với dữ liệu tương tác.

        Args:
            interactions: Dữ liệu tương tác
            n_factors: Số lượng nhân tố ẩn
            full_retrain: Có huấn luyện lại toàn bộ hay không
        """
        if not interactions:
            logger.warning("No interactions provided for training")
            return

        # Tạo DataFrame từ dữ liệu
        df = pd.DataFrame(interactions)

        # Tạo map user_id và song_id sang indices
        if full_retrain or self.model is None:
            # Nếu huấn luyện lại hoàn toàn, xây dựng mapping mới
            unique_users = df['user_id'].unique()
            unique_songs = df['song_id'].unique()

            self.user_mapping = {user: i for i, user in enumerate(unique_users)}
            self.song_mapping = {song: i for i, song in enumerate(unique_songs)}
            self.reverse_user_mapping = {i: user for user, i in self.user_mapping.items()}
            self.reverse_song_mapping = {i: song for song, i in self.song_mapping.items()}
        else:
            # Nếu incremental, cập nhật mapping với dữ liệu mới
            for user_id in df['user_id'].unique():
                if user_id not in self.user_mapping:
                    new_idx = len(self.user_mapping)
                    self.user_mapping[user_id] = new_idx
                    self.reverse_user_mapping[new_idx] = user_id

            for song_id in df['song_id'].unique():
                if song_id not in self.song_mapping:
                    new_idx = len(self.song_mapping)
                    self.song_mapping[song_id] = new_idx
                    self.reverse_song_mapping[new_idx] = song_id

        # Chuyển đổi df thành ma trận sparse
        user_indices = df['user_id'].map(self.user_mapping).values
        song_indices = df['song_id'].map(self.song_mapping).values

        # Tính rating dựa trên tương tác
        ratings = []
        for _, interaction in df.iterrows():
            # Play = 3, Like = 5, Follow artist = 2
            rating = 0
            if interaction.get("play_count", 0) > 0:
                rating += min(3, interaction["play_count"] / 5)  # Max 3 điểm cho play
            if interaction.get("liked", False):
                rating += 5  # 5 điểm cho like
            if interaction.get("follows_artist", False):
                rating += 2  # 2 điểm cho follow artist
            ratings.append(rating)

        n_users = len(self.user_mapping)
        n_songs = len(self.song_mapping)

        # Tạo ma trận sparse
        user_item_matrix = csr_matrix((ratings, (user_indices, song_indices)), shape=(n_users, n_songs))

        # Áp dụng SVD
        U, sigma, Vt = svds(user_item_matrix, k=n_factors)

        # Tạo ma trận diagonal sigma
        sigma_diag = np.diag(sigma)

        # Lưu model components
        self.user_factors = U.dot(sigma_diag)
        self.song_factors = Vt.T
        self.model = {
            'U': U,
            'sigma': sigma,
            'Vt': Vt,
            'user_mapping': self.user_mapping,
            'song_mapping': self.song_mapping,
            'reverse_user_mapping': self.reverse_user_mapping,
            'reverse_song_mapping': self.reverse_song_mapping
        }

        logger.info(f"Collaborative filtering model trained with {n_users} users and {n_songs} songs")