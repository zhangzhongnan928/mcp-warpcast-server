from fastapi import HTTPException
from pydantic import BaseModel

import logging

import warpcast_api

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - fallback for testing
    from fastmcp_stub import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("Warpcast MCP Server")
app = mcp.app




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

@mcp.tool()
async def post_cast(req: CastRequest):
    ensure_token()
    result = await warpcast_api.post_cast(req.text)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@mcp.tool()
async def user_casts(username: str, limit: int = 20):
    ensure_token()
    return await warpcast_api.get_user_casts(username, limit)


@mcp.tool()
async def search_casts(q: str, limit: int = 20):
    ensure_token()
    return await warpcast_api.search_casts(q, limit)


@mcp.tool()
async def trending_casts(limit: int = 20):
    ensure_token()
    return await warpcast_api.get_trending_casts(limit)


@mcp.tool()
async def all_channels():
    ensure_token()
    return await warpcast_api.get_all_channels()


@mcp.tool()
async def get_channel(channel_id: str):
    ensure_token()
    return await warpcast_api.get_channel(channel_id)


@mcp.tool()
async def channel_casts(channel_id: str, limit: int = 20):
    ensure_token()
    return await warpcast_api.get_channel_casts(channel_id, limit)


@mcp.tool()
async def follow_channel(req: ChannelRequest):
    ensure_token()
    result = await warpcast_api.follow_channel(req.channel_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@mcp.tool()
async def unfollow_channel(req: ChannelRequest):
    ensure_token()
    result = await warpcast_api.unfollow_channel(req.channel_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result
