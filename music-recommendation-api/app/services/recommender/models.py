import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Optional, Union, Any

logger = logging.getLogger(__name__)


class NCFDataset(Dataset):
    def __init__(self, user_item_interactions: List[Tuple[int, int, float]]):

        self.users = [interaction[0] for interaction in user_item_interactions]
        self.items = [interaction[1] for interaction in user_item_interactions]
        self.ratings = [interaction[2] for interaction in user_item_interactions]

    def __len__(self):
        return len(self.users)

    def __getitem__(self, idx):
        return {
            'user': torch.tensor(self.users[idx], dtype=torch.long),
            'item': torch.tensor(self.items[idx], dtype=torch.long),
            'rating': torch.tensor(self.ratings[idx], dtype=torch.float)
        }


class NCF(nn.Module):

    def __init__(
            self,
            n_users: int,
            n_items: int,
            embedding_dim: int = 32,
            layers: List[int] = [64, 32, 16, 8],
            dropout: float = 0.2
    ):
        super(NCF, self).__init__()

        self.n_users = n_users
        self.n_items = n_items
        self.embedding_dim = embedding_dim
        self.layers = layers

        # GMF embedding layers
        self.user_gmf_embedding = nn.Embedding(n_users, embedding_dim)
        self.item_gmf_embedding = nn.Embedding(n_items, embedding_dim)

        # MLP embedding layers
        self.user_mlp_embedding = nn.Embedding(n_users, embedding_dim)
        self.item_mlp_embedding = nn.Embedding(n_items, embedding_dim)

        # MLP layers
        self.mlp_layers = nn.ModuleList()
        input_size = 2 * embedding_dim

        for i, layer_size in enumerate(layers):
            self.mlp_layers.append(nn.Linear(input_size, layer_size))
            input_size = layer_size

            # Add dropout after each layer except the last one
            if i < len(layers) - 1:
                self.mlp_layers.append(nn.Dropout(dropout))

        # Output layer
        self.output_layer = nn.Linear(embedding_dim + layers[-1], 1)

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.01)

    def forward(self, user_indices: torch.Tensor, item_indices: torch.Tensor) -> torch.Tensor:
        # GMF part
        user_gmf_emb = self.user_gmf_embedding(user_indices)
        item_gmf_emb = self.item_gmf_embedding(item_indices)
        gmf_output = user_gmf_emb * item_gmf_emb  # Element-wise product

        # MLP part
        user_mlp_emb = self.user_mlp_embedding(user_indices)
        item_mlp_emb = self.item_mlp_embedding(item_indices)
        mlp_input = torch.cat([user_mlp_emb, item_mlp_emb], dim=1)  # Concatenation

        # Process MLP layers
        for i, layer in enumerate(self.mlp_layers):
            mlp_input = layer(mlp_input)
            if not isinstance(layer, nn.Dropout):
                mlp_input = F.relu(mlp_input)

        # Concatenate GMF and MLP outputs
        concat_output = torch.cat([gmf_output, mlp_input], dim=1)

        # Final prediction layer
        prediction = self.output_layer(concat_output)

        # Apply sigmoid to constrain the output between 0 and 1
        return torch.sigmoid(prediction).squeeze()

    def get_user_embedding(self, user_idx: int) -> torch.Tensor:

        user_tensor = torch.tensor([user_idx], dtype=torch.long)
        gmf_emb = self.user_gmf_embedding(user_tensor)
        mlp_emb = self.user_mlp_embedding(user_tensor)
        return torch.cat([gmf_emb, mlp_emb], dim=1).detach()

    def get_item_embedding(self, item_idx: int) -> torch.Tensor:

        item_tensor = torch.tensor([item_idx], dtype=torch.long)
        gmf_emb = self.item_gmf_embedding(item_tensor)
        mlp_emb = self.item_mlp_embedding(item_tensor)
        return torch.cat([gmf_emb, mlp_emb], dim=1).detach()

    def predict_batch(self, user_indices: torch.Tensor, item_indices: torch.Tensor) -> torch.Tensor:

        return self.forward(user_indices, item_indices)

    def predict(self, user_idx: int, item_idx: int) -> float:

        user_tensor = torch.tensor([user_idx], dtype=torch.long)
        item_tensor = torch.tensor([item_idx], dtype=torch.long)

        self.eval()
        with torch.no_grad():
            prediction = self.forward(user_tensor, item_tensor)

        return prediction.item()


