from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services.playlist import PlaylistService

router = APIRouter()


@router.get("/", response_model=List[schemas.Playlist])
async def get_user_playlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    playlist_service: PlaylistService = Depends(deps.get_playlist_service)
) -> Any:

    playlists = await playlist_service.get_user_playlists(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return playlists


@router.post("/", response_model=schemas.Playlist, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    playlist_data: schemas.PlaylistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    playlist_service: PlaylistService = Depends(deps.get_playlist_service)
) -> Any:

    playlist = await playlist_service.create_playlist(current_user.id, playlist_data)
    return playlist


@router.get("/{playlist_id}", response_model=schemas.PlaylistWithSongs)
async def get_playlist(
    playlist_id: int = Path(..., ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    playlist_service: PlaylistService = Depends(deps.get_playlist_service)
) -> Any:

    result = await playlist_service.get_playlist_with_songs(
        playlist_id=playlist_id,
        skip=skip,
        limit=limit
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    playlist = result["playlist"]
    
    if playlist.user_id != current_user.id and not playlist.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this playlist"
        )
    
    return result


@router.put("/{playlist_id}", response_model=schemas.Playlist)
async def update_playlist(
    playlist_id: int = Path(..., ge=1),
    playlist_data: schemas.PlaylistUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    playlist_service: PlaylistService = Depends(deps.get_playlist_service)
) -> Any:

    playlist = await playlist_service.update_playlist(
        playlist_id=playlist_id,
        user_id=current_user.id,
        data=playlist_data
    )
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found or you don't have permission to update it"
        )
    
    return playlist


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    playlist_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    playlist_service: PlaylistService = Depends(deps.get_playlist_service)
) -> Any:

    result = await playlist_service.delete_playlist(
        playlist_id=playlist_id,
        user_id=current_user.id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found or you don't have permission to delete it"
        )


@router.post("/{playlist_id}/songs", response_model=schemas.PlaylistSong)
async def add_song_to_playlist(
    playlist_id: int = Path(..., ge=1),
    song_id: int = Query(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    playlist_service: PlaylistService = Depends(deps.get_playlist_service)
) -> Any:

    playlist_song = await playlist_service.add_song_to_playlist(
        playlist_id=playlist_id,
        user_id=current_user.id,
        song_id=song_id
    )
    
    if not playlist_song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found, song not found, or you don't have permission"
        )
    
    return playlist_song


@router.delete("/{playlist_id}/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_song_from_playlist(
    playlist_id: int = Path(..., ge=1),
    song_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    playlist_service: PlaylistService = Depends(deps.get_playlist_service)
) -> Any:

    result = await playlist_service.remove_song_from_playlist(
        playlist_id=playlist_id,
        user_id=current_user.id,
        song_id=song_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found in playlist or you don't have permission"
        )


@router.put("/{playlist_id}/songs/{song_id}/position", response_model=schemas.PlaylistSong)
async def update_song_position(
    playlist_id: int = Path(..., ge=1),
    song_id: int = Path(..., ge=1),
    position: int = Query(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    playlist_service: PlaylistService = Depends(deps.get_playlist_service)
) -> Any:

    playlist_song = await playlist_service.update_song_position(
        playlist_id=playlist_id,
        user_id=current_user.id,
        song_id=song_id,
        new_position=position
    )
    
    if not playlist_song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found in playlist or you don't have permission"
        )
    
    return playlist_song