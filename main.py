from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import warpcast_api

app = FastAPI(title="Warpcast MCP Server")


class CastRequest(BaseModel):
    text: str


class ChannelRequest(BaseModel):
    channel_id: str


@app.post("/post-cast")
def post_cast(req: CastRequest):
    result = warpcast_api.post_cast(req.text)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/user-casts/{username}")
def user_casts(username: str, limit: int = 20):
    return warpcast_api.get_user_casts(username, limit)


@app.get("/search-casts")
def search_casts(q: str, limit: int = 20):
    return warpcast_api.search_casts(q, limit)


@app.get("/trending-casts")
def trending_casts(limit: int = 20):
    return warpcast_api.get_trending_casts(limit)


@app.get("/channels")
def all_channels():
    return warpcast_api.get_all_channels()


@app.get("/channels/{channel_id}")
def get_channel(channel_id: str):
    return warpcast_api.get_channel(channel_id)


@app.get("/channels/{channel_id}/casts")
def channel_casts(channel_id: str, limit: int = 20):
    return warpcast_api.get_channel_casts(channel_id, limit)


@app.post("/follow-channel")
def follow_channel(req: ChannelRequest):
    result = warpcast_api.follow_channel(req.channel_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/unfollow-channel")
def unfollow_channel(req: ChannelRequest):
    result = warpcast_api.unfollow_channel(req.channel_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result
