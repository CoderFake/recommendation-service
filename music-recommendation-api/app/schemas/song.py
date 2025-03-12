from datetime import datetime
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, Field


class SongBase(BaseModel):
    soundcloud_id: str
    title: str
    artist: str
    artwork_url: Optional[str] = None
    duration: Optional[int] = None
    genre: Optional[str] = None


class SongCreate(SongBase):
    features: Optional[Dict[str, Any]] = None


class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    artwork_url: Optional[str] = None
    duration: Optional[int] = None
    genre: Optional[str] = None
    features: Optional[Dict[str, Any]] = None


class SongInDBBase(SongBase):
    id: int
    features: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Song(SongInDBBase):
    pass


class SongInDB(SongInDBBase):
    pass


class SongSearchResult(BaseModel):
    songs: List[Song]
    total: int
    page: int
    size: int


class SoundCloudTrack(BaseModel):
    id: str
    title: str
    permalink_url: str
    duration: int
    user: Dict[str, Any]
    artwork_url: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    playback_count: Optional[int] = None
    likes_count: Optional[int] = None

    @property
    def artist(self) -> str:
        return self.user.get("username", "Unknown Artist")

    def to_song_create(self) -> SongCreate:
        return SongCreate(
            soundcloud_id=self.id,
            title=self.title,
            artist=self.artist,
            artwork_url=self.artwork_url,
            duration=self.duration,
            genre=self.genre,
        )