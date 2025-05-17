import asyncio
import sys

import httpx_stub
sys.modules["httpx"] = httpx_stub

import main


def test_post_cast(monkeypatch):
    monkeypatch.setattr(main, "ensure_token", lambda: None)

    async def mock_post_cast(text):
        return {"status": "success", "text": text}

    monkeypatch.setattr(main.warpcast_api, "post_cast", mock_post_cast)
    result = asyncio.run(main.post_cast(main.CastRequest(text="hello")))
    assert result == {"status": "success", "text": "hello"}


def test_user_casts(monkeypatch):
    monkeypatch.setattr(main, "ensure_token", lambda: None)

    async def mock_user_casts(username, limit=20):
        return {"casts": [f"{username}-{limit}"]}

    monkeypatch.setattr(main.warpcast_api, "get_user_casts", mock_user_casts)
    result = asyncio.run(main.user_casts("alice", limit=5))
    assert result == {"casts": ["alice-5"]}


def test_search_casts(monkeypatch):
    monkeypatch.setattr(main, "ensure_token", lambda: None)

    async def mock_search_casts(q, limit=20):
        return {"results": [q, limit]}

    monkeypatch.setattr(main.warpcast_api, "search_casts", mock_search_casts)
    result = asyncio.run(main.search_casts("test", limit=3))
    assert result == {"results": ["test", 3]}


def test_trending_casts(monkeypatch):
    monkeypatch.setattr(main, "ensure_token", lambda: None)

    async def mock_trending_casts(limit=20):
        return {"trending": limit}

    monkeypatch.setattr(main.warpcast_api, "get_trending_casts", mock_trending_casts)
    result = asyncio.run(main.trending_casts(limit=4))
    assert result == {"trending": 4}


def test_all_channels(monkeypatch):
    monkeypatch.setattr(main, "ensure_token", lambda: None)

    async def mock_all_channels():
        return {"channels": []}

    monkeypatch.setattr(main.warpcast_api, "get_all_channels", mock_all_channels)
    result = asyncio.run(main.all_channels())
    assert result == {"channels": []}


def test_get_channel(monkeypatch):
    monkeypatch.setattr(main, "ensure_token", lambda: None)

    async def mock_get_channel(channel_id):
        return {"channel": channel_id}

    monkeypatch.setattr(main.warpcast_api, "get_channel", mock_get_channel)
    result = asyncio.run(main.get_channel("123"))
    assert result == {"channel": "123"}


def test_channel_casts(monkeypatch):
    monkeypatch.setattr(main, "ensure_token", lambda: None)

    async def mock_channel_casts(channel_id, limit=20):
        return {"casts": [channel_id, limit]}

    monkeypatch.setattr(main.warpcast_api, "get_channel_casts", mock_channel_casts)
    result = asyncio.run(main.channel_casts("abc", limit=2))
    assert result == {"casts": ["abc", 2]}


def test_follow_channel(monkeypatch):
    monkeypatch.setattr(main, "ensure_token", lambda: None)

    async def mock_follow_channel(channel_id):
        return {"status": "success", "channel": channel_id}

    monkeypatch.setattr(main.warpcast_api, "follow_channel", mock_follow_channel)
    result = asyncio.run(main.follow_channel(main.ChannelRequest(channel_id="xyz")))
    assert result == {"status": "success", "channel": "xyz"}


def test_unfollow_channel(monkeypatch):
    monkeypatch.setattr(main, "ensure_token", lambda: None)

    async def mock_unfollow_channel(channel_id):
        return {"status": "success", "channel": channel_id}

    monkeypatch.setattr(main.warpcast_api, "unfollow_channel", mock_unfollow_channel)
    result = asyncio.run(main.unfollow_channel(main.ChannelRequest(channel_id="xyz")))
    assert result == {"status": "success", "channel": "xyz"}


def test_post_cast_missing_token(monkeypatch):
    monkeypatch.setattr(main.warpcast_api, "has_token", lambda: False)
    try:
        asyncio.run(main.post_cast(main.CastRequest(text="hi")))
    except main.HTTPException as exc:
        assert exc.status_code == 500
    else:
        assert False, "Expected HTTPException"


def test_auth_helpers_environment(monkeypatch):
    monkeypatch.delenv("WARPCAST_API_TOKEN", raising=False)
    import importlib
    import warpcast_api
    importlib.reload(warpcast_api)
    assert not warpcast_api.has_token()
    assert warpcast_api._auth_headers() == {}
    monkeypatch.setenv("WARPCAST_API_TOKEN", "secret")
    assert warpcast_api.has_token()
    assert warpcast_api._auth_headers() == {"Authorization": "Bearer secret"}


def test_tools_registered():
    # Ensure that the FastMCP server registered the expected tools
    tool_names = {t["name"] for t in main.mcp.tools}
    assert "post-cast" in tool_names

