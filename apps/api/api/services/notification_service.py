from typing import Any, Dict

from ..db.firestore import FirestoreDB


class NotificationService:
    """
    Single entry point for creating a notification. Persists to Firestore AND pushes it
    live over the WebSocket connection the client has open (see routes/notifications.py's
    ConnectionManager) - the real-time "webhook-style" delivery the app promises.

    Every notification-creation call site should go through notify() instead of calling
    FirestoreDB.create_notification() directly - that only persists, it never reaches a
    connected client until their next poll.
    """

    @staticmethod
    async def notify(user_id: str, notification_type: str, title: str, message: str) -> Dict[str, Any]:
        notification = await FirestoreDB.create_notification({
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "read": False,
        })

        # Local import: routes/notifications.py owns the ConnectionManager and doesn't
        # import this module, so there's no real cycle - kept lazy anyway to stay clear
        # of any FastAPI router import-order fragility at app startup.
        from ..routes.notifications import manager
        await manager.send_personal_message(user_id, notification)

        return notification
