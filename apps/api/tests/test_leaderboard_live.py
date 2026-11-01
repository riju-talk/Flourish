import asyncio
from unittest.mock import patch

from api.routes.leaderboard import LeaderboardHub


class FakeWS:
    def __init__(self):
        self.msgs = []

    async def accept(self):
        pass

    async def send_json(self, message):
        self.msgs.append(message)


class FakeWatch:
    def __init__(self):
        self.unsubscribed = False

    def unsubscribe(self):
        self.unsubscribed = True


def _rows(*scores):
    return [
        {"id": f"u{i}", "display_name": f"User {i}", "total_score": s, "email": f"u{i}@x.com",
         "privacy": {}}
        for i, s in enumerate(scores)
    ]


def test_hub_pushes_every_snapshot_and_respects_privacy():
    async def run():
        captured = {}
        watch = FakeWatch()

        def fake_listen(callback, limit=100):
            captured["cb"] = callback
            return watch

        hub = LeaderboardHub()
        a, b = FakeWS(), FakeWS()
        with patch("api.routes.leaderboard.FirestoreDB.listen_leaderboard", side_effect=fake_listen):
            await hub.connect(a, "u0")
            await hub.connect(b, "u1")  # second client reuses the one listener

        # Firestore listener thread reports a change -> every client is pushed
        captured["cb"](_rows(50, 40))
        await asyncio.sleep(0.05)
        captured["cb"](_rows(40, 60))  # u1 overtakes u0
        await asyncio.sleep(0.05)

        assert len(a.msgs) == 2 and len(b.msgs) == 2
        assert [r["id"] for r in b.msgs[-1]["leaderboard"]] == ["u0", "u1"]
        # Each viewer sees only their own contact info
        assert a.msgs[-1]["leaderboard"][0].get("email") == "u0@x.com"
        assert "email" not in b.msgs[-1]["leaderboard"][0]

        hub.disconnect(a)
        assert not watch.unsubscribed          # one client still connected
        hub.disconnect(b)
        assert watch.unsubscribed              # last one out stops the listener

    asyncio.run(run())
