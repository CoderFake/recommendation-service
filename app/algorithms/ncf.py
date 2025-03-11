from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import time
from datetime import datetime
import threading
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from pathlib import Path

from app.core.logging import logger
from app.core.config import settings


class NCFDataset(Dataset):
    """Dataset cho mô hình NCF."""

    def __init__(self, user_indices, item_indices, labels):
        """
        Khởi tạo NCF Dataset.

        Args:
            user_indices: Chỉ mục của người dùng
            item_indices: Chỉ mục của bài hát
            labels: Nhãn (giá trị tương tác)
        """
        self.user_indices = torch.LongTensor(user_indices)
        self.item_indices = torch.LongTensor(item_indices)
        self.labels = torch.FloatTensor(labels)

    def __len__(self):
        return len(self.user_indices)

    def __getitem__(self, idx):
        return self.user_indices[idx], self.item_indices[idx], self.labels[idx]


class NCF(nn.Module):
    """
    Mô hình Neural Collaborative Filtering.

    Triển khai mô hình NCF với các lớp nhúng người dùng và bài hát,
    kết hợp với Multi-Layer Perceptron (MLP).
    """

    def __init__(
            self,
            num_users: int,
            num_items: int,
            embedding_size: int = 32,
            layers: List[int] = [64, 32, 16, 8],
            dropout: float = 0.2
    ):
        """
        Khởi tạo mô hình NCF.

        Args:
            num_users: Số lượng người dùng trong hệ thống
            num_items: Số lượng bài hát trong hệ thống
            embedding_size: Kích thước vector nhúng
            layers: Cấu trúc các lớp ẩn của MLP
            dropout: Tỷ lệ dropout để tránh overfitting
        """
        super(NCF, self).__init__()

        # Embedding layers
        self.user_embedding = nn.Embedding(num_users, embedding_size)
        self.item_embedding = nn.Embedding(num_items, embedding_size)

        # GMF (Generalized Matrix Factorization) part
        self.gmf_user_embedding = nn.Embedding(num_users, embedding_size)
        self.gmf_item_embedding = nn.Embedding(num_items, embedding_size)

        # MLP (Multi-Layer Perceptron) part
        self.mlp_layers = nn.ModuleList()
        input_size = 2 * embedding_size

        for i, next_size in enumerate(layers):
            self.mlp_layers.append(nn.Linear(input_size, next_size))
            self.mlp_layers.append(nn.ReLU())
            self.mlp_layers.append(nn.Dropout(p=dropout))
            input_size = next_size

        # Lớp đầu ra
        self.output_layer = nn.Linear(layers[-1] + embedding_size, 1)
        self.sigmoid = nn.Sigmoid()

        # Khởi tạo trọng số
        self._init_weights()

    def _init_weights(self):
        """Khởi tạo trọng số của mô hình."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.01)

    def forward(self, user_indices, item_indices):
        """
        Forward pass của mô hình.

        Args:
            user_indices: Chỉ mục người dùng
            item_indices: Chỉ mục bài hát

        Returns:
            torch.Tensor: Giá trị dự đoán
        """
        # GMF part
        gmf_user_emb = self.gmf_user_embedding(user_indices)
        gmf_item_emb = self.gmf_item_embedding(item_indices)
        gmf_vector = gmf_user_emb * gmf_item_emb

        # MLP part
        mlp_user_emb = self.user_embedding(user_indices)
        mlp_item_emb = self.item_embedding(item_indices)
        mlp_vector = torch.cat([mlp_user_emb, mlp_item_emb], dim=-1)

        for layer in self.mlp_layers:
            mlp_vector = layer(mlp_vector)

        # Kết hợp GMF và MLP
        prediction_vector = torch.cat([gmf_vector, mlp_vector], dim=-1)
        prediction = self.output_layer(prediction_vector)

        return self.sigmoid(prediction).squeeze()


class NCFRecommender:
    """
    Recommender sử dụng Neural Collaborative Filtering với Incremental Learning.

    Lớp này cung cấp giao diện để huấn luyện, cập nhật và thực hiện gợi ý
    bằng mô hình Neural Collaborative Filtering.
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
        """Khởi tạo NCF Recommender."""
        if self._initialized:
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.user_encoder = LabelEncoder()
        self.item_encoder = LabelEncoder()
        self.batch_size = 64
        self.learning_rate = 0.001
        self.num_epochs = 20
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)

        # Các thông số cho incremental learning
        self.buffer = []
        self.buffer_size = 1000
        self.update_interval = 100  # Số lượng mẫu mới để kích hoạt cập nhật
        self.last_update_time = datetime.now()
        self.update_frequency = 300  # Seconds (5 phút)

        # Khóa cho đồng bộ hóa
        self.model_lock = threading.Lock()

        # Khởi tạo hoặc tải mô hình
        self._load_or_init_model()

        # Bắt đầu thread cho incremental learning
        self._start_incremental_learning_thread()

        self._initialized = True

    def _load_or_init_model(self):
        """Tải mô hình hiện có hoặc khởi tạo mô hình mới."""
        model_path = self.model_dir / "ncf_model.pt"
        encoders_path = self.model_dir / "ncf_encoders.joblib"

        try:
            if model_path.exists() and encoders_path.exists():
                # Tải encoders
                encoders = joblib.load(encoders_path)
                self.user_encoder = encoders["user_encoder"]
                self.item_encoder = encoders["item_encoder"]

                # Tạo model với kích thước đúng
                num_users = len(self.user_encoder.classes_)
                num_items = len(self.item_encoder.classes_)

                self.model = NCF(num_users, num_items)
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.model.to(self.device)
                self.model.eval()

                logger.info(f"Đã tải mô hình NCF với {num_users} người dùng và {num_items} bài hát")
            else:
                logger.info("Không tìm thấy mô hình NCF hiện có. Sẽ tạo mô hình mới khi có dữ liệu.")
                self.model = None

        except Exception as e:
            logger.error(f"Lỗi khi tải mô hình NCF: {str(e)}")
            self.model = None

    def _start_incremental_learning_thread(self):
        """Bắt đầu thread nền cho incremental learning."""

        def update_thread():
            while True:
                time.sleep(10)  # Kiểm tra mỗi 10 giây
                self._check_and_update_model()

        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()
        logger.info("Đã bắt đầu thread incremental learning")

    def _check_and_update_model(self):
        """Kiểm tra và cập nhật mô hình nếu cần."""
        # Kiểm tra xem có đủ dữ liệu mới không
        if len(self.buffer) >= self.update_interval:
            current_time = datetime.now()
            # Hoặc đã đến thời gian cập nhật định kỳ
            if (current_time - self.last_update_time).total_seconds() >= self.update_frequency:
                logger.info(f"Đang cập nhật mô hình NCF với {len(self.buffer)} mẫu mới")
                self._update_model_incremental()
                self.last_update_time = current_time

    def _prepare_data(self, interactions):
        """
        Chuẩn bị dữ liệu cho mô hình NCF.

        Args:
            interactions: Danh sách các tương tác

        Returns:
            Tuple: (user_indices, item_indices, labels)
        """
        if not interactions:
            return [], [], []

        df = pd.DataFrame(interactions)

        # Mã hóa người dùng và bài hát
        if self.model is None:
            # Khởi tạo encoders với dữ liệu mới
            self.user_encoder.fit(df["user_id"].unique())
            self.item_encoder.fit(df["song_id"].unique())
        else:
            # Cập nhật encoders với dữ liệu mới
            # Lấy các lớp hiện tại
            current_users = set(self.user_encoder.classes_)
            current_items = set(self.item_encoder.classes_)

            # Lấy các giá trị mới
            new_users = set(df["user_id"].unique()) - current_users
            new_items = set(df["song_id"].unique()) - current_items

            # Cập nhật encoders nếu có giá trị mới
            if new_users:
                self.user_encoder.classes_ = np.append(self.user_encoder.classes_, list(new_users))

            if new_items:
                self.item_encoder.classes_ = np.append(self.item_encoder.classes_, list(new_items))

        # Chuyển đổi thành chỉ mục
        user_indices = self.user_encoder.transform(df["user_id"])
        item_indices = self.item_encoder.transform(df["song_id"])

        # Chuẩn bị nhãn (thường từ 0-1 dựa trên loại tương tác)
        labels = []
        for _, row in df.iterrows():
            # Tính toán label dựa trên tương tác
            score = 0.0
            if row.get("play_count", 0) > 0:
                score += min(1.0, row["play_count"] / 10.0) * 0.5
            if row.get("liked", False):
                score += 0.5
            labels.append(min(1.0, score))

        return user_indices, item_indices, labels

    def add_interaction(self, interaction):
        """
        Thêm tương tác mới vào buffer.

        Args:
            interaction: Thông tin tương tác mới
        """
        self.buffer.append(interaction)

        # Cập nhật mô hình nếu buffer đầy
        if len(self.buffer) >= self.buffer_size:
            self._update_model_incremental()

    def _update_model_incremental(self):
        """Cập nhật mô hình với dữ liệu mới từ buffer."""
        if not self.buffer:
            return

        with self.model_lock:
            user_indices, item_indices, labels = self._prepare_data(self.buffer)

            if not user_indices:
                self.buffer = []
                return

            # Nếu chưa có mô hình, tạo mô hình mới
            if self.model is None:
                num_users = len(self.user_encoder.classes_)
                num_items = len(self.item_encoder.classes_)

                self.model = NCF(num_users, num_items)
                self.model.to(self.device)
                logger.info(f"Đã tạo mô hình NCF mới với {num_users} người dùng và {num_items} bài hát")
            else:
                # Cập nhật kích thước embeddings nếu có người dùng/bài hát mới
                current_num_users = self.model.user_embedding.weight.shape[0]
                current_num_items = self.model.item_embedding.weight.shape[0]

                new_num_users = len(self.user_encoder.classes_)
                new_num_items = len(self.item_encoder.classes_)

                if new_num_users > current_num_users or new_num_items > current_num_items:
                    # Lưu weights hiện tại
                    old_user_weights = self.model.user_embedding.weight.data
                    old_item_weights = self.model.item_embedding.weight.data
                    old_gmf_user_weights = self.model.gmf_user_embedding.weight.data
                    old_gmf_item_weights = self.model.gmf_item_embedding.weight.data

                    # Tạo mô hình mới với kích thước lớn hơn
                    new_model = NCF(new_num_users, new_num_items)

                    # Sao chép weights
                    new_model.user_embedding.weight.data[:current_num_users] = old_user_weights
                    new_model.item_embedding.weight.data[:current_num_items] = old_item_weights
                    new_model.gmf_user_embedding.weight.data[:current_num_users] = old_gmf_user_weights
                    new_model.gmf_item_embedding.weight.data[:current_num_items] = old_gmf_item_weights

                    # Sao chép các trọng số của các lớp MLP
                    for i in range(0, len(self.model.mlp_layers), 3):
                        new_model.mlp_layers[i].weight.data = self.model.mlp_layers[i].weight.data.clone()
                        new_model.mlp_layers[i].bias.data = self.model.mlp_layers[i].bias.data.clone()

                    # Sao chép trọng số lớp đầu ra
                    new_model.output_layer.weight.data = self.model.output_layer.weight.data.clone()
                    new_model.output_layer.bias.data = self.model.output_layer.bias.data.clone()

                    # Thay thế mô hình cũ
                    self.model = new_model
                    self.model.to(self.device)

                    logger.info(f"Đã mở rộng mô hình NCF tới {new_num_users} người dùng và {new_num_items} bài hát")

            # Chuẩn bị dataset
            dataset = NCFDataset(user_indices, item_indices, labels)
            dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

            # Cấu hình huấn luyện
            optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
            criterion = nn.BCELoss()

            # Huấn luyện
            self.model.train()
            for epoch in range(self.num_epochs):
                total_loss = 0
                for batch_user, batch_item, batch_label in dataloader:
                    batch_user = batch_user.to(self.device)
                    batch_item = batch_item.to(self.device)
                    batch_label = batch_label.to(self.device)

                    # Forward
                    optimizer.zero_grad()
                    output = self.model(batch_user, batch_item)
                    loss = criterion(output, batch_label)

                    # Backward
                    loss.backward()
                    optimizer.step()

                    total_loss += loss.item()

                # Ghi log
                if (epoch + 1) % 5 == 0 or epoch == 0:
                    logger.info(f"Epoch {epoch + 1}/{self.num_epochs}, Loss: {total_loss / len(dataloader):.4f}")

            # Lưu mô hình
            self._save_model()

            # Xóa buffer
            self.buffer = []

            # Chuyển mô hình về chế độ đánh giá
            self.model.eval()

            logger.info("Đã cập nhật mô hình NCF thành công")

    def _save_model(self):
        """Lưu mô hình và encoders."""
        try:
            model_path = self.model_dir / "ncf_model.pt"
            encoders_path = self.model_dir / "ncf_encoders.joblib"

            # Lưu mô hình
            torch.save(self.model.state_dict(), model_path)

            # Lưu encoders
            encoders = {
                "user_encoder": self.user_encoder,
                "item_encoder": self.item_encoder
            }
            joblib.dump(encoders, encoders_path)

            logger.info(f"Đã lưu mô hình NCF và encoders vào {self.model_dir}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu mô hình NCF: {str(e)}")

    def recommend(
            self,
            song_id: str,
            user_id: str,
            candidate_songs: List[str],
            limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Gợi ý bài hát cho người dùng.

        Args:
            song_id: ID bài hát gốc
            user_id: ID người dùng
            candidate_songs: Danh sách các bài hát ứng viên
            limit: Số lượng gợi ý trả về

        Returns:
            List[Tuple[str, float]]: Danh sách (song_id, điểm số)
        """
        if self.model is None:
            logger.warning("Mô hình NCF chưa được huấn luyện")
            return []

        with self.model_lock:
            try:
                # Kiểm tra xem người dùng và bài hát có trong mô hình chưa
                if user_id not in self.user_encoder.classes_:
                    logger.warning(f"Người dùng {user_id} không có trong mô hình")
                    return []

                # Mã hóa người dùng
                user_idx = self.user_encoder.transform([user_id])[0]

                # Chuẩn bị dữ liệu gợi ý
                valid_songs = [s for s in candidate_songs if s in self.item_encoder.classes_]
                if not valid_songs:
                    logger.warning("Không có bài hát hợp lệ để gợi ý")
                    return []

                # Mã hóa bài hát
                item_indices = self.item_encoder.transform(valid_songs)

                # Chuẩn bị dữ liệu cho mô hình
                users = torch.LongTensor([user_idx] * len(item_indices)).to(self.device)
                items = torch.LongTensor(item_indices).to(self.device)

                # Dự đoán
                self.model.eval()
                with torch.no_grad():
                    scores = self.model(users, items).cpu().numpy()

                # Tạo kết quả
                song_scores = list(zip(valid_songs, scores))

                # Sắp xếp theo điểm giảm dần
                song_scores.sort(key=lambda x: x[1], reverse=True)

                # Trả về top-k
                return song_scores[:limit]

            except Exception as e:
                logger.error(f"Lỗi khi gợi ý với mô hình NCF: {str(e)}")
                return []

    def bulk_train(self, interactions: List[Dict]):
        """
        Huấn luyện lại mô hình với toàn bộ dữ liệu.

        Args:
            interactions: Danh sách các tương tác người dùng
        """
        if not interactions:
            logger.warning("Không có dữ liệu tương tác để huấn luyện")
            return

        with self.model_lock:
            try:
                # Chuẩn bị dữ liệu
                user_indices, item_indices, labels = self._prepare_data(interactions)

                # Tạo mô hình mới
                num_users = len(self.user_encoder.classes_)
                num_items = len(self.item_encoder.classes_)

                self.model = NCF(num_users, num_items)
                self.model.to(self.device)

                # Huấn luyện mô hình
                dataset = NCFDataset(user_indices, item_indices, labels)
                dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

                optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
                criterion = nn.BCELoss()

                self.model.train()
                for epoch in range(self.num_epochs):
                    total_loss = 0
                    for batch_user, batch_item, batch_label in dataloader:
                        batch_user = batch_user.to(self.device)
                        batch_item = batch_item.to(self.device)
                        batch_label = batch_label.to(self.device)

                        # Forward
                        optimizer.zero_grad()
                        output = self.model(batch_user, batch_item)
                        loss = criterion(output, batch_label)

                        # Backward
                        loss.backward()
                        optimizer.step()

                        total_loss += loss.item()

                    # Ghi log
                    if (epoch + 1) % 5 == 0 or epoch == 0:
                        logger.info(f"Epoch {epoch + 1}/{self.num_epochs}, Loss: {total_loss / len(dataloader):.4f}")

                # Lưu mô hình
                self._save_model()

                # Chuyển mô hình về chế độ đánh giá
                self.model.eval()

                logger.info(f"Đã huấn luyện lại mô hình NCF với {len(interactions)} tương tác")

            except Exception as e:
                logger.error(f"Lỗi khi huấn luyện mô hình NCF: {str(e)}")


# Tạo instance toàn cục
ncf_recommender = NCFRecommender()