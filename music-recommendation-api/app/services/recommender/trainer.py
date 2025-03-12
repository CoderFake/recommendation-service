import logging
import os
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple, Optional, Any, Union

from app.core.config import settings
from app.services.recommender.models import NCF, NCFDataset, ContentBasedModel, HybridRecommender
from app.services.recommender.data import RecommenderDataManager

logger = logging.getLogger(__name__)


class ModelTrainer:

    def __init__(
            self,
            data_manager: RecommenderDataManager,
            model_dir: str = "models",
            device: str = "cpu",
            embedding_dim: int = 32,
            hidden_layers: List[int] = [64, 32, 16, 8],
            learning_rate: float = 0.001,
            batch_size: int = 256,
            num_epochs: int = 10,
            weight_decay: float = 1e-5,
            early_stopping_patience: int = 3,
            collaborative_weight: float = 0.7,
            content_weight: float = 0.3
    ):
        self.data_manager = data_manager
        self.model_dir = Path(model_dir)
        self.device = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")

        # Training hyperparameters
        self.embedding_dim = embedding_dim
        self.hidden_layers = hidden_layers
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.weight_decay = weight_decay
        self.early_stopping_patience = early_stopping_patience

        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight

        self.ncf_model = None
        self.content_model = None
        self.hybrid_model = None

        os.makedirs(self.model_dir, exist_ok=True)

    def _init_models(self, force_reinit: bool = False):
        if not self.data_manager.data_initialized:
            logger.warning("Data not initialized, cannot initialize models")
            return

        if self.ncf_model is None or force_reinit:
            self.ncf_model = NCF(
                n_users=self.data_manager.n_users,
                n_items=self.data_manager.n_items,
                embedding_dim=self.embedding_dim,
                layers=self.hidden_layers
            ).to(self.device)
            logger.info(
                f"Initialized NCF model with {self.data_manager.n_users} users and {self.data_manager.n_items} items")

        if (self.content_model is None or force_reinit) and self.data_manager.item_features_matrix is not None:
            self.content_model = ContentBasedModel(
                n_items=self.data_manager.n_items,
                feature_dim=self.data_manager.feature_dim
            )
            self.content_model.set_item_features(self.data_manager.item_features_matrix)
            logger.info(f"Initialized content-based model with {self.data_manager.feature_dim} features")

        if (self.ncf_model is not None and
                self.content_model is not None and
                (self.hybrid_model is None or force_reinit)):
            self.hybrid_model = HybridRecommender(
                ncf_model=self.ncf_model,
                content_model=self.content_model,
                collaborative_weight=self.collaborative_weight,
                content_weight=self.content_weight
            )
            logger.info(
                f"Initialized hybrid model with weights: CF={self.collaborative_weight}, CB={self.content_weight}")

    def train_ncf_model(self, validation_split: float = 0.1):
        logger.info("Starting NCF model training")
        start_time = time.time()

        self._init_models()

        if self.ncf_model is None:
            logger.error("NCF model not initialized, cannot train")
            return {"error": "Model not initialized"}

        train_data = self.data_manager.get_training_data()
        if not train_data:
            logger.warning("No training data available")
            return {"error": "No training data"}

        np.random.shuffle(train_data)
        split_idx = int(len(train_data) * (1 - validation_split))
        train_interactions = train_data[:split_idx]
        val_interactions = train_data[split_idx:]

        logger.info(f"Training with {len(train_interactions)} samples, validating with {len(val_interactions)}")

        train_dataset = NCFDataset(train_interactions)
        val_dataset = NCFDataset(val_interactions)

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=4
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=4
        )

        # Loss function and optimizer
        criterion = nn.BCELoss()
        optimizer = optim.Adam(
            self.ncf_model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay
        )

        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        history = {
            "train_loss": [],
            "val_loss": [],
            "epoch_times": []
        }

        self.ncf_model.train()
        for epoch in range(self.num_epochs):
            epoch_start = time.time()

            # Training
            train_loss = 0.0
            self.ncf_model.train()

            for batch in train_loader:
                user_indices = batch['user'].to(self.device)
                item_indices = batch['item'].to(self.device)
                ratings = batch['rating'].to(self.device)

                # Zero gradients
                optimizer.zero_grad()

                # Forward pass
                predictions = self.ncf_model(user_indices, item_indices)

                # Compute loss
                loss = criterion(predictions, ratings)

                # Backward pass and optimize
                loss.backward()
                optimizer.step()

                train_loss += loss.item()

            train_loss /= len(train_loader)

            # Validation
            val_loss = 0.0
            self.ncf_model.eval()

            with torch.no_grad():
                for batch in val_loader:
                    user_indices = batch['user'].to(self.device)
                    item_indices = batch['item'].to(self.device)
                    ratings = batch['rating'].to(self.device)

                    # Forward pass
                    predictions = self.ncf_model(user_indices, item_indices)

                    # Compute loss
                    loss = criterion(predictions, ratings)
                    val_loss += loss.item()

            val_loss /= len(val_loader)

            epoch_time = time.time() - epoch_start
            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)
            history["epoch_times"].append(epoch_time)

            logger.info(f"Epoch {epoch + 1}/{self.num_epochs} - "
                        f"Train Loss: {train_loss:.4f}, "
                        f"Val Loss: {val_loss:.4f}, "
                        f"Time: {epoch_time:.2f}s")

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0

                self._save_ncf_model(f"ncf_best.pt")
            else:
                patience_counter += 1

                if patience_counter >= self.early_stopping_patience:
                    logger.info(f"Early stopping at epoch {epoch + 1}")
                    break

        self._save_ncf_model(f"ncf_final.pt")

        total_time = time.time() - start_time
        logger.info(f"NCF training completed in {total_time:.2f}s")

        history["total_time"] = total_time
        history["best_val_loss"] = best_val_loss
        history["epochs_completed"] = len(history["train_loss"])

        return history

    def _save_ncf_model(self, filename: str):
        if self.ncf_model is None:
            logger.warning("No model to save")
            return

        file_path = self.model_dir / filename

        save_dict = {
            "state_dict": self.ncf_model.state_dict(),
            "architecture": {
                "n_users": self.ncf_model.n_users,
                "n_items": self.ncf_model.n_items,
                "embedding_dim": self.ncf_model.embedding_dim,
                "layers": self.ncf_model.layers
            },
            "user_mapping": self.data_manager.user_mapping,
            "item_mapping": self.data_manager.item_mapping,
            "reverse_user_mapping": self.data_manager.reverse_user_mapping,
            "reverse_item_mapping": self.data_manager.reverse_item_mapping
        }

        torch.save(save_dict, file_path)
        logger.info(f"Saved NCF model to {file_path}")

    def load_ncf_model(self, filename: str) -> bool:
        file_path = self.model_dir / filename

        if not file_path.exists():
            logger.warning(f"Model file {file_path} not found")
            return False

        try:
            save_dict = torch.load(file_path, map_location=self.device)

            architecture = save_dict["architecture"]

            self.ncf_model = NCF(
                n_users=architecture["n_users"],
                n_items=architecture["n_items"],
                embedding_dim=architecture["embedding_dim"],
                layers=architecture["layers"]
            ).to(self.device)

            self.ncf_model.load_state_dict(save_dict["state_dict"])

            # Update data manager mappings
            self.data_manager.user_mapping = save_dict["user_mapping"]
            self.data_manager.item_mapping = save_dict["item_mapping"]
            self.data_manager.reverse_user_mapping = save_dict["reverse_user_mapping"]
            self.data_manager.reverse_item_mapping = save_dict["reverse_item_mapping"]

            # Update metadata in data manager
            self.data_manager.n_users = architecture["n_users"]
            self.data_manager.n_items = architecture["n_items"]
            self.data_manager.data_initialized = True

            logger.info(f"Loaded NCF model from {file_path}")

            self._init_models()

            return True
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False

    def update_model_incrementally(self, user_id: int, song_id: int, rating: float):
        if self.ncf_model is None:
            logger.warning("NCF model not initialized, cannot update incrementally")
            return

        # Add or update interaction in data manager
        user_idx, item_idx = self.data_manager.update_interaction(user_id, song_id, rating)

        # Perform one step of SGD update for this interaction
        self.ncf_model.train()
        user_tensor = torch.tensor([user_idx], dtype=torch.long).to(self.device)
        item_tensor = torch.tensor([item_idx], dtype=torch.long).to(self.device)
        rating_tensor = torch.tensor([rating], dtype=torch.float).to(self.device)

        # Loss function and optimizer
        criterion = nn.BCELoss()
        optimizer = optim.Adam(
            self.ncf_model.parameters(),
            lr=self.learning_rate * 0.1,
            weight_decay=self.weight_decay
        )

        # Zero gradients
        optimizer.zero_grad()

        # Forward pass
        prediction = self.ncf_model(user_tensor, item_tensor)

        # Compute loss
        loss = criterion(prediction, rating_tensor)

        loss.backward()
        optimizer.step()

        logger.debug(
            f"Incremental update for user {user_id}, song {song_id} with rating {rating:.2f}, loss: {loss.item():.4f}")

    def process_event(self, user_id: int, song_id: int, event_type: str, context: Optional[Dict[str, Any]] = None):

        rating = 0.0

        if event_type.lower() == "play":
            rating = 0.6
        elif event_type.lower() == "like":
            rating = 1.0
        elif event_type.lower() == "unlike":
            rating = 0.0
        elif event_type.lower() == "skip":
            rating = 0.2
        elif event_type.lower() == "save":
            rating = 0.8
        elif event_type.lower() == "unsave":
            rating = 0.3

        self.update_model_incrementally(user_id, song_id, rating)

    def get_recommendations(
            self,
            user_id: int,
            n: int = 10,
            exclude_items: Optional[List[int]] = None,
            include_liked: bool = False,
            collaborative_weight: Optional[float] = None,
            content_weight: Optional[float] = None
    ) -> List[Tuple[int, float, Dict[str, float]]]:

        self._init_models()

        if self.hybrid_model is None:
            logger.warning("Hybrid model not initialized, cannot get recommendations")
            return []

        if collaborative_weight is not None and content_weight is not None:
            self.hybrid_model.set_weights(collaborative_weight, content_weight)

        user_idx = self.data_manager.get_user_idx(user_id)
        if user_idx is None:
            logger.warning(f"User {user_id} not found in mapping")
            return []

        user_history = self.data_manager.get_user_history(user_id)

        exclude_items_set = set()
        if exclude_items:
            for item_id in exclude_items:
                item_idx = self.data_manager.get_item_idx(item_id)
                if item_idx is not None:
                    exclude_items_set.add(item_idx)

        if not include_liked:
            liked_items = self.data_manager.user_positive_items.get(user_idx, set())
            exclude_items_set.update(liked_items)

        recommendations = self.hybrid_model.recommend_items(
            user_idx=user_idx,
            user_history=user_history,
            n=n,
            exclude_items=list(exclude_items_set)
        )

        result = []
        for item_idx, score in recommendations:
            song_id = self.data_manager.get_item_id(item_idx)
            if song_id is None:
                continue

            cf_score = self.ncf_model.predict(user_idx, item_idx)

            cb_scores = self.content_model.predict_item_scores(user_history)
            cb_score = cb_scores[item_idx]

            relevance_factors = {
                "collaborative": cf_score,
                "content_based": cb_score,
            }

            result.append((song_id, score, relevance_factors))

        return result

    def get_similar_songs(self, song_id: int, n: int = 10) -> List[Tuple[int, float]]:

        self._init_models()

        if self.content_model is None:
            logger.warning("Content model not initialized, cannot get similar songs")
            return []

        item_idx = self.data_manager.get_item_idx(song_id)
        if item_idx is None:
            logger.warning(f"Song {song_id} not found in mapping")
            return []

        similar_items = self.content_model.get_similar_items(item_idx, n=n)

        result = []
        for item_idx, similarity in similar_items:
            similar_song_id = self.data_manager.get_item_id(item_idx)
            if similar_song_id is None:
                continue

            result.append((similar_song_id, similarity))

        return result