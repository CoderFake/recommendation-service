from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


# Model cho request gợi ý bài hát
class ContextType(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    WORKOUT = "workout"
    STUDY = "study"
    RELAX = "relax"
    PARTY = "party"


class DeviceType(str, Enum):
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    SPEAKER = "speaker"
    TV = "tv"
    OTHER = "other"


class RecommendationContext(BaseModel):
    """Context thông tin phục vụ gợi ý chính xác hơn"""
    time_of_day: Optional[ContextType] = None
    device: Optional[DeviceType] = None
    previous_songs: Optional[List[str]] = None
    location: Optional[str] = None
    mood: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class SongRecommendationRequest(BaseModel):
    """Request model để yêu cầu gợi ý bài hát"""
    song_id: str = Field(..., description="ID của bài hát gốc để gợi ý")
    user_id: Optional[str] = Field(None, description="ID người dùng để cá nhân hóa gợi ý")
    limit: Optional[int] = Field(10, description="Số lượng bài hát gợi ý trả về", ge=1, le=50)
    context: Optional[RecommendationContext] = Field(None, description="Thông tin ngữ cảnh bổ sung")

    class Config:
        schema_extra = {
            "example": {
                "song_id": "song_12345",
                "user_id": "user_67890",
                "limit": 10,
                "context": {
                    "time_of_day": "evening",
                    "device": "mobile",
                    "previous_songs": ["song_11111", "song_22222"],
                    "location": "home",
                    "mood": "relaxed"
                }
            }
        }


# Model cho Recommendation Type
class RecommendationType(str, Enum):
    SIMILAR_SONG = "similar_song"
    USER_PREFERENCE = "user_preference"
    TRENDING = "trending"
    GENRE_BASED = "genre_based"
    ARTIST_BASED = "artist_based"
    COLLABORATIVE = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    REAL_TIME = "real_time"


class SongRecommendation(BaseModel):
    """Chi tiết về một bài hát được gợi ý"""
    song_id: str
    score: float = Field(..., description="Điểm số phù hợp (0-1)", ge=0, le=1)
    reason: Optional[str] = None
    recommendation_type: RecommendationType


class SongRecommendationResponse(BaseModel):
    """Response model cho gợi ý bài hát"""
    recommended_songs: List[str] = Field(..., description="Danh sách ID bài hát được gợi ý")
    detailed_recommendations: Optional[List[SongRecommendation]] = None
    based_on_song_id: str
    recommendation_reason: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "recommended_songs": ["song_33333", "song_44444", "song_55555"],
                "detailed_recommendations": [
                    {
                        "song_id": "song_33333",
                        "score": 0.95,
                        "reason": "Người dùng thường nghe bài này sau bài gốc",
                        "recommendation_type": "user_preference"
                    }
                ],
                "based_on_song_id": "song_12345",
                "recommendation_reason": "Dựa trên mẫu nghe và sự tương đồng giữa các bài hát"
            }
        }


# Model cho API tạo token
class TokenRequest(BaseModel):
    user_id: str = Field(..., description="ID người dùng cần tạo token")


class TokenResponse(BaseModel):
    access_token: str
    expires_at: int
    token_type: str = "Bearer"