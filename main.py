from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from typing import Optional

import warpcast_api

logger = logging.getLogger(__name__)

app = FastAPI(title="Warpcast MCP Server")


@app.on_event("startup")
async def validate_token() -> None:
    if not warpcast_api.has_token():
        logger.warning(
            "WARPCAST_API_TOKEN is not set. Requests requiring authorization will fail"
        )


def ensure_token() -> None:
    if not warpcast_api.has_token():
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: WARPCAST_API_TOKEN not set",
        )


class CastRequest(BaseModel):
    text: str


class ChannelRequest(BaseModel):
    channel_id: str


class HandshakeRequest(BaseModel):
    """Payload for MCP handshake."""
    client: Optional[str] = None
    protocol_version: str = "0.1"


@app.post("/handshake")
def handshake(req: HandshakeRequest):
    """Basic MCP handshake endpoint."""
    return {
        "server": "warpcast-mcp-server",
        "protocol_version": req.protocol_version,
    }


@app.post("/post-cast")
def post_cast(req: CastRequest):
    ensure_token()
    result = warpcast_api.post_cast(req.text)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/user-casts/{username}")
def user_casts(username: str, limit: int = 20):
    ensure_token()
    return warpcast_api.get_user_casts(username, limit)


@app.get("/search-casts")
def search_casts(q: str, limit: int = 20):
    ensure_token()
    return warpcast_api.search_casts(q, limit)


@app.get("/trending-casts")
def trending_casts(limit: int = 20):
    ensure_token()
    return warpcast_api.get_trending_casts(limit)


@app.get("/channels")
def all_channels():
    ensure_token()
    return warpcast_api.get_all_channels()


@app.get("/channels/{channel_id}")
def get_channel(channel_id: str):
    ensure_token()
    return warpcast_api.get_channel(channel_id)


@app.get("/channels/{channel_id}/casts")
def channel_casts(channel_id: str, limit: int = 20):
    ensure_token()
    return warpcast_api.get_channel_casts(channel_id, limit)


@app.post("/follow-channel")
def follow_channel(req: ChannelRequest):
    ensure_token()
    result = warpcast_api.follow_channel(req.channel_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/unfollow-channel")
def unfollow_channel(req: ChannelRequest):
    ensure_token()
    result = warpcast_api.unfollow_channel(req.channel_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result
