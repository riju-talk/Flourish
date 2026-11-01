"""
Tests for persistent chat sessions (ChatGPT-style). FirestoreDB's session methods are
replaced with an in-memory fake and GroqService is stubbed, so these exercise the route
logic (ownership, history windowing, titling, failed-turn handling) without any network.
"""
import itertools
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

with patch("firebase_admin.initialize_app"), \
     patch("firebase_admin.auth.verify_id_token", return_value={"uid": "test-user-123"}), \
     patch("firebase_admin.credentials.Certificate"):
    from main import app

from api.core.auth import verify_firebase_token
from api.db.firestore import FirestoreDB
from api.models.chat import ChatResponse
from api.services.groq_service import GroqService

_current_user = {"uid": "alice"}
app.dependency_overrides[verify_firebase_token] = lambda: _current_user["uid"]
client = TestClient(app)

_clock = itertools.count()


def _tick() -> datetime:
    return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=next(_clock))


@pytest.fixture(autouse=True)
def fake_store(monkeypatch):
    sessions, messages = {}, {}
    ids = itertools.count(1)
    _current_user["uid"] = "alice"

    async def create(user_id, title=None):
        sid = f"s{next(ids)}"
        now = _tick()
        sessions[sid] = {"user_id": user_id, "title": (title or "New chat"),
                         "title_locked": bool(title), "message_count": 0,
                         "created_at": now, "updated_at": now}
        messages[sid] = []
        return {"id": sid, **sessions[sid]}

    async def get(sid, user_id):
        s = sessions.get(sid)
        return {"id": sid, **s} if s and s["user_id"] == user_id else None

    async def list_(user_id):
        out = [{"id": k, **v} for k, v in sessions.items() if v["user_id"] == user_id]
        return sorted(out, key=lambda s: s["updated_at"], reverse=True)

    async def update(sid, updates):
        sessions[sid].update(updates)

    async def get_msgs(sid, limit=None):
        msgs = messages[sid]
        return msgs[-limit:] if limit else list(msgs)

    async def add_msg(sid, role, content, suggestions=None):
        m = {"id": f"m{next(ids)}", "role": role, "content": content,
             "suggestions": suggestions or [], "created_at": _tick()}
        messages[sid].append(m)
        return m

    async def delete(sid):
        sessions.pop(sid, None)
        messages.pop(sid, None)

    for name, fn in [("create_chat_session", create), ("get_chat_session", get),
                     ("list_chat_sessions", list_), ("update_chat_session", update),
                     ("get_chat_messages", get_msgs), ("add_chat_message", add_msg),
                     ("delete_chat_session", delete)]:
        monkeypatch.setattr(FirestoreDB, name, staticmethod(fn))
    return sessions, messages


@pytest.fixture
def ai_ok(monkeypatch):
    chat = AsyncMock(return_value=ChatResponse(response="Water weekly.", suggestions=["More?"]))
    monkeypatch.setattr(GroqService, "chat_with_ai", chat)
    monkeypatch.setattr(GroqService, "generate_chat_title", AsyncMock(return_value="Watering schedule"))
    return chat


def _new():
    return client.post("/api/chat/sessions", json={}).json()["id"]


def test_create_and_list_newest_first():
    a, b = _new(), _new()
    ids = [s["id"] for s in client.get("/api/chat/sessions").json()]
    assert ids == [b, a]


def test_send_message_persists_both_turns_and_auto_titles(ai_ok):
    sid = _new()
    r = client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "How often do I water a fern?"})
    body = r.json()
    assert r.status_code == 200 and body["error"] is False
    assert body["session"]["title"] == "Watering schedule"
    assert body["user_message"]["role"] == "user"
    assert body["assistant_message"]["content"] == "Water weekly."

    detail = client.get(f"/api/chat/sessions/{sid}").json()
    assert [m["role"] for m in detail["messages"]] == ["user", "assistant"]
    assert detail["message_count"] == 2


def test_history_is_loaded_server_side_for_follow_ups(ai_ok):
    sid = _new()
    client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "first"})
    client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "second"})
    turns = ai_ok.call_args_list[-1].args[0]
    assert [t.content for t in turns] == ["first", "Water weekly.", "second"]


def test_only_first_message_triggers_titling(ai_ok):
    sid = _new()
    client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "one"})
    client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "two"})
    assert GroqService.generate_chat_title.await_count == 1


def test_manual_rename_is_not_overwritten_by_auto_title(ai_ok):
    sid = _new()
    r = client.patch(f"/api/chat/sessions/{sid}", json={"title": "  My   ferns  "})
    assert r.json()["title"] == "My ferns"
    client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "hi"})
    assert client.get(f"/api/chat/sessions/{sid}").json()["title"] == "My ferns"


def test_failed_ai_turn_is_not_saved(monkeypatch):
    monkeypatch.setattr(GroqService, "chat_with_ai", AsyncMock(
        return_value=ChatResponse(response="I'm having trouble", error=True)))
    sid = _new()
    body = client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "hello"}).json()
    assert body["error"] is True and body["user_message"] is None
    detail = client.get(f"/api/chat/sessions/{sid}").json()
    assert detail["messages"] == [] and detail["title"] == "New chat"


def test_rejects_empty_and_oversized_messages(ai_ok):
    sid = _new()
    assert client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "   "}).status_code == 422
    assert client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "x" * 4001}).status_code == 422
    assert client.patch(f"/api/chat/sessions/{sid}", json={"title": "  "}).status_code == 422


def test_other_users_cannot_read_modify_or_delete_a_session(ai_ok):
    sid = _new()
    _current_user["uid"] = "mallory"
    assert client.get(f"/api/chat/sessions/{sid}").status_code == 404
    assert client.patch(f"/api/chat/sessions/{sid}", json={"title": "x"}).status_code == 404
    assert client.delete(f"/api/chat/sessions/{sid}").status_code == 404
    assert client.post(f"/api/chat/sessions/{sid}/messages", json={"content": "hi"}).status_code == 404
    assert client.get("/api/chat/sessions").json() == []


def test_delete_removes_session():
    sid = _new()
    assert client.delete(f"/api/chat/sessions/{sid}").status_code == 204
    assert client.get(f"/api/chat/sessions/{sid}").status_code == 404


def test_fallback_title_truncates():
    assert GroqService.fallback_title("  hello   world ") == "hello world"
    assert GroqService.fallback_title("x" * 100) == "x" * 40 + "…"
    assert GroqService.fallback_title("") == "New chat"
