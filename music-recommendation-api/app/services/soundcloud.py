import asyncio
import logging
from typing import Dict, List, Optional, Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class SoundCloudClient:

    def __init__(self) -> None:
        self.client_id = settings.SOUNDCLOUD_CLIENT_ID
        self.base_url = settings.SOUNDCLOUD_API_BASE_URL
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[
        str, Any]:
        url = f"{self.base_url}{endpoint}"

        if params is None:
            params = {}

        params["client_id"] = self.client_id

        try:
            logger.debug(f"Making {method} request to {url} with params {params}")

            if method.lower() == "get":
                response = await self._client.get(url, params=params)
            elif method.lower() == "post":
                response = await self._client.post(url, json=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"SoundCloud API error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error communicating with SoundCloud: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )

    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        params = {
            "q": query,
            "limit": limit,
            "linked_partitioning": 1,
        }

        response = await self._make_request("get", "/tracks", params)

        if "collection" in response:
            return response["collection"]
        return response

    async def get_track(self, track_id: str) -> Dict[str, Any]:

        return await self._make_request("get", f"/tracks/{track_id}")

    async def get_related_tracks(self, track_id: str, limit: int = 10) -> List[Dict[str, Any]]:

        params = {"limit": limit}

        response = await self._make_request("get", f"/tracks/{track_id}/related", params)

        if "collection" in response:
            return response["collection"]
        return response

    async def get_user_tracks(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:

        params = {"limit": limit}

        response = await self._make_request("get", f"/users/{user_id}/tracks", params)

        if "collection" in response:
            return response["collection"]
        return response

    async def get_track_audio_features(self, track_id: str) -> Dict[str, Any]:
        track = await self.get_track(track_id)

        features = {
            "duration": track.get("duration"),
            "genre": track.get("genre"),
            "bpm": track.get("bpm"),
            "key_signature": track.get("key_signature"),
            "playback_count": track.get("playback_count"),
            "likes_count": track.get("likes_count"),
            "comment_count": track.get("comment_count"),
            "description": track.get("description"),
            "tags": track.get("tag_list", "").split(),
        }

        return features

    async def close(self) -> None:
        await self._client.aclose()