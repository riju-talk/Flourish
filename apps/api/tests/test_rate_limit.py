import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

with patch("firebase_admin.initialize_app"), \
     patch("firebase_admin.auth.verify_id_token", return_value={"uid": "test-user-123"}), \
     patch("firebase_admin.credentials.Certificate"):
    from main import app

from api.core import rate_limit as rl
from api.core.auth import verify_firebase_token
from api.core.rate_limit import SlidingWindowLimiter
from api.models.chat import ChatResponse
from api.services.groq_service import GroqService


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def test_allows_up_to_limit_then_reports_seconds_to_wait():
    clock = FakeClock()
    lim = SlidingWindowLimiter(clock)
    windows = [(3, 60)]
    assert [lim.check("u", "b", windows) for _ in range(3)] == [None, None, None]
    clock.t += 20
    assert lim.check("u", "b", windows) == 40          # oldest hit expires 60s after t=1000


def test_rejected_requests_are_not_recorded():
    clock = FakeClock()
    lim = SlidingWindowLimiter(clock)
    for _ in range(2):
        lim.check("u", "b", [(2, 60)])
    for _ in range(5):                                  # hammering while blocked...
        assert lim.check("u", "b", [(2, 60)]) is not None
    clock.t += 60                                       # ...must not extend the block
    assert lim.check("u", "b", [(2, 60)]) is None


def test_every_window_is_enforced_and_the_longest_wait_wins():
    clock = FakeClock()
    lim = SlidingWindowLimiter(clock)
    windows = [(2, 10), (3, 100)]                       # burst 2 per 10s, cap 3 per 100s
    assert lim.check("u", "b", windows) is None
    assert lim.check("u", "b", windows) is None
    assert lim.check("u", "b", windows) is not None     # burst full
    clock.t += 11
    assert lim.check("u", "b", windows) is None         # burst cleared, 3rd of 3 used
    clock.t += 11
    assert lim.check("u", "b", windows) == 78           # hourly-style cap now binds (1000+100-1022)


def test_users_and_buckets_are_independent():
    lim = SlidingWindowLimiter(FakeClock())
    assert lim.check("alice", "chat", [(1, 60)]) is None
    assert lim.check("alice", "chat", [(1, 60)]) is not None
    assert lim.check("bob", "chat", [(1, 60)]) is None
    assert lim.check("alice", "lookup", [(1, 60)]) is None


def test_idle_users_are_swept():
    clock = FakeClock()
    lim = SlidingWindowLimiter(clock)
    lim.check("ghost", "b", [(5, 60)])
    clock.t += 400                                      # past both the window and the sweep interval
    lim.check("other", "b", [(5, 60)])
    assert ("ghost", "b") not in lim._hits


@pytest.fixture
def client():
    app.dependency_overrides[verify_firebase_token] = lambda: "rate-user"
    yield TestClient(app)
    app.dependency_overrides.pop(verify_firebase_token, None)


def test_chat_endpoint_returns_429_with_retry_after_once_the_burst_is_spent(client):
    burst = rl.LIMITS["chat"][0][0]
    with patch.object(GroqService, "chat_with_ai", AsyncMock(return_value=ChatResponse(response="ok"))):
        body = [{"role": "user", "content": "hi"}]
        statuses = [client.post("/api/chat/", json=body).status_code for _ in range(burst + 2)]
        blocked = client.post("/api/chat/", json=body)
    assert statuses[:burst] == [200] * burst
    assert statuses[burst:] == [429, 429]
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) >= 1
    assert "wait" in blocked.json()["detail"]


def test_limit_is_per_user(client):
    burst = rl.LIMITS["chat"][0][0]
    with patch.object(GroqService, "chat_with_ai", AsyncMock(return_value=ChatResponse(response="ok"))):
        body = [{"role": "user", "content": "hi"}]
        for _ in range(burst):
            client.post("/api/chat/", json=body)
        assert client.post("/api/chat/", json=body).status_code == 429
        app.dependency_overrides[verify_firebase_token] = lambda: "someone-else"
        assert client.post("/api/chat/", json=body).status_code == 200


def test_can_be_disabled_by_setting(client, monkeypatch):
    monkeypatch.setattr(rl.settings, "RATE_LIMIT_ENABLED", False)
    burst = rl.LIMITS["chat"][0][0]
    with patch.object(GroqService, "chat_with_ai", AsyncMock(return_value=ChatResponse(response="ok"))):
        body = [{"role": "user", "content": "hi"}]
        assert all(client.post("/api/chat/", json=body).status_code == 200 for _ in range(burst + 3))