class ContentBasedModel:

    def __init__(self, n_items: int, feature_dim: int):
        self.n_items = n_items
        self.feature_dim = feature_dim
        self.item_features = np.zeros((n_items, feature_dim))
        self.item_similarity_matrix = None

    def set_item_features(self, item_features: np.ndarray):

        if item_features.shape != (self.n_items, self.feature_dim):
            raise ValueError(f"Expected shape {(self.n_items, self.feature_dim)}, got {item_features.shape}")

        self.item_features = item_features
        self._compute_similarity_matrix()

    def update_item_feature(self, item_idx: int, features: np.ndarray):

        if features.shape != (self.feature_dim,):
            raise ValueError(f"Expected shape ({self.feature_dim},), got {features.shape}")

        self.item_features[item_idx] = features
        self._compute_similarity_matrix()

    def _compute_similarity_matrix(self):
        normalized_features = self.item_features / (np.linalg.norm(self.item_features, axis=1, keepdims=True) + 1e-8)

        self.item_similarity_matrix = cosine_similarity(normalized_features)

        np.fill_diagonal(self.item_similarity_matrix, 0)

    def get_similar_items(self, item_idx: int, n: int = 10) -> List[Tuple[int, float]]:

        if self.item_similarity_matrix is None:
            raise ValueError("Similarity matrix not computed. Call set_item_features first.")

        similarities = self.item_similarity_matrix[item_idx]
        top_indices = np.argsort(similarities)[::-1][:n]

        return [(idx, similarities[idx]) for idx in top_indices]

    def predict_item_scores(self, user_history: List[Tuple[int, float]]) -> np.ndarray:
        if self.item_similarity_matrix is None:
            raise ValueError("Similarity matrix not computed. Call set_item_features first.")

        scores = np.zeros(self.n_items)

        # Calculate weighted sum of similarities
        total_weight = 0
        for item_idx, rating in user_history:
            scores += rating * self.item_similarity_matrix[item_idx]
            total_weight += abs(rating)

        # Normalize scores
        if total_weight > 0:
            scores /= total_weight

        return scores


class HybridRecommender:
    def __init__(
            self,
            ncf_model: NCF,
            content_model: ContentBasedModel,
            collaborative_weight: float = 0.7,
            content_weight: float = 0.3
    ):

        self.ncf_model = ncf_model
        self.content_model = content_model
        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight

        # Normalize weights
        total_weight = self.collaborative_weight + self.content_weight
        self.collaborative_weight /= total_weight
        self.content_weight /= total_weight

    def set_weights(self, collaborative_weight: float, content_weight: float):
        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight

        # Normalize weights
        total_weight = self.collaborative_weight + self.content_weight
        self.collaborative_weight /= total_weight
        self.content_weight /= total_weight

    def predict(self, user_idx: int, item_idx: int, user_history: List[Tuple[int, float]]) -> float:
        # Get collaborative filtering prediction
        cf_prediction = self.ncf_model.predict(user_idx, item_idx)

        # Get content-based prediction
        content_scores = self.content_model.predict_item_scores(user_history)
        cb_prediction = content_scores[item_idx]

        # Combine predictions
        hybrid_prediction = (
                self.collaborative_weight * cf_prediction +
                self.content_weight * cb_prediction
        )

        return hybrid_prediction

    def recommend_items(
            self,
            user_idx: int,
            user_history: List[Tuple[int, float]],
            n: int = 10,
            exclude_items: Optional[List[int]] = None
    ) -> List[Tuple[int, float]]:

        exclude_items = set(exclude_items or [])
        history_items = {item[0] for item in user_history}
        exclude_items.update(history_items)

        # Predict scores for all items
        all_items = np.arange(self.ncf_model.n_items)
        all_predictions = []

        for item_idx in all_items:
            if item_idx in exclude_items:
                continue

            prediction = self.predict(user_idx, item_idx, user_history)
            all_predictions.append((item_idx, prediction))

        # Sort by prediction score in descending order
        all_predictions.sort(key=lambda x: x[1], reverse=True)

        return all_predictions[:n]