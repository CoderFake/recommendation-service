from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services.spotify import SpotifyClient

router = APIRouter()


@router.get("/", response_model=schemas.SongSearchResult)
async def search_songs(
        q: Optional[str] = None,
        genre: Optional[str] = None,
        artist: Optional[str] = None,
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    offset = (page - 1) * size

    query = select(models.Song)
    count_query = select(func.count()).select_from(models.Song)

    if q:
        search_filter = (
                models.Song.title.ilike(f"%{q}%") |
                models.Song.artist.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)
        count_query = count_query.filter(search_filter)

    if genre:
        query = query.filter(models.Song.genre.ilike(f"%{genre}%"))
        count_query = count_query.filter(models.Song.genre.ilike(f"%{genre}%"))

    if artist:
        query = query.filter(models.Song.artist.ilike(f"%{artist}%"))
        count_query = count_query.filter(models.Song.artist.ilike(f"%{artist}%"))

    result = await db.execute(count_query)
    total_count = result.scalar()

    query = query.offset(offset).limit(size).order_by(models.Song.title)

    result = await db.execute(query)
    songs = result.scalars().all()

    return {
        "songs": songs,
        "total": total_count,
        "page": page,
        "size": size
    }


@router.get("/{song_id}", response_model=schemas.Song)
async def get_song(
        song_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    query = select(models.Song).filter(models.Song.id == song_id)
    result = await db.execute(query)
    song = result.scalars().first()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    return song


@router.post("/spotify/search", response_model=List[schemas.SpotifyTrack])
async def search_spotify(
        q: str,
        limit: int = Query(10, ge=1, le=50),
        spotify_client: SpotifyClient = Depends(deps.get_spotify_client),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    try:
        tracks = await spotify_client.search_tracks(q, limit=limit)
        return tracks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Spotify API error: {str(e)}"
        )


@router.post("/spotify/import", response_model=schemas.Song)
async def import_spotify_track(
        track_id: str,
        db: AsyncSession = Depends(get_db),
        spotify_client: SpotifyClient = Depends(deps.get_spotify_client),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    query = select(models.Song).filter(models.Song.spotify_id == track_id)
    result = await db.execute(query)
    existing_song = result.scalars().first()

    if existing_song:
        return existing_song

    try:
        track_data = await spotify_client.get_track(track_id)
        audio_features = await spotify_client.get_track_audio_features(track_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Spotify API error: {str(e)}"
        )

    track = schemas.SpotifyTrack(**track_data)

    # Get genre from the first artist if available
    genre = None
    if track.artists and len(track.artists) > 0:
        try:
            artist_id = track.artists[0].id
            artist_data = await spotify_client._make_request("get", f"/artists/{artist_id}")
            if "genres" in artist_data and artist_data["genres"]:
                genre = artist_data["genres"][0]
        except Exception:
            # If we can't get genre, just continue without it
            pass

    db_song = models.Song(
        spotify_id=track.id,
        title=track.title,
        artist=track.artist,
        artwork_url=track.artwork_url,
        duration=track.duration_ms,
        genre=genre,
        features={
            "popularity": track.popularity,
            "preview_url": track.preview_url,
            "explicit": track.explicit,
            **audio_features
        }
    )

    db.add(db_song)
    await db.commit()
    await db.refresh(db_song)

    return db_song


@router.get("/spotify/recommendations/{song_id}", response_model=List[schemas.SpotifyTrack])
async def get_spotify_recommendations(
        song_id: int,
        limit: int = Query(10, ge=1, le=50),
        db: AsyncSession = Depends(get_db),
        spotify_client: SpotifyClient = Depends(deps.get_spotify_client),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    query = select(models.Song).filter(models.Song.id == song_id)
    result = await db.execute(query)
    song = result.scalars().first()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    try:
        related_tracks = await spotify_client.get_related_tracks(song.spotify_id, limit=limit)
        return related_tracks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Spotify API error: {str(e)}"
        )