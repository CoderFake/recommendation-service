from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Song(Base):
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    artist = Column(String, index=True, nullable=False)
    artwork_url = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)
    genre = Column(String, index=True, nullable=True)
    features = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interactions = relationship("Interaction", back_populates="song", cascade="all, delete-orphan")
    playlists = relationship("PlaylistSong", back_populates="song", cascade="all, delete-orphan")