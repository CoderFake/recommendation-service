from app.schemas.user import (
    User, UserCreate, UserUpdate, UserInDB, UserInDBBase,
    FirebaseUserProfile, UserRegistration
)

from app.schemas.song import (
    Song, SongCreate, SongUpdate, SongInDB, SongInDBBase,
    SongSearchResult, SpotifyTrack
)

from app.schemas.interaction import (
    Interaction, InteractionCreate, InteractionUpdate,
    InteractionInDB, InteractionEvent
)

from app.schemas.recommendation import (
    RecommendationRequest, SongRecommendation,
    RecommendationResponse, UserTaste
)
