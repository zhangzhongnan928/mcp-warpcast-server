import json
import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_post_cast(monkeypatch):
    def mock_post_cast(text):
        return {"status": "success", "text": text}

    monkeypatch.setattr(main.warpcast_api, "post_cast", mock_post_cast)
    response = client.post("/post-cast", json={"text": "hello"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "text": "hello"}


def test_user_casts(monkeypatch):
    def mock_user_casts(username, limit=20):
        return {"casts": [f"{username}-{limit}"]}

    monkeypatch.setattr(main.warpcast_api, "get_user_casts", mock_user_casts)
    response = client.get("/user-casts/alice?limit=5")
    assert response.status_code == 200
    assert response.json() == {"casts": ["alice-5"]}


def test_search_casts(monkeypatch):
    def mock_search_casts(q, limit=20):
        return {"results": [q, limit]}

    monkeypatch.setattr(main.warpcast_api, "search_casts", mock_search_casts)
    response = client.get("/search-casts?q=test&limit=3")
    assert response.status_code == 200
    assert response.json() == {"results": ["test", 3]}


def test_trending_casts(monkeypatch):
    def mock_trending_casts(limit=20):
        return {"trending": limit}

    monkeypatch.setattr(main.warpcast_api, "get_trending_casts", mock_trending_casts)
    response = client.get("/trending-casts?limit=4")
    assert response.status_code == 200
    assert response.json() == {"trending": 4}


def test_all_channels(monkeypatch):
    def mock_all_channels():
        return {"channels": []}

    monkeypatch.setattr(main.warpcast_api, "get_all_channels", mock_all_channels)
    response = client.get("/channels")
    assert response.status_code == 200
    assert response.json() == {"channels": []}


def test_get_channel(monkeypatch):
    def mock_get_channel(channel_id):
        return {"channel": channel_id}

    monkeypatch.setattr(main.warpcast_api, "get_channel", mock_get_channel)
    response = client.get("/channels/123")
    assert response.status_code == 200
    assert response.json() == {"channel": "123"}


def test_channel_casts(monkeypatch):
    def mock_channel_casts(channel_id, limit=20):
        return {"casts": [channel_id, limit]}

    monkeypatch.setattr(main.warpcast_api, "get_channel_casts", mock_channel_casts)
    response = client.get("/channels/abc/casts?limit=2")
    assert response.status_code == 200
    assert response.json() == {"casts": ["abc", 2]}


def test_follow_channel(monkeypatch):
    def mock_follow_channel(channel_id):
        return {"status": "success", "channel": channel_id}

    monkeypatch.setattr(main.warpcast_api, "follow_channel", mock_follow_channel)
    response = client.post("/follow-channel", json={"channel_id": "xyz"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "channel": "xyz"}


def test_unfollow_channel(monkeypatch):
    def mock_unfollow_channel(channel_id):
        return {"status": "success", "channel": channel_id}

    monkeypatch.setattr(main.warpcast_api, "unfollow_channel", mock_unfollow_channel)
    response = client.post("/unfollow-channel", json={"channel_id": "xyz"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "channel": "xyz"}


def test_mcp_stream_invalid_origin():
    response = client.get("/mcp", headers={"Origin": "http://evil.com"})
    assert response.status_code == 403


def test_mcp_stream_missing_origin():
    response = client.get("/mcp")
    assert response.status_code == 403

