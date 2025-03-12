from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services.recommender import RecommenderService

router = APIRouter()


@router.get("/", response_model=List[schemas.Interaction])
async def get_user_interactions(
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        skip: int = 0,
        limit: int = 100
) -> Any:
    query = (
        select(models.Interaction)
        .filter(models.Interaction.user_id == current_user.id)
        .order_by(models.Interaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    interactions = result.scalars().all()

    return interactions


@router.post("/", response_model=schemas.Interaction)
async def create_interaction(
        interaction_data: schemas.InteractionCreate,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        recommender: RecommenderService = Depends(deps.get_recommender_service)
) -> Any:
    song_query = select(models.Song).filter(models.Song.id == interaction_data.song_id)
    result = await db.execute(song_query)
    song = result.scalars().first()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    interaction_query = select(models.Interaction).filter(
        models.Interaction.user_id == current_user.id,
        models.Interaction.song_id == interaction_data.song_id
    )
    result = await db.execute(interaction_query)
    existing_interaction = result.scalars().first()

    if existing_interaction:
        existing_interaction.listen_count += interaction_data.listen_count or 0

        if interaction_data.like_score is not None:
            existing_interaction.like_score = interaction_data.like_score

        if interaction_data.saved is not None:
            existing_interaction.saved = interaction_data.saved

        if interaction_data.context is not None:
            if existing_interaction.context:
                existing_interaction.context.update(interaction_data.context)
            else:
                existing_interaction.context = interaction_data.context

        existing_interaction.timestamp = datetime.utcnow()

        await db.commit()
        await db.refresh(existing_interaction)

        background_tasks.add_task(
            recommender.update_incrementally,
            user_id=current_user.id,
            song_id=interaction_data.song_id,
            rating=interaction_data.like_score or float(existing_interaction.listen_count > 0)
        )

        return existing_interaction
    else:
        db_interaction = models.Interaction(
            user_id=current_user.id,
            song_id=interaction_data.song_id,
            listen_count=interaction_data.listen_count or 0,
            like_score=interaction_data.like_score or 0.0,
            saved=interaction_data.saved or False,
            context=interaction_data.context
        )

        db.add(db_interaction)
        await db.commit()
        await db.refresh(db_interaction)

        # Schedule background task to update the recommendation model
        background_tasks.add_task(
            recommender.update_incrementally,
            user_id=current_user.id,
            song_id=interaction_data.song_id,
            rating=interaction_data.like_score or float(db_interaction.listen_count > 0)
        )

        return db_interaction


@router.put("/{song_id}", response_model=schemas.Interaction)
async def update_interaction(
        song_id: int,
        interaction_data: schemas.InteractionUpdate,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        recommender: RecommenderService = Depends(deps.get_recommender_service)
) -> Any:
    interaction_query = select(models.Interaction).filter(
        models.Interaction.user_id == current_user.id,
        models.Interaction.song_id == song_id
    )
    result = await db.execute(interaction_query)
    interaction = result.scalars().first()

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )


    update_data = interaction_data.dict(exclude_unset=True)

    if "context" in update_data and interaction.context:
        interaction.context.update(update_data["context"])
        del update_data["context"]

    for key, value in update_data.items():
        setattr(interaction, key, value)

    interaction.timestamp = datetime.utcnow()

    await db.commit()
    await db.refresh(interaction)

    if interaction_data.like_score is not None:
        background_tasks.add_task(
            recommender.update_incrementally,
            user_id=current_user.id,
            song_id=song_id,
            rating=interaction_data.like_score
        )

    return interaction


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction(
        song_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> None:

    interaction_query = select(models.Interaction).filter(
        models.Interaction.user_id == current_user.id,
        models.Interaction.song_id == song_id
    )
    result = await db.execute(interaction_query)
    interaction = result.scalars().first()

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )

    await db.delete(interaction)
    await db.commit()


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def track_interaction_event(
        event: schemas.InteractionEvent,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        recommender: RecommenderService = Depends(deps.get_recommender_service)
) -> Any:

    song_query = select(models.Song).filter(models.Song.id == event.song_id)
    result = await db.execute(song_query)
    song = result.scalars().first()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    event_type = event.event_type.lower()

    interaction_query = select(models.Interaction).filter(
        models.Interaction.user_id == current_user.id,
        models.Interaction.song_id == event.song_id
    )
    result = await db.execute(interaction_query)
    interaction = result.scalars().first()

    if not interaction:
        interaction = models.Interaction(
            user_id=current_user.id,
            song_id=event.song_id,
            listen_count=0,
            like_score=0.0,
            saved=False,
            context={}
        )
        db.add(interaction)

    if event_type == "play":
        interaction.listen_count += 1
        if interaction.like_score < 0.6:
            interaction.like_score = min(0.6, interaction.like_score + 0.05)

    elif event_type == "like":
        interaction.like_score = 1.0

    elif event_type == "unlike":
        interaction.like_score = 0.0

    elif event_type == "skip":
        interaction.like_score = max(0.0, interaction.like_score - 0.1)

    elif event_type == "save":
        interaction.saved = True
        interaction.like_score = max(0.8, interaction.like_score)

    elif event_type == "unsave":
        interaction.saved = False

    if event.context:
        if not interaction.context:
            interaction.context = {}

        if "event_history" not in interaction.context:
            interaction.context["event_history"] = []


        interaction.context["event_history"].append({
            "type": event_type,
            "timestamp": (event.timestamp or datetime.utcnow()).isoformat(),
            "duration": event.duration,
            "position": event.position
        })

        if len(interaction.context["event_history"]) > 20:
            interaction.context["event_history"] = interaction.context["event_history"][-20:]

    interaction.timestamp = datetime.utcnow()

    await db.commit()

    background_tasks.add_task(
        recommender.process_event,
        user_id=current_user.id,
        song_id=event.song_id,
        event_type=event_type,
        context=event.context
    )

    return {"status": "accepted"}