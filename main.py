from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import os
import sys
from urllib.parse import urlparse

import logging
from typing import Optional

import warpcast_api

logger = logging.getLogger(__name__)

app = FastAPI(title="Warpcast MCP Server")

# Queues for SSE communication (one per connection)
mcp_queues: set[asyncio.Queue] = set()

# Allowed origins for SSE connections. We include some common defaults so
# Claude Desktop can connect out of the box.
ALLOWED_ORIGINS = {
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "claude://desktop.claude.ai,https://claude.ai,http://localhost:3000",
    ).split(",")
    if o.strip()
}


def _origin_allowed(origin: str) -> bool:
    """Return True if the origin is localhost or in ALLOWED_ORIGINS."""
    if not origin:
        return False
    if origin in ALLOWED_ORIGINS:
        return True
    try:
        parsed = urlparse(origin)
    except ValueError:
        return False
    # Allow localhost, loopback and file URLs used by desktop clients
    if parsed.scheme == "file":
        return True
    return parsed.hostname in {"localhost", "127.0.0.1"}

# Tool definitions exposed via MCP
TOOLS = [
    {
        "name": "post-cast",
        "description": "Create a new post on Warpcast (max 320 characters)",
    },
    {
        "name": "get-user-casts",
        "description": "Retrieve recent casts from a specific user",
    },
    {
        "name": "search-casts",
        "description": "Search for casts by keyword or phrase",
    },
    {
        "name": "get-trending-casts",
        "description": "Get the currently trending casts on Warpcast",
    },
    {
        "name": "get-all-channels",
        "description": "List available channels on Warpcast",
    },
    {
        "name": "get-channel",
        "description": "Get information about a specific channel",
    },
    {
        "name": "get-channel-casts",
        "description": "Get casts from a specific channel",
    },
    {
        "name": "follow-channel",
        "description": "Follow a channel",
    },
    {
        "name": "unfollow-channel",
        "description": "Unfollow a channel",
    },
]


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


async def _event_generator(queue: asyncio.Queue):
    """Yield server-sent events from the queue."""
    try:
        while True:
            data = await queue.get()
            print(f"SSE send: {data}", file=sys.stderr)
            if isinstance(data, dict) and "event" in data and "data" in data:
                event = data["event"]
                payload = data["data"]
            else:
                event = "message"
                payload = data
            yield f"event: {event}\ndata: {json.dumps(payload)}\n\n"
    finally:
        # Connection closed
        print("SSE connection closed", file=sys.stderr)
        mcp_queues.discard(queue)


@app.get("/mcp")
async def mcp_stream(request: Request):
    """Establish an SSE connection for MCP messages."""
    origin = request.headers.get("origin")
    print(f"/mcp GET from origin: {origin}", file=sys.stderr)
    if not origin or not _origin_allowed(origin):
        print("Origin not allowed", file=sys.stderr)
        raise HTTPException(status_code=403)
    queue = asyncio.Queue()
    mcp_queues.add(queue)
    await queue.put({"event": "endpoint", "data": "/mcp"})
    return StreamingResponse(_event_generator(queue), media_type="text/event-stream")


@app.post("/mcp")
async def mcp_message(request: Request):
    """Handle JSON-RPC messages sent by the client."""
    origin = request.headers.get("origin")
    print(f"/mcp POST from origin: {origin}", file=sys.stderr)
    if not origin or not _origin_allowed(origin):
        print("Origin not allowed", file=sys.stderr)
        raise HTTPException(status_code=403)
    message = await request.json()
    print(f"Received message: {message}", file=sys.stderr)

    if message.get("method") == "initialize":
        if not mcp_queues:
            raise HTTPException(status_code=400, detail="MCP stream not established")

        response = {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "Warpcast MCP Server", "version": "0.1.0"},
            },
        }
        for q in list(mcp_queues):
            print("Sending initialize response", file=sys.stderr)
            await q.put(response)
        return {"status": "ok"}

    if message.get("method") == "tools/list":
        if not mcp_queues:
            raise HTTPException(status_code=400, detail="MCP stream not established")
        response = {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {"tools": TOOLS, "nextCursor": None},
        }
        for q in list(mcp_queues):
            print("Sending tools/list response", file=sys.stderr)
            await q.put(response)
        return {"status": "ok"}

    raise HTTPException(status_code=404, detail="Method not found")
    

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
