from datetime import datetime
from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Interaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("song.id", ondelete="CASCADE"), nullable=False)
    listen_count = Column(Integer, default=0, nullable=False)
    like_score = Column(Float, default=0.0, nullable=False)
    saved = Column(Boolean, default=False, nullable=False)
    context = Column(JSONB, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="interactions")
    song = relationship("Song", back_populates="interactions")