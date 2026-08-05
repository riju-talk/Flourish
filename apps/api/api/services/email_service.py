from typing import Optional
from ..db.firestore import FirestoreDB

# Which profiles.notification_preferences key gates each notification type.
# A value of None means that type is never emailed (in-app only).
TYPE_TO_PREFERENCE = {
    "task_due": "email_task_reminders",
    "task_completed": None,
    "achievement": "email_achievements",
    "streak_risk": "email_streak_risk",
    "recommendation_ready": "email_recommendations",
    "health_score_change": None,
    "analysis_complete": None,
}

class EmailService:
    """
    Writes to the `mail` collection (consumed by the Firebase Trigger Email extension)
    and the paired `email_logs` collection - see docs/03-Data-Schema.md and
    docs/04-Rules-of-Engagement.md Rule 13. Every send is gated by the user's
    notification_preferences.
    """

    @staticmethod
    async def send_for_notification(
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        trigger: str = "event"
    ) -> Optional[dict]:
        preference_key = TYPE_TO_PREFERENCE.get(notification_type)
        if preference_key is None:
            return None

        profile = await FirestoreDB.get_profile(user_id)
        if not profile:
            return None

        preferences = profile.get("notification_preferences") or {}
        if not preferences.get(preference_key, False):
            return None

        email = profile.get("email")
        if not email:
            return None

        html = f"<p>{message}</p><p style=\"color:#588157\">— Flourish 🌿</p>"
        return await FirestoreDB.enqueue_email(
            user_id=user_id,
            to_email=email,
            subject=title,
            html=html,
            email_type=notification_type,
            trigger=trigger
        )

    @staticmethod
    async def send_digest(user_id: str, subject: str, html: str) -> Optional[dict]:
        """Scheduled digest emails (e.g. weekly summary) - gated on email_task_reminders."""
        profile = await FirestoreDB.get_profile(user_id)
        if not profile:
            return None

        preferences = profile.get("notification_preferences") or {}
        if not preferences.get("email_task_reminders", False):
            return None

        email = profile.get("email")
        if not email:
            return None

        return await FirestoreDB.enqueue_email(
            user_id=user_id,
            to_email=email,
            subject=subject,
            html=html,
            email_type="digest",
            trigger="scheduled"
        )
