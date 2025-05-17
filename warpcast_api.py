import os
from typing import Any, Dict

import logging
import httpx

API_BASE_URL = "https://api.warpcast.com/v2"
API_TOKEN = os.getenv("WARPCAST_API_TOKEN")
PROPAGATE_EXCEPTIONS = os.getenv("PROPAGATE_EXCEPTIONS") is not None

logger = logging.getLogger(__name__)


def has_token() -> bool:
    """Return True if the API token is configured."""
    return bool(API_TOKEN)


def _auth_headers() -> Dict[str, str]:
    if not API_TOKEN:
        return {}
    return {"Authorization": f"Bearer {API_TOKEN}"}


async def post_cast(text: str) -> Dict[str, Any]:
    """Create a new cast on Warpcast."""
    url = f"{API_BASE_URL}/casts"
    payload = {"text": text}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, json=payload, headers=_auth_headers(), timeout=10
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        logger.exception("Could not post cast")
        if PROPAGATE_EXCEPTIONS:
            raise
        return {"status": "error", "message": "Could not post cast"}


async def get_user_casts(username: str, limit: int = 20) -> Dict[str, Any]:
    """Retrieve recent casts from a user."""
    url = f"{API_BASE_URL}/users/{username}/casts?limit={limit}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=_auth_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        logger.exception("Could not fetch user casts")
        if PROPAGATE_EXCEPTIONS:
            raise
        return {"status": "error", "message": "Could not fetch user casts"}


async def search_casts(query: str, limit: int = 20) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/casts/search?q={query}&limit={limit}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=_auth_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        logger.exception("Could not search casts")
        if PROPAGATE_EXCEPTIONS:
            raise
        return {"status": "error", "message": "Could not search casts"}


async def get_trending_casts(limit: int = 20) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/casts/trending?limit={limit}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=_auth_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        logger.exception("Could not fetch trending casts")
        if PROPAGATE_EXCEPTIONS:
            raise
        return {"status": "error", "message": "Could not fetch trending casts"}


async def get_all_channels() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/channels"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=_auth_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        logger.exception("Could not fetch channels")
        if PROPAGATE_EXCEPTIONS:
            raise
        return {"status": "error", "message": "Could not fetch channels"}


async def get_channel(channel_id: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/channels/{channel_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=_auth_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        logger.exception("Could not fetch channel")
        if PROPAGATE_EXCEPTIONS:
            raise
        return {"status": "error", "message": "Could not fetch channel"}


async def get_channel_casts(channel_id: str, limit: int = 20) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/channels/{channel_id}/casts?limit={limit}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=_auth_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        logger.exception("Could not fetch channel casts")
        if PROPAGATE_EXCEPTIONS:
            raise
        return {"status": "error", "message": "Could not fetch channel casts"}


async def follow_channel(channel_id: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/channels/{channel_id}/follow"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=_auth_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        logger.exception("Could not follow channel")
        if PROPAGATE_EXCEPTIONS:
            raise
        return {"status": "error", "message": "Could not follow channel"}


async def unfollow_channel(channel_id: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/channels/{channel_id}/unfollow"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=_auth_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        logger.exception("Could not unfollow channel")
        if PROPAGATE_EXCEPTIONS:
            raise
        return {"status": "error", "message": "Could not unfollow channel"}
