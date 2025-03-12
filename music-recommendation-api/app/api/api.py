from fastapi import APIRouter

from app.api.endpoints import auth, songs, interactions, recommendations, playlists

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(songs.router, prefix="/songs", tags=["songs"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(playlists.router, prefix="/playlists", tags=["playlists"])