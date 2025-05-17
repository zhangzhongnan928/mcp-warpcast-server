import asyncio
import json
import sys

import httpx_stub
sys.modules["httpx"] = httpx_stub

import main

# Helper request object for mcp_message
class FakeRequest:
    def __init__(self, payload=None, headers=None):
        self._payload = payload or {}
        if headers is None:
            headers = {"origin": "http://localhost"}
        self.headers = headers

    async def json(self):
        return self._payload


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


def test_mcp_multiple_streams():
    async def run_test():
        q1 = asyncio.Queue()
        q2 = asyncio.Queue()
        main.mcp_queues.add(q1)
        main.mcp_queues.add(q2)
        gen1 = main._event_generator(q1)
        gen2 = main._event_generator(q2)
        next1 = asyncio.create_task(gen1.__anext__())
        next2 = asyncio.create_task(gen2.__anext__())
        await main.mcp_message(FakeRequest({"method": "initialize", "id": 1}))
        data1 = await next1
        data2 = await next2
        assert data1 == data2
        lines = data1.splitlines()
        assert lines[0] == "event: message"
        payload = json.loads(lines[1].split("data: ")[1])
        assert payload["result"]["protocolVersion"] == "2024-11-05"
        await gen1.aclose()
        await gen2.aclose()
        assert not main.mcp_queues
    asyncio.run(run_test())


def test_handshake_removed():
    assert not any(route.path == "/handshake" for route in main.app.routes)


def test_mcp_stream_invalid_origin():
    async def run_test():
        try:
            await main.mcp_stream(FakeRequest(headers={"origin": "http://evil.com"}))
        except main.HTTPException as exc:
            assert exc.status_code == 403
        else:
            assert False, "Expected HTTPException"

    asyncio.run(run_test())


def test_mcp_stream_missing_origin():
    async def run_test():
        try:
            await main.mcp_stream(FakeRequest(headers={}))
        except main.HTTPException as exc:
            assert exc.status_code == 403
        else:
            assert False, "Expected HTTPException"

    asyncio.run(run_test())


def test_mcp_stream_initial_event():
    async def run_test():
        main.mcp_queues.clear()
        class Req:
            def __init__(self):
                self.headers = {"origin": "http://localhost"}

        # Establish the stream (but don't consume the returned StreamingResponse)
        await main.mcp_stream(Req())
        assert len(main.mcp_queues) == 1
        queue = next(iter(main.mcp_queues))
        gen = main._event_generator(queue)
        first = await gen.__anext__()
        assert first.startswith("event: endpoint")
        await gen.aclose()
        assert not main.mcp_queues

    asyncio.run(run_test())


def test_mcp_post_invalid_origin():
    async def run_test():
        try:
            await main.mcp_message(FakeRequest({}, headers={"origin": "http://evil.com"}))
        except main.HTTPException as exc:
            assert exc.status_code == 403
        else:
            assert False, "Expected HTTPException"

    asyncio.run(run_test())


def test_mcp_post_missing_origin():

    async def run_test():
        try:
            await main.mcp_message(FakeRequest({"method": "initialize"}, headers={}))
        except main.HTTPException as exc:
            assert exc.status_code == 403
        else:
            assert False, "Expected HTTPException"

    asyncio.run(run_test())


def test_post_cast_missing_token(monkeypatch):
    monkeypatch.setattr(main.warpcast_api, "has_token", lambda: False)
    try:
        main.post_cast(main.CastRequest(text="hi"))
    except main.HTTPException as exc:
        assert exc.status_code == 500
    else:
        assert False, "Expected HTTPException"


def test_mcp_post_unknown_method():
    async def run_test():
        try:
            await main.mcp_message(FakeRequest({"method": "unknown"}))
        except main.HTTPException as exc:
            assert exc.status_code == 404
        else:
            assert False, "Expected HTTPException"

    asyncio.run(run_test())


def test_mcp_post_invalid_json():
    class BadRequest:
        def __init__(self):
            self.headers = {"origin": "http://localhost"}

        async def json(self):
            raise json.JSONDecodeError("bad", "bad", 0)

    async def run_test():
        try:
            await main.mcp_message(BadRequest())
        except main.HTTPException as exc:
            assert exc.status_code == 400
        else:
            assert False, "Expected HTTPException"

    asyncio.run(run_test())

    response = client.post("/mcp", json={"method": "initialize"})
    assert response.status_code == 403


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

