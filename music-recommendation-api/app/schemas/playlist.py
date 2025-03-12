from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.song import Song


class PlaylistBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: Optional[bool] = True


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class PlaylistInDBBase(PlaylistBase):
    id: int
    user_id: int
    song_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Playlist(PlaylistInDBBase):
    pass


class PlaylistSongBase(BaseModel):
    playlist_id: int
    song_id: int
    position: int


class PlaylistSongCreate(BaseModel):
    song_id: int


class PlaylistSongInDBBase(PlaylistSongBase):
    id: int
    added_at: datetime

    class Config:
        orm_mode = True


class PlaylistSong(PlaylistSongInDBBase):
    song: Optional[Song] = None


class PlaylistWithSongs(BaseModel):
    playlist: Playlist
    songs: List[Song]
    total_songs: int