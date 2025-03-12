from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

from app.schemas.song import Song


class RecommendationRequest(BaseModel):
    limit: Optional[int] = Field(10, ge=1, le=50, description="Number of recommendations to return")
    seed_songs: Optional[List[int]] = Field(None, description="List of song IDs to use as seeds")
    seed_genres: Optional[List[str]] = Field(None, description="List of genres to use as seeds")
    collaborative_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="Weight for collaborative filtering")
    content_based_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="Weight for content-based filtering")
    diversity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Diversity factor for recommendations")
    include_liked: Optional[bool] = Field(False, description="Include songs the user has liked")
    include_listened: Optional[bool] = Field(True, description="Include songs the user has listened to")


class SongRecommendation(BaseModel):
    song: Song
    score: float = Field(..., description="Recommendation score between 0 and 1")
    relevance_factors: Dict[str, float] = Field(
        ...,
        description="Factors contributing to the recommendation (e.g. collaborative: 0.7, content: 0.3)"
    )


class RecommendationResponse(BaseModel):
    recommendations: List[SongRecommendation]
    seed_info: Dict[str, Any] = Field(
        ...,
        description="Information about the seeds used for recommendations"
    )
    explanation: Optional[str] = None


class UserTaste(BaseModel):
    top_genres: List[Dict[str, Any]]
    top_artists: List[Dict[str, Any]]
    listening_patterns: Dict[str, Any]
    genre_distribution: Dict[str, float]
    feature_preferences: Dict[str, float]