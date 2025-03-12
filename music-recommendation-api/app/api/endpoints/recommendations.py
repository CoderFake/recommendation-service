from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.core.config import settings
from app.db.session import get_db
from app.services.recommender import RecommenderService

router = APIRouter()


@router.get("/", response_model=schemas.RecommendationResponse)
async def get_recommendations(
        limit: int = Query(settings.DEFAULT_NUM_RECOMMENDATIONS, ge=1, le=50),
        seed_songs: Optional[List[int]] = Query(None),
        seed_genres: Optional[List[str]] = Query(None),
        collaborative_weight: Optional[float] = Query(None, ge=0.0, le=1.0),
        content_based_weight: Optional[float] = Query(None, ge=0.0, le=1.0),
        diversity: Optional[float] = Query(None, ge=0.0, le=1.0),
        include_liked: bool = False,
        include_listened: bool = True,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        recommender: RecommenderService = Depends(deps.get_recommender_service)
) -> Any:

    request = schemas.RecommendationRequest(
        limit=limit,
        seed_songs=seed_songs,
        seed_genres=seed_genres,
        collaborative_weight=collaborative_weight,
        content_based_weight=content_based_weight,
        diversity=diversity,
        include_liked=include_liked,
        include_listened=include_listened
    )

    try:
        recommendations = await recommender.get_recommendations(
            user_id=current_user.id,
            request=request
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/similar/{song_id}", response_model=List[schemas.SongRecommendation])
async def get_similar_songs(
        song_id: int,
        limit: int = Query(10, ge=1, le=50),
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        recommender: RecommenderService = Depends(deps.get_recommender_service)
) -> Any:

    song_query = select(models.Song).filter(models.Song.id == song_id)
    result = await db.execute(song_query)
    song = result.scalars().first()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    try:
        similar_songs = await recommender.get_similar_songs(
            song_id=song_id,
            limit=limit
        )
        return similar_songs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding similar songs: {str(e)}"
        )


@router.get("/taste-profile", response_model=schemas.UserTaste)
async def get_user_taste_profile(
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        recommender: RecommenderService = Depends(deps.get_recommender_service)
) -> Any:

    try:
        taste_profile = await recommender.get_user_taste_profile(user_id=current_user.id)
        return taste_profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating taste profile: {str(e)}"
        )


@router.post("/refresh-model", status_code=status.HTTP_202_ACCEPTED)
async def refresh_recommendation_model(
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        recommender: RecommenderService = Depends(deps.get_recommender_service)
) -> Any:

    try:
        await recommender.retrain_model()
        return {"status": "Model refresh scheduled"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing model: {str(e)}"
        )