import asyncio
import logging
import base64
from typing import Dict, List, Optional, Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class SpotifyClient:
    def __init__(self) -> None:
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.base_url = settings.SPOTIFY_API_BASE_URL
        self._client = httpx.AsyncClient(timeout=30.0)
        self._access_token = None
        self._token_expiry = 0

    async def _get_access_token(self) -> str:
        """Get a new access token or use cached one if still valid"""
        import time

        if self._access_token and time.time() < self._token_expiry:
            return self._access_token

        try:
            # Encode client_id and client_secret in base64
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode("ascii")
            auth_base64 = base64.b64encode(auth_bytes).decode("ascii")

            headers = {
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {"grant_type": "client_credentials"}

            response = await self._client.post(
                "https://accounts.spotify.com/api/token",
                headers=headers,
                data=data
            )

            response.raise_for_status()
            token_data = response.json()

            self._access_token = token_data["access_token"]
            self._token_expiry = time.time() + token_data["expires_in"] - 60  # Buffer of 60 seconds

            return self._access_token
        except Exception as e:
            logger.error(f"Error getting Spotify access token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Spotify authentication error: {str(e)}"
            )

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None,
                            data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        if params is None:
            params = {}

        try:
            # Get a valid access token
            access_token = await self._get_access_token()
            headers = {"Authorization": f"Bearer {access_token}"}

            logger.debug(f"Making {method} request to {url} with params {params}")

            if method.lower() == "get":
                response = await self._client.get(url, params=params, headers=headers)
            elif method.lower() == "post":
                response = await self._client.post(url, params=params, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Spotify API error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error communicating with Spotify: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )

    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for tracks on Spotify"""
        params = {
            "q": query,
            "type": "track",
            "limit": limit
        }

        response = await self._make_request("get", "/search", params)

        if "tracks" in response and "items" in response["tracks"]:
            return response["tracks"]["items"]
        return []

    async def get_track(self, track_id: str) -> Dict[str, Any]:
        """Get details for a specific track"""
        return await self._make_request("get", f"/tracks/{track_id}")

    async def get_related_tracks(self, track_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tracks related to the given track using the recommendations endpoint"""
        # First, get the track to get its audio features
        track = await self.get_track(track_id)

        # Then, get recommendations based on this seed track
        params = {
            "seed_tracks": track_id,
            "limit": limit
        }

        recommendations = await self._make_request("get", "/recommendations", params)

        if "tracks" in recommendations:
            return recommendations["tracks"]
        return []

    async def get_track_audio_features(self, track_id: str) -> Dict[str, Any]:
        features = await self._make_request("get", f"/audio-features/{track_id}")

        track = await self.get_track(track_id)

        result = {
            "duration": track.get("duration_ms"),
            "popularity": track.get("popularity"),
            "explicit": track.get("explicit"),
            "danceability": features.get("danceability"),
            "energy": features.get("energy"),
            "key": features.get("key"),
            "loudness": features.get("loudness"),
            "mode": features.get("mode"),
            "speechiness": features.get("speechiness"),
            "acousticness": features.get("acousticness"),
            "instrumentalness": features.get("instrumentalness"),
            "liveness": features.get("liveness"),
            "valence": features.get("valence"),
            "tempo": features.get("tempo"),
        }

        return result

    async def get_artist_tracks(self, artist_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        response = await self._make_request("get", f"/artists/{artist_id}/top-tracks?market=VN")

        if "tracks" in response:
            return response["tracks"][:limit]
        return []

    async def close(self) -> None:
        await self._client.aclose()