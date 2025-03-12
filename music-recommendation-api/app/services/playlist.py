import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas
from datetime import datetime

logger = logging.getLogger(__name__)

class PlaylistService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_playlists(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.Playlist]:
        stmt = (
            select(models.Playlist)
            .where(models.Playlist.user_id == user_id)
            .order_by(desc(models.Playlist.updated_at))
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
        
    async def get_playlist_with_songs(
        self, 
        playlist_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Optional[Dict[str, Any]]:

        playlist_stmt = (
            select(models.Playlist)
            .where(models.Playlist.id == playlist_id)
        )
        
        result = await self.db.execute(playlist_stmt)
        playlist = result.scalars().first()
        
        if not playlist:
            return None
            
        songs_stmt = (
            select(models.PlaylistSong)
            .where(models.PlaylistSong.playlist_id == playlist_id)
            .order_by(models.PlaylistSong.position)
            .offset(skip)
            .limit(limit)
            .options(selectinload(models.PlaylistSong.song))
        )
        
        songs_result = await self.db.execute(songs_stmt)
        playlist_songs = songs_result.scalars().all()
        
        songs = [ps.song for ps in playlist_songs]
        
        return {
            "playlist": playlist,
            "songs": songs,
            "total_songs": playlist.song_count
        }

    async def create_playlist(
        self, 
        user_id: int, 
        data: schemas.PlaylistCreate
    ) -> models.Playlist:
        now = datetime.utcnow()
        
        db_playlist = models.Playlist(
            user_id=user_id,
            title=data.title,
            description=data.description,
            is_public=data.is_public if data.is_public is not None else True,
            song_count=0,
            created_at=now,
            updated_at=now
        )
        
        self.db.add(db_playlist)
        await self.db.commit()
        await self.db.refresh(db_playlist)
        
        return db_playlist

    async def update_playlist(
        self, 
        playlist_id: int, 
        user_id: int, 
        data: schemas.PlaylistUpdate
    ) -> Optional[models.Playlist]:
        stmt = (
            select(models.Playlist)
            .where(
                and_(
                    models.Playlist.id == playlist_id,
                    models.Playlist.user_id == user_id
                )
            )
        )
        
        result = await self.db.execute(stmt)
        playlist = result.scalars().first()
        
        if not playlist:
            return None
        
        update_data = data.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(playlist, key, value)
        
        playlist.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(playlist)
        
        return playlist

    async def delete_playlist(
        self, 
        playlist_id: int, 
        user_id: int
    ) -> bool:
        stmt = (
            select(models.Playlist)
            .where(
                and_(
                    models.Playlist.id == playlist_id,
                    models.Playlist.user_id == user_id
                )
            )
        )
        
        result = await self.db.execute(stmt)
        playlist = result.scalars().first()
        
        if not playlist:
            return False
        
        await self.db.delete(playlist)
        await self.db.commit()
        
        return True

    async def add_song_to_playlist(
        self, 
        playlist_id: int, 
        user_id: int, 
        song_id: int
    ) -> Optional[models.PlaylistSong]:
        stmt = (
            select(models.Playlist)
            .where(
                and_(
                    models.Playlist.id == playlist_id,
                    models.Playlist.user_id == user_id
                )
            )
        )
        
        result = await self.db.execute(stmt)
        playlist = result.scalars().first()
        
        if not playlist:
            return None
        
        song_stmt = select(models.Song).where(models.Song.id == song_id)
        song_result = await self.db.execute(song_stmt)
        song = song_result.scalars().first()
        
        if not song:
            return None
            
        existing_stmt = (
            select(models.PlaylistSong)
            .where(
                and_(
                    models.PlaylistSong.playlist_id == playlist_id,
                    models.PlaylistSong.song_id == song_id
                )
            )
        )
        
        existing_result = await self.db.execute(existing_stmt)
        existing = existing_result.scalars().first()
        
        if existing:
            return existing
        
        position_stmt = (
            select(func.max(models.PlaylistSong.position))
            .where(models.PlaylistSong.playlist_id == playlist_id)
        )
        
        position_result = await self.db.execute(position_stmt)
        max_position = position_result.scalar() or 0
        
        playlist_song = models.PlaylistSong(
            playlist_id=playlist_id,
            song_id=song_id,
            position=max_position + 1,
            added_at=datetime.utcnow()
        )
        
        self.db.add(playlist_song)
        
        playlist.song_count += 1
        playlist.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(playlist_song)
        
        return playlist_song

    async def remove_song_from_playlist(
        self, 
        playlist_id: int, 
        user_id: int, 
        song_id: int
    ) -> bool:
        stmt = (
            select(models.Playlist)
            .where(
                and_(
                    models.Playlist.id == playlist_id,
                    models.Playlist.user_id == user_id
                )
            )
        )
        
        result = await self.db.execute(stmt)
        playlist = result.scalars().first()
        
        if not playlist:
            return False
        
        playlist_song_stmt = (
            select(models.PlaylistSong)
            .where(
                and_(
                    models.PlaylistSong.playlist_id == playlist_id,
                    models.PlaylistSong.song_id == song_id
                )
            )
        )
        
        playlist_song_result = await self.db.execute(playlist_song_stmt)
        playlist_song = playlist_song_result.scalars().first()
        
        if not playlist_song:
            return False
        
        removed_position = playlist_song.position
        
        await self.db.delete(playlist_song)

        update_stmt = (
            select(models.PlaylistSong)
            .where(
                and_(
                    models.PlaylistSong.playlist_id == playlist_id,
                    models.PlaylistSong.position > removed_position
                )
            )
        )
        
        update_result = await self.db.execute(update_stmt)
        songs_to_update = update_result.scalars().all()
        
        for song in songs_to_update:
            song.position -= 1
        
        playlist.song_count = max(0, playlist.song_count - 1)
        playlist.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        return True
        
    async def update_song_position(
        self,
        playlist_id: int,
        user_id: int,
        song_id: int,
        new_position: int
    ) -> Optional[models.PlaylistSong]:
        stmt = (
            select(models.Playlist)
            .where(
                and_(
                    models.Playlist.id == playlist_id,
                    models.Playlist.user_id == user_id
                )
            )
        )
        
        result = await self.db.execute(stmt)
        playlist = result.scalars().first()
        
        if not playlist:
            return None
            
        song_stmt = (
            select(models.PlaylistSong)
            .where(
                and_(
                    models.PlaylistSong.playlist_id == playlist_id,
                    models.PlaylistSong.song_id == song_id
                )
            )
        )
        
        song_result = await self.db.execute(song_stmt)
        playlist_song = song_result.scalars().first()
        
        if not playlist_song:
            return None
            
        current_position = playlist_song.position
        
        valid_new_position = max(1, min(new_position, playlist.song_count))
        
        if current_position == valid_new_position:
            return playlist_song
            
        if current_position < valid_new_position:
            update_stmt = (
                select(models.PlaylistSong)
                .where(
                    and_(
                        models.PlaylistSong.playlist_id == playlist_id,
                        models.PlaylistSong.position > current_position,
                        models.PlaylistSong.position <= valid_new_position
                    )
                )
            )
            
            update_result = await self.db.execute(update_stmt)
            songs_to_update = update_result.scalars().all()
            
            for song in songs_to_update:
                song.position -= 1
        else:
            update_stmt = (
                select(models.PlaylistSong)
                .where(
                    and_(
                        models.PlaylistSong.playlist_id == playlist_id,
                        models.PlaylistSong.position < current_position,
                        models.PlaylistSong.position >= valid_new_position
                    )
                )
            )
            
            update_result = await self.db.execute(update_stmt)
            songs_to_update = update_result.scalars().all()
            
            for song in songs_to_update:
                song.position += 1
                
        playlist_song.position = valid_new_position
        
        playlist.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(playlist_song)
        
        return playlist_song