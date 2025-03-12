import logging
import asyncio
import traceback
from datetime import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Set, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core.config import settings
from app.services.recommender.data import RecommenderDataManager
from app.services.recommender.trainer import ModelTrainer

logger = logging.getLogger(__name__)


class RecommenderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.data_manager = RecommenderDataManager()
        self.model_trainer = ModelTrainer(
            data_manager=self.data_manager,
            model_dir="./models",
            collaborative_weight=settings.COLLABORATIVE_WEIGHT,
            content_weight=settings.CONTENT_BASED_WEIGHT
        )
        self.model_initialized = False
        self.last_training_time = None
        self.training_in_progress = False

    async def initialize(self, force_reload: bool = False):

        if self.model_initialized and not force_reload:
            return

        logger.info("Initializing recommender service")

        try:
            model_loaded = False
            try:
                if self.model_trainer.load_ncf_model("ncf_best.pt"):
                    model_loaded = True
                    logger.info("Loaded existing recommendation model")
            except Exception as e:
                logger.warning(f"Error loading model: {str(e)}")

            if not model_loaded:
                await self._load_data()

                if self.data_manager.n_interactions < settings.MIN_INTERACTIONS_FOR_TRAINING:
                    logger.warning(
                        f"Not enough interactions for model training. "
                        f"Need {settings.MIN_INTERACTIONS_FOR_TRAINING}, but got {self.data_manager.n_interactions}."
                    )
                    self.model_trainer._init_models(force_reinit=True)
                    self.model_initialized = True
                    return

                asyncio.create_task(self._train_model())

            logger.info("Recommender service initialized")
            self.model_initialized = True

        except Exception as e:
            logger.error(f"Error initializing recommender service: {str(e)}")
            logger.error(traceback.format_exc())
            try:
                self.model_trainer._init_models(force_reinit=True)
                self.model_initialized = True
                logger.info("Initialized recommender with default parameters due to error")
            except Exception as nested_e:
                logger.critical(f"Critical error initializing models: {str(nested_e)}")
                raise

    async def _load_data(self):
        logger.info("Loading recommender data from database")

        stmt = select(
            models.Interaction.user_id,
            models.Interaction.song_id,
            models.Interaction.like_score.label('rating'),
            models.Interaction.timestamp
        )

        result = await self.db.execute(stmt)
        interactions = result.all()

        interactions_df = pd.DataFrame(
            [(row.user_id, row.song_id, row.rating) for row in interactions],
            columns=['user_id', 'song_id', 'rating']
        )

        if not interactions_df.empty:
            self.data_manager.load_interactions(interactions_df)
            logger.info(f"Loaded {len(interactions_df)} interactions")
        else:
            logger.warning("No interactions found in database")

        stmt = select(
            models.Song.id.label('song_id'),
            models.Song.features
        ).where(models.Song.features.is_not(None))

        result = await self.db.execute(stmt)
        songs = result.all()

        features_data = []
        for song in songs:
            if song.features:
                song_features = {
                    'song_id': song.song_id
                }

                for key, value in song.features.items():
                    if isinstance(value, (int, float)) and key not in ['song_id']:
                        song_features[key] = value

                features_data.append(song_features)

        if features_data:
            features_df = pd.DataFrame(features_data)

            for col in features_df.columns:
                if col != 'song_id' and features_df[col].dtype in [np.float64, np.int64]:
                    features_df[col] = features_df[col].fillna(features_df[col].mean())

            self.data_manager.load_item_features(features_df)
            logger.info(f"Loaded features for {len(features_df)} songs")
        else:
            logger.warning("No song features found in database")

    async def _train_model(self):
        if self.training_in_progress:
            logger.info("Training already in progress, skipping")
            return

        self.training_in_progress = True

        try:
            logger.info("Starting model training")

            training_history = self.model_trainer.train_ncf_model(validation_split=0.2)

            if "error" in training_history:
                logger.error(f"Error training model: {training_history['error']}")
                return

            logger.info(
                f"Model training completed with best validation loss: {training_history.get('best_val_loss', 'N/A')}")

            self.last_training_time = datetime.utcnow()
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            self.training_in_progress = False

    async def retrain_model(self):
        try:
            await self._load_data()

            asyncio.create_task(self._train_model())

            return {"status": "retraining_started"}
        except Exception as e:
            logger.error(f"Error retraining model: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def update_incrementally(self, user_id: int, song_id: int, rating: float):
        if not self.model_initialized:
            await self.initialize()

        try:
            self.model_trainer.update_model_incrementally(user_id, song_id, rating)
            return True
        except Exception as e:
            logger.error(f"Error updating model incrementally: {str(e)}")
            return False

    async def process_event(self, user_id: int, song_id: int, event_type: str,
                            context: Optional[Dict[str, Any]] = None):
        if not self.model_initialized:
            await self.initialize()

        try:
            self.model_trainer.process_event(user_id, song_id, event_type, context)
            return True
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
            return False

    async def get_recommendations(
            self,
            user_id: int,
            request: schemas.RecommendationRequest
    ) -> schemas.RecommendationResponse:
        if not self.model_initialized:
            await self.initialize()

        try:
            stmt = select(func.count()).select_from(models.Interaction).where(models.Interaction.user_id == user_id)
            result = await self.db.execute(stmt)
            interaction_count = result.scalar() or 0

            if interaction_count < settings.MIN_INTERACTIONS_FOR_RECOMMENDATIONS:
                return await self.get_cold_start_recommendations(user_id,
                                                                 request.limit or settings.DEFAULT_NUM_RECOMMENDATIONS)

            limit = request.limit or settings.DEFAULT_NUM_RECOMMENDATIONS
            exclude_items = set(request.seed_songs or [])
            collaborative_weight = request.collaborative_weight or settings.COLLABORATIVE_WEIGHT
            content_weight = request.content_based_weight or settings.CONTENT_BASED_WEIGHT

            recommendations = self.model_trainer.get_recommendations(
                user_id=user_id,
                n=limit,
                exclude_items=list(exclude_items),
                include_liked=request.include_liked,
                collaborative_weight=collaborative_weight,
                content_weight=content_weight
            )

            song_recs = []

            for song_id, score, relevance_factors in recommendations:
                stmt = select(models.Song).where(models.Song.id == song_id)
                result = await self.db.execute(stmt)
                song = result.scalars().first()

                if song:
                    song_recs.append(
                        schemas.SongRecommendation(
                            song=song,
                            score=score,
                            relevance_factors=relevance_factors
                        )
                    )

            seed_info = {
                "seed_songs": request.seed_songs or [],
                "seed_genres": request.seed_genres or [],
                "collaborative_weight": collaborative_weight,
                "content_based_weight": content_weight,
                "diversity": request.diversity,
                "include_liked": request.include_liked,
                "include_listened": request.include_listened
            }

            explanation = self._generate_explanation(song_recs, seed_info)

            return schemas.RecommendationResponse(
                recommendations=song_recs,
                seed_info=seed_info,
                explanation=explanation
            )

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def get_cold_start_recommendations(self, user_id: int, limit: int = 10) -> schemas.RecommendationResponse:

        logger.info(f"Generating cold-start recommendations for user {user_id}")

        try:
            # Get top songs by popularity
            stmt = (
                select(models.Song)
                .order_by(models.Song.features['popularity'].desc())
                .limit(limit * 2)  # Fetch more for diversity
            )

            result = await self.db.execute(stmt)
            popular_songs = result.scalars().all()

            # Get recent interactions (if any) to find genres
            user_stmt = (
                select(models.Interaction)
                .where(models.Interaction.user_id == user_id)
                .order_by(models.Interaction.timestamp.desc())
                .limit(5)
            )

            user_result = await self.db.execute(user_stmt)
            user_interactions = user_result.scalars().all()

            # If we have some interactions, try to use them for genre preferences
            genre_weighted_songs = []
            if user_interactions:
                song_ids = [interaction.song_id for interaction in user_interactions]

                # Get genres from these songs
                songs_stmt = (
                    select(models.Song)
                    .where(models.Song.id.in_(song_ids))
                )

                songs_result = await self.db.execute(songs_stmt)
                interacted_songs = songs_result.scalars().all()

                genres = []
                for song in interacted_songs:
                    if song.genre and song.genre not in genres:
                        genres.append(song.genre)

                if genres:
                    # Get songs from these genres but not in the already interacted songs
                    genre_stmt = (
                        select(models.Song)
                        .where(
                            models.Song.genre.in_(genres),
                            ~models.Song.id.in_(song_ids)
                        )
                        .order_by(models.Song.features['popularity'].desc())
                        .limit(limit * 2)
                    )

                    genre_result = await self.db.execute(genre_stmt)
                    genre_songs = genre_result.scalars().all()

                    # Assign weights based on popularity
                    for song in genre_songs:
                        popularity = song.features.get('popularity', 50) if song.features else 50
                        genre_weighted_songs.append((song, popularity / 100))

            # Combine recommendations from both approaches
            final_recommendations = []

            # Add genre-based first if available
            for song, weight in genre_weighted_songs:
                if len(final_recommendations) >= limit:
                    break

                final_recommendations.append(
                    schemas.SongRecommendation(
                        song=song,
                        score=weight,
                        relevance_factors={
                            "genre_match": weight,
                            "popularity": song.features.get('popularity', 50) / 100 if song.features else 0.5
                        }
                    )
                )

            # Add popularity-based recommendations to fill remaining slots
            for song in popular_songs:
                if len(final_recommendations) >= limit:
                    break

                # Skip if already added
                if any(rec.song.id == song.id for rec in final_recommendations):
                    continue

                popularity = song.features.get('popularity', 50) / 100 if song.features else 0.5

                final_recommendations.append(
                    schemas.SongRecommendation(
                        song=song,
                        score=popularity,
                        relevance_factors={
                            "popularity": popularity
                        }
                    )
                )

            # Create explanation
            if genre_weighted_songs:
                explanation = f"Since you're new, we're recommending popular songs and songs from genres like {', '.join(genres[:3])} based on your recent activity."
            else:
                explanation = "Since you're new, we're recommending some popular songs to help you get started."

            # Create seed info
            seed_info = {
                "seed_songs": [],
                "seed_genres": genres[:3] if genre_weighted_songs else [],
                "collaborative_weight": 0.0,
                "content_based_weight": 1.0,
                "diversity": 0.5,
                "include_liked": False,
                "include_listened": False,
                "is_cold_start": True
            }

            return schemas.RecommendationResponse(
                recommendations=final_recommendations,
                seed_info=seed_info,
                explanation=explanation
            )

        except Exception as e:
            logger.error(f"Error generating cold-start recommendations: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def get_similar_songs(self, song_id: int, limit: int = 10) -> List[schemas.SongRecommendation]:
        if not self.model_initialized:
            await self.initialize()

        try:
            similar_songs = self.model_trainer.get_similar_songs(song_id, n=limit)

            song_recs = []

            for similar_song_id, similarity in similar_songs:
                stmt = select(models.Song).where(models.Song.id == similar_song_id)
                result = await self.db.execute(stmt)
                song = result.scalars().first()

                if song:
                    song_recs.append(
                        schemas.SongRecommendation(
                            song=song,
                            score=similarity,
                            relevance_factors={"content_similarity": similarity}
                        )
                    )

            return song_recs

        except Exception as e:
            logger.error(f"Error getting similar songs: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def get_user_taste_profile(self, user_id: int) -> schemas.UserTaste:
        try:
            stmt = select(
                models.Song.genre,
                func.count(models.Song.id).label('count'),
                func.avg(models.Interaction.like_score).label('avg_score')
            ).join(
                models.Interaction,
                models.Song.id == models.Interaction.song_id
            ).where(
                models.Interaction.user_id == user_id,
                models.Song.genre.is_not(None)
            ).group_by(
                models.Song.genre
            ).order_by(
                func.avg(models.Interaction.like_score).desc(),
                func.count(models.Song.id).desc()
            ).limit(10)

            result = await self.db.execute(stmt)
            genres = result.all()

            top_genres = [
                {
                    "genre": genre.genre,
                    "count": genre.count,
                    "score": float(genre.avg_score)
                }
                for genre in genres
            ]

            stmt = select(
                models.Song.artist,
                func.count(models.Song.id).label('count'),
                func.avg(models.Interaction.like_score).label('avg_score')
            ).join(
                models.Interaction,
                models.Song.id == models.Interaction.song_id
            ).where(
                models.Interaction.user_id == user_id
            ).group_by(
                models.Song.artist
            ).order_by(
                func.avg(models.Interaction.like_score).desc(),
                func.count(models.Song.id).desc()
            ).limit(10)

            result = await self.db.execute(stmt)
            artists = result.all()

            top_artists = [
                {
                    "artist": artist.artist,
                    "count": artist.count,
                    "score": float(artist.avg_score)
                }
                for artist in artists
            ]

            stmt = select(
                models.Interaction.context
            ).where(
                models.Interaction.user_id == user_id,
                models.Interaction.context.is_not(None)
            ).order_by(
                models.Interaction.timestamp.desc()
            ).limit(100)

            result = await self.db.execute(stmt)
            contexts = result.scalars().all()

            time_of_day = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
            devices = {}

            for context in contexts:
                if not context:
                    continue

                if "time_of_day" in context:
                    tod = context["time_of_day"]
                    if tod in time_of_day:
                        time_of_day[tod] += 1

                if "device" in context:
                    device = context["device"]
                    devices[device] = devices.get(device, 0) + 1

            total_genre_count = sum(genre["count"] for genre in top_genres)
            genre_distribution = {}

            if total_genre_count > 0:
                for genre in top_genres:
                    genre_distribution[genre["genre"]] = genre["count"] / total_genre_count

            return schemas.UserTaste(
                top_genres=top_genres,
                top_artists=top_artists,
                listening_patterns={
                    "time_of_day": time_of_day,
                    "devices": devices
                },
                genre_distribution=genre_distribution,
                feature_preferences={}  # TODO: Implement feature preference analysis
            )

        except Exception as e:
            logger.error(f"Error getting user taste profile: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _generate_explanation(
            self,
            recommendations: List[schemas.SongRecommendation],
            seed_info: Dict[str, Any]
    ) -> str:
        if not recommendations:
            return "No recommendations could be generated."

        cf_avg = sum(rec.relevance_factors.get("collaborative", 0) for rec in recommendations) / len(recommendations)
        cb_avg = sum(rec.relevance_factors.get("content_based", 0) for rec in recommendations) / len(recommendations)

        seed_songs = seed_info.get("seed_songs", [])
        seed_genres = seed_info.get("seed_genres", [])

        explanation_parts = []

        if seed_songs:
            explanation_parts.append(f"Based on {len(seed_songs)} seed songs you provided")

        if seed_genres:
            if explanation_parts:
                explanation_parts.append(f" and your interest in {', '.join(seed_genres)}")
            else:
                explanation_parts.append(f"Based on your interest in {', '.join(seed_genres)}")

        if not seed_songs and not seed_genres:
            explanation_parts.append("Based on your listening history")

        if cf_avg > cb_avg * 1.5:
            explanation_parts.append(", we found songs that users with similar taste have enjoyed")
        elif cb_avg > cf_avg * 1.5:
            explanation_parts.append(", we found songs with similar musical features")
        else:
            explanation_parts.append(
                ", we balanced finding songs that similar users enjoy and songs with similar musical features")

        explanation_parts.append(".")

        return "".join(explanation_parts)
