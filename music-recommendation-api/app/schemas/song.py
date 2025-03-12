from datetime import datetime
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, Field


class SongBase(BaseModel):
    spotify_id: str
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


class SpotifyArtist(BaseModel):
    id: str
    name: str


class SpotifyAlbum(BaseModel):
    id: str
    name: str
    images: List[Dict[str, Any]]


class SpotifyTrack(BaseModel):
    id: str
    name: str
    href: str
    duration_ms: int
    popularity: Optional[int] = None
    album: SpotifyAlbum
    artists: List[SpotifyArtist]
    preview_url: Optional[str] = None
    explicit: bool = False

    @property
    def title(self) -> str:
        return self.name

    @property
    def artist(self) -> str:
        if self.artists and len(self.artists) > 0:
            return self.artists[0].name
        return "Unknown Artist"

    @property
    def artwork_url(self) -> Optional[str]:
        if self.album and self.album.images and len(self.album.images) > 0:
            return self.album.images[0].get("url")
        return None

    def to_song_create(self) -> SongCreate:
        return SongCreate(
            spotify_id=self.id,
            title=self.name,
            artist=self.artist,
            artwork_url=self.artwork_url,
            duration=self.duration_ms,
            genre=None,
        )