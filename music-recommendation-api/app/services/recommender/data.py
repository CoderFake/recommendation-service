import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Set
from collections import defaultdict
import torch
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class RecommenderDataManager:

    def __init__(self):
        self.interactions_df = None
        self.user_mapping = {}
        self.item_mapping = {}
        self.reverse_user_mapping = {}
        self.reverse_item_mapping = {}

        # Item features
        self.item_features_df = None
        self.item_features_matrix = None
        self.feature_scaler = StandardScaler()

        # User state for incremental learning
        self.user_positive_items = defaultdict(set)  # User -> set of liked items
        self.user_negative_items = defaultdict(set)  # User -> set of disliked items

        # Metadata
        self.n_users = 0
        self.n_items = 0
        self.n_interactions = 0
        self.feature_dim = 0

        # Flags
        self.data_initialized = False

    def load_interactions(self, interactions_df: pd.DataFrame):
        logger.info(f"Loading interactions data with shape {interactions_df.shape}")

        self.interactions_df = interactions_df.copy()

        unique_users = self.interactions_df['user_id'].unique()
        unique_items = self.interactions_df['song_id'].unique()

        self.user_mapping = {user_id: idx for idx, user_id in enumerate(unique_users)}
        self.item_mapping = {item_id: idx for idx, item_id in enumerate(unique_items)}

        self.reverse_user_mapping = {idx: user_id for user_id, idx in self.user_mapping.items()}
        self.reverse_item_mapping = {idx: item_id for item_id, idx in self.item_mapping.items()}

        # Update metadata
        self.n_users = len(unique_users)
        self.n_items = len(unique_items)
        self.n_interactions = len(self.interactions_df)

        logger.info(f"Loaded {self.n_interactions} interactions from {self.n_users} users on {self.n_items} items")

        self._build_user_preference_sets()

        self.data_initialized = True

    def _build_user_preference_sets(self):
        logger.info("Building user preference sets")

        self.user_positive_items = defaultdict(set)
        self.user_negative_items = defaultdict(set)

        # Consider interactions with rating > 0.6 as positive, < 0.3 as negative
        POSITIVE_THRESHOLD = 0.6
        NEGATIVE_THRESHOLD = 0.3

        for _, row in self.interactions_df.iterrows():
            user_idx = self.user_mapping.get(row['user_id'])
            item_idx = self.item_mapping.get(row['song_id'])

            if user_idx is None or item_idx is None:
                continue

            rating = row.get('rating', row.get('like_score', 0.0))

            if rating >= POSITIVE_THRESHOLD:
                self.user_positive_items[user_idx].add(item_idx)
            elif rating <= NEGATIVE_THRESHOLD:
                self.user_negative_items[user_idx].add(item_idx)

    def load_item_features(self, features_df: pd.DataFrame):
        logger.info(f"Loading item features with shape {features_df.shape}")

        self.item_features_df = features_df.copy()

        feature_columns = [col for col in features_df.columns if col != 'song_id']
        self.feature_dim = len(feature_columns)

        self.item_features_matrix = np.zeros((self.n_items, self.feature_dim))

        features_array = features_df[feature_columns].values
        standardized_features = self.feature_scaler.fit_transform(features_array)

        for i, song_id in enumerate(features_df['song_id']):
            if song_id in self.item_mapping:
                item_idx = self.item_mapping[song_id]
                self.item_features_matrix[item_idx] = standardized_features[i]

        logger.info(f"Loaded {self.feature_dim} features for {self.n_items} items")

    def add_interaction(self, user_id: int, song_id: int, rating: float) -> Tuple[int, int]:
        if user_id not in self.user_mapping:
            user_idx = len(self.user_mapping)
            self.user_mapping[user_id] = user_idx
            self.reverse_user_mapping[user_idx] = user_id
            self.n_users += 1
        else:
            user_idx = self.user_mapping[user_id]

        if song_id not in self.item_mapping:
            item_idx = len(self.item_mapping)
            self.item_mapping[song_id] = item_idx
            self.reverse_item_mapping[item_idx] = song_id
            self.n_items += 1

            if self.item_features_matrix is not None:
                new_features = np.zeros((1, self.feature_dim))
                self.item_features_matrix = np.vstack([self.item_features_matrix, new_features])
        else:
            item_idx = self.item_mapping[song_id]

        new_interaction = pd.DataFrame({
            'user_id': [user_id],
            'song_id': [song_id],
            'rating': [rating]
        })

        if self.interactions_df is None:
            self.interactions_df = new_interaction
        else:
            self.interactions_df = pd.concat([self.interactions_df, new_interaction], ignore_index=True)

        self.n_interactions += 1

        if rating >= 0.6:
            self.user_positive_items[user_idx].add(item_idx)
        elif rating <= 0.3:
            self.user_negative_items[user_idx].add(item_idx)

        return user_idx, item_idx

    def update_interaction(self, user_id: int, song_id: int, rating: float) -> Tuple[int, int]:

        user_idx = self.user_mapping.get(user_id)
        item_idx = self.item_mapping.get(song_id)

        if user_idx is None or item_idx is None:
            return self.add_interaction(user_id, song_id, rating)

        mask = (self.interactions_df['user_id'] == user_id) & (self.interactions_df['song_id'] == song_id)
        if mask.any():
            self.interactions_df.loc[mask, 'rating'] = rating
        else:
            return self.add_interaction(user_id, song_id, rating)

        if rating >= 0.6:
            self.user_positive_items[user_idx].add(item_idx)
            if item_idx in self.user_negative_items[user_idx]:
                self.user_negative_items[user_idx].remove(item_idx)
        elif rating <= 0.3:
            self.user_negative_items[user_idx].add(item_idx)
            if item_idx in self.user_positive_items[user_idx]:
                self.user_positive_items[user_idx].remove(item_idx)
        else:
            if item_idx in self.user_positive_items[user_idx]:
                self.user_positive_items[user_idx].remove(item_idx)
            if item_idx in self.user_negative_items[user_idx]:
                self.user_negative_items[user_idx].remove(item_idx)

        return user_idx, item_idx

    def update_item_features(self, song_id: int, features: Dict[str, Any]):

        if song_id not in self.item_mapping:
            logger.warning(f"Item {song_id} not found in mapping, cannot update features.")
            return

        item_idx = self.item_mapping[song_id]

        if self.item_features_df is not None:
            mask = self.item_features_df['song_id'] == song_id
            if mask.any():
                for feature_name, value in features.items():
                    if feature_name in self.item_features_df.columns:
                        self.item_features_df.loc[mask, feature_name] = value

        if self.item_features_matrix is not None:
            feature_columns = [col for col in self.item_features_df.columns if col != 'song_id']
            feature_values = np.array([features.get(col, 0) for col in feature_columns]).reshape(1, -1)

            standardized_features = self.feature_scaler.transform(feature_values)
            self.item_features_matrix[item_idx] = standardized_features.flatten()

    def get_training_data(self) -> List[Tuple[int, int, float]]:

        if not self.data_initialized:
            logger.warning("Data not initialized, returning empty training data")
            return []

        training_data = []

        for _, row in self.interactions_df.iterrows():
            user_id = row['user_id']
            song_id = row['song_id']

            if user_id in self.user_mapping and song_id in self.item_mapping:
                user_idx = self.user_mapping[user_id]
                item_idx = self.item_mapping[song_id]
                rating = row.get('rating', row.get('like_score', 0.0))

                training_data.append((user_idx, item_idx, rating))

        return training_data

    def get_user_history(self, user_id: int) -> List[Tuple[int, float]]:
        if user_id not in self.user_mapping:
            return []

        user_idx = self.user_mapping[user_id]
        mask = self.interactions_df['user_id'] == user_id

        history = []
        for _, row in self.interactions_df[mask].iterrows():
            song_id = row['song_id']

            if song_id in self.item_mapping:
                item_idx = self.item_mapping[song_id]
                rating = row.get('rating', row.get('like_score', 0.0))

                history.append((item_idx, rating))

        return history

    def get_item_features(self, song_id: int) -> Optional[np.ndarray]:
        if song_id not in self.item_mapping or self.item_features_matrix is None:
            return None

        item_idx = self.item_mapping[song_id]
        return self.item_features_matrix[item_idx]

    def generate_candidate_items(
            self,
            user_id: int,
            exclude_items: Optional[Set[int]] = None,
            include_history: bool = False
    ) -> List[int]:

        if user_id not in self.user_mapping:
            return list(self.item_mapping.values())

        user_idx = self.user_mapping[user_id]
        exclude_items = exclude_items or set()
        exclude_indices = {self.item_mapping[item_id] for item_id in exclude_items if item_id in self.item_mapping}

        if not include_history:
            user_history = set()
            mask = self.interactions_df['user_id'] == user_id

            for song_id in self.interactions_df[mask]['song_id']:
                if song_id in self.item_mapping:
                    user_history.add(self.item_mapping[song_id])

            exclude_indices.update(user_history)

        candidates = [
            item_idx for item_idx in range(self.n_items)
            if item_idx not in exclude_indices
        ]

        return candidates

    def get_user_idx(self, user_id: int) -> Optional[int]:
        return self.user_mapping.get(user_id)

    def get_item_idx(self, song_id: int) -> Optional[int]:
        return self.item_mapping.get(song_id)

    def get_user_id(self, user_idx: int) -> Optional[int]:
        return self.reverse_user_mapping.get(user_idx)

    def get_item_id(self, item_idx: int) -> Optional[int]:
        return self.reverse_item_mapping.get(item_idx)