from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse

from fastmcp_stub import FastMCP
from pydantic import BaseModel
import asyncio
import json
import os
import sys
from urllib.parse import urlparse

import logging
from typing import Optional

import warpcast_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("Warpcast MCP Server")
app = mcp.app

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
            logger.debug("SSE send: %s", data)
            if isinstance(data, dict) and "event" in data and "data" in data:
                event = data["event"]
                payload = data["data"]
            else:
                event = "message"
                payload = data
            yield f"event: {event}\ndata: {json.dumps(payload)}\n\n"
    finally:
        # Connection closed
        logger.info("SSE connection closed")
        mcp_queues.discard(queue)


@app.get("/mcp")
async def mcp_stream(request: Request):
    """Establish an SSE connection for MCP messages."""
    origin = request.headers.get("origin")
    logger.info("/mcp GET from origin: %s", origin)
    if not origin or not _origin_allowed(origin):
        logger.info("Origin not allowed")
        raise HTTPException(status_code=403)
    queue = asyncio.Queue()
    mcp_queues.add(queue)
    await queue.put({"event": "endpoint", "data": {"uri": "/mcp"}})
    return StreamingResponse(_event_generator(queue), media_type="text/event-stream")


@app.post("/mcp")
async def mcp_message(request: Request):
    """Handle JSON-RPC messages sent by the client."""
    origin = request.headers.get("origin")
    logger.info("/mcp POST from origin: %s", origin)
    if not origin or not _origin_allowed(origin):
        logger.info("Origin not allowed")
        raise HTTPException(status_code=403)
    
    try:
        message = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    logger.info(f"Received message: {message}")

    method = message.get("method")
    
    if method == "initialize":
        logger.info("Processing initialize request")
        
        if not mcp_queues:
            logger.error("No MCP stream established")
            raise HTTPException(status_code=400, detail="MCP stream not established")

        # Create response for initialize method
        response = {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "Warpcast MCP Server", "version": "0.1.0"},
            },
        }
        
        # Send the response back through all connected queues
        for q in list(mcp_queues):
            try:
                logger.info("Sending initialize response through queue")
                await q.put(response)
            except Exception as e:
                logger.error(f"Error sending response to queue: {e}")
        
        # Also return the response directly through the HTTP response
        logger.info("Returning initialize response directly")
        return JSONResponse(content=response)

    elif method == "tools/list":
        logger.info("Processing tools/list request")
        
        if not mcp_queues:
            logger.error("No MCP stream established")
            raise HTTPException(status_code=400, detail="MCP stream not established")
        
        # Create response for tools/list method
        response = {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {"tools": mcp.tools, "nextCursor": None},
        }
        
        # Send the response back through all connected queues
        for q in list(mcp_queues):
            try:
                logger.info("Sending tools/list response through queue")
                await q.put(response)
            except Exception as e:
                logger.error(f"Error sending response to queue: {e}")
        
        # Also return the response directly through the HTTP response
        logger.info("Returning tools/list response directly")
        return JSONResponse(content=response)

    else:
        logger.error(f"Unknown method: {method}")
        raise HTTPException(status_code=404, detail="Method not found")

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
