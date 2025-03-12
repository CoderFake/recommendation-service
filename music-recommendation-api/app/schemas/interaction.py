from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field, validator


class InteractionBase(BaseModel):
    user_id: int
    song_id: int
    listen_count: Optional[int] = 0
    like_score: Optional[float] = 0.0
    saved: Optional[bool] = False
    context: Optional[Dict[str, Any]] = None


class InteractionCreate(BaseModel):
    song_id: int
    listen_count: Optional[int] = 1
    like_score: Optional[float] = 0.0
    saved: Optional[bool] = False
    context: Optional[Dict[str, Any]] = None

    @validator('like_score')
    def validate_like_score(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('like_score must be between 0.0 and 1.0')
        return v


class InteractionUpdate(BaseModel):
    listen_count: Optional[int] = None
    like_score: Optional[float] = None
    saved: Optional[bool] = None
    context: Optional[Dict[str, Any]] = None

    @validator('like_score')
    def validate_like_score(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('like_score must be between 0.0 and 1.0')
        return v


class InteractionInDBBase(InteractionBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class Interaction(InteractionInDBBase):
    pass


class InteractionInDB(InteractionInDBBase):
    pass


class InteractionEvent(BaseModel):
    event_type: str = Field(..., description="Type of interaction event (e.g., 'play', 'like', 'skip')")
    song_id: int
    timestamp: Optional[datetime] = None
    duration: Optional[int] = None
    position: Optional[int] = None
    context: Optional[Dict[str, Any]] = None