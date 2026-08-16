from firebase_admin import firestore
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ..core.config import settings

# Lazy-initialized Firestore client
_db = None

def get_db():
    """
    Get or initialize the Firestore client lazily. Targets FIRESTORE_DATABASE_ID
    instead of always assuming "(default)" - the project's "(default)" database can
    be provisioned in a mode (e.g. Enterprise edition with the classic Firestore API
    access disabled) that this Admin SDK client can't reach at all, in which case a
    separate named database with standard Firestore access is required.
    """
    global _db
    if _db is None:
        _db = firestore.client(database_id=settings.FIRESTORE_DATABASE_ID)
    return _db

# Collection names
PROFILES_COLLECTION = "profiles"
PLANTS_COLLECTION = "plants"
TASKS_COLLECTION = "care_tasks"
NOTIFICATIONS_COLLECTION = "notifications"
HEALTH_CHECKS_COLLECTION = "health_checks"
RECOMMENDATIONS_COLLECTION = "recommendations"
EMAIL_LOGS_COLLECTION = "email_logs"
MAIL_COLLECTION = "mail"

class FirestoreDB:
    """Firestore database operations"""
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())

    @staticmethod
    def _read_back(collection: str, doc_id: str) -> Dict:
        """
        Re-fetch a just-written document instead of returning the dict that was passed
        to .set(). Any field written as firestore.SERVER_TIMESTAMP stays an unresolved
        Sentinel object in that local dict - Firestore only resolves it server-side -
        so returning it directly hands FastAPI (or a WebSocket send_json) something it
        can't serialize. Every create_* method below reads back through this instead.
        """
        doc = get_db().collection(collection).document(doc_id).get()
        data = doc.to_dict() or {}
        data['id'] = doc_id
        return data

    # ============ PROFILES ============
    
    @staticmethod
    async def get_profile(user_id: str) -> Optional[Dict]:
        """Get user profile"""
        try:
            doc = get_db().collection(PROFILES_COLLECTION).document(user_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            print(f"Error getting profile for {user_id}: {e}")
            return None
    
    @staticmethod
    async def create_profile(
        user_id: str,
        email: str,
        display_name: str = "",
        photo_url: str = "",
        full_name: str = "",
        phone_number: str = ""
    ) -> Dict:
        """Create user profile (onboarding). Privacy defaults to fully private."""
        try:
            profile_data = {
                "email": email,
                "full_name": full_name,
                "phone_number": phone_number,
                "display_name": display_name,
                "photo_url": photo_url,
                "bio": "",
                "total_score": 0,
                "level": 1,
                "tasks_completed": 0,
                "streak_days": 0,
                "last_activity": None,
                "achievements": [],
                "privacy": {
                    "public_profile_enabled": False,
                    "show_email": False,
                    "show_phone": False
                },
                "notification_preferences": {
                    "email_task_reminders": True,
                    "email_achievements": True,
                    "email_streak_risk": True,
                    "email_recommendations": False
                },
                "agent_profile": {
                    "summary": "",
                    "garden_composition": {},
                    "care_habits": {},
                    "recommendation_preferences": {"avoided_plants": [], "preferred_traits": []},
                    "updated_at": None
                },
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP
            }
            get_db().collection(PROFILES_COLLECTION).document(user_id).set(profile_data)
            return FirestoreDB._read_back(PROFILES_COLLECTION, user_id)
        except Exception as e:
            print(f"Error creating profile for {user_id}: {e}")
            raise

    @staticmethod
    async def update_profile(user_id: str, updates: Dict) -> None:
        """Update user profile"""
        updates['updated_at'] = firestore.SERVER_TIMESTAMP
        get_db().collection(PROFILES_COLLECTION).document(user_id).update(updates)

    @staticmethod
    async def get_all_profiles() -> List[Dict]:
        """Get every user profile - used by SchedulerService's per-user sweeps"""
        docs = get_db().collection(PROFILES_COLLECTION).stream()
        profiles = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            profiles.append(data)
        return profiles
    
    # ============ PLANTS ============
    
    @staticmethod
    async def create_plant(user_id: str, plant_data: Dict) -> Dict:
        """Create a new plant"""
        plant_id = FirestoreDB.generate_id()
        plant_data.update({
            "id": plant_id,
            "user_id": user_id,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        get_db().collection(PLANTS_COLLECTION).document(plant_id).set(plant_data)
        return FirestoreDB._read_back(PLANTS_COLLECTION, plant_id)
    
    @staticmethod
    async def get_plant(plant_id: str, user_id: str) -> Optional[Dict]:
        """Get a single plant"""
        doc = get_db().collection(PLANTS_COLLECTION).document(plant_id).get()
        if doc.exists:
            data = doc.to_dict()
            if data.get('user_id') == user_id:
                data['id'] = doc.id
                return data
        return None
    
    @staticmethod
    async def get_user_plants(user_id: str) -> List[Dict]:
        """Get all plants for a user"""
        plants_ref = get_db().collection(PLANTS_COLLECTION).where('user_id', '==', user_id)
        docs = plants_ref.stream()
        plants = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            plants.append(data)
        return plants
    
    @staticmethod
    async def update_plant(plant_id: str, updates: Dict) -> None:
        """Update a plant"""
        updates['updated_at'] = firestore.SERVER_TIMESTAMP
        get_db().collection(PLANTS_COLLECTION).document(plant_id).update(updates)
    
    @staticmethod
    async def delete_plant(plant_id: str) -> None:
        """Delete a plant"""
        get_db().collection(PLANTS_COLLECTION).document(plant_id).delete()
    
    # ============ CARE TASKS ============
    
    @staticmethod
    async def create_task(task_data: Dict) -> Dict:
        """Create a care task"""
        task_id = FirestoreDB.generate_id()
        task_data.update({
            "id": task_id,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        get_db().collection(TASKS_COLLECTION).document(task_id).set(task_data)
        return FirestoreDB._read_back(TASKS_COLLECTION, task_id)
    
    @staticmethod
    async def get_task(task_id: str) -> Optional[Dict]:
        """Get a single task"""
        doc = get_db().collection(TASKS_COLLECTION).document(task_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    @staticmethod
    async def get_user_tasks(user_id: str, completed: Optional[bool] = None) -> List[Dict]:
        """Get all tasks for a user, optionally filtered by completion status"""
        query = get_db().collection(TASKS_COLLECTION).where('user_id', '==', user_id)
        # Push the completed filter down to Firestore instead of streaming every task
        # and filtering in Python - a pure-equality compound filter like this doesn't
        # need a composite index.
        if completed is not None:
            query = query.where('completed', '==', completed)
        docs = query.stream()
        tasks = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            tasks.append(data)
        return tasks
    
    @staticmethod
    async def get_plant_tasks(plant_id: str) -> List[Dict]:
        """Get all tasks for a specific plant"""
        tasks_ref = get_db().collection(TASKS_COLLECTION).where('plant_id', '==', plant_id)
        docs = tasks_ref.stream()
        tasks = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            tasks.append(data)
        return tasks
    
    @staticmethod
    async def update_task(task_id: str, updates: Dict) -> None:
        """Update a task"""
        get_db().collection(TASKS_COLLECTION).document(task_id).update(updates)
    
    @staticmethod
    async def delete_task(task_id: str) -> None:
        """Delete a task"""
        get_db().collection(TASKS_COLLECTION).document(task_id).delete()
    
    # ============ NOTIFICATIONS ============
    
    @staticmethod
    async def create_notification(notification_data: Dict) -> Dict:
        """Create a notification"""
        notif_id = FirestoreDB.generate_id()
        notification_data.update({
            "id": notif_id,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        get_db().collection(NOTIFICATIONS_COLLECTION).document(notif_id).set(notification_data)
        return FirestoreDB._read_back(NOTIFICATIONS_COLLECTION, notif_id)
    
    @staticmethod
    async def get_user_notifications(user_id: str, unread_only: bool = False, limit: int = 50) -> List[Dict]:
        """Get notifications for a user"""
        query = get_db().collection(NOTIFICATIONS_COLLECTION).where('user_id', '==', user_id)
        if unread_only:
            query = query.where('read', '==', False)
        query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        notifications = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            notifications.append(data)
        return notifications
    
    @staticmethod
    async def update_notification(notif_id: str, updates: Dict) -> None:
        """Update a notification"""
        get_db().collection(NOTIFICATIONS_COLLECTION).document(notif_id).update(updates)
    
    @staticmethod
    async def delete_notification(notif_id: str) -> None:
        """Delete a notification"""
        get_db().collection(NOTIFICATIONS_COLLECTION).document(notif_id).delete()
    
    @staticmethod
    async def mark_all_notifications_read(user_id: str) -> None:
        """Mark all user notifications as read"""
        notifications = get_db().collection(NOTIFICATIONS_COLLECTION).where('user_id', '==', user_id).where('read', '==', False).stream()
        for doc in notifications:
            doc.reference.update({'read': True})
    
    # ============ HEALTH CHECKS ============
    
    @staticmethod
    async def create_health_check(health_data: Dict) -> Dict:
        """Create a health check"""
        check_id = FirestoreDB.generate_id()
        health_data.update({
            "id": check_id,
            "checked_at": firestore.SERVER_TIMESTAMP
        })
        get_db().collection(HEALTH_CHECKS_COLLECTION).document(check_id).set(health_data)
        return FirestoreDB._read_back(HEALTH_CHECKS_COLLECTION, check_id)
    
    @staticmethod
    async def get_plant_health_checks(plant_id: str) -> List[Dict]:
        """Get health checks for a plant"""
        checks_ref = get_db().collection(HEALTH_CHECKS_COLLECTION).where('plant_id', '==', plant_id)
        docs = checks_ref.order_by('checked_at', direction=firestore.Query.DESCENDING).stream()
        checks = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            checks.append(data)
        return checks
    
    # ============ RECOMMENDATIONS ============

    @staticmethod
    async def create_recommendation(rec_data: Dict) -> Dict:
        """Create a personalized plant recommendation"""
        rec_id = FirestoreDB.generate_id()
        rec_data.update({
            "id": rec_id,
            "status": rec_data.get("status", "pending"),
            "created_at": firestore.SERVER_TIMESTAMP
        })
        get_db().collection(RECOMMENDATIONS_COLLECTION).document(rec_id).set(rec_data)
        return FirestoreDB._read_back(RECOMMENDATIONS_COLLECTION, rec_id)

    @staticmethod
    async def get_recommendation(rec_id: str) -> Optional[Dict]:
        """Get a single recommendation"""
        doc = get_db().collection(RECOMMENDATIONS_COLLECTION).document(rec_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None

    @staticmethod
    async def get_user_recommendations(user_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get recommendations for a user, optionally filtered by status"""
        query = get_db().collection(RECOMMENDATIONS_COLLECTION).where('user_id', '==', user_id)
        docs = query.stream()
        recommendations = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            if status is None or data.get('status') == status:
                recommendations.append(data)
        return recommendations

    @staticmethod
    async def update_recommendation(rec_id: str, updates: Dict) -> None:
        """Update a recommendation"""
        get_db().collection(RECOMMENDATIONS_COLLECTION).document(rec_id).update(updates)

    # ============ EMAIL (mail + email_logs) ============

    @staticmethod
    async def enqueue_email(user_id: str, to_email: str, subject: str, html: str, email_type: str, trigger: str) -> Dict:
        """
        Write a document to the `mail` collection (consumed by the Firebase Trigger
        Email extension) and a paired `email_logs` entry, per
        docs/04-Rules-of-Engagement.md Rule 13.
        """
        mail_id = FirestoreDB.generate_id()
        mail_data = {
            "id": mail_id,
            "to": [to_email],
            "message": {"subject": subject, "html": html}
        }
        get_db().collection(MAIL_COLLECTION).document(mail_id).set(mail_data)

        log_id = FirestoreDB.generate_id()
        log_data = {
            "id": log_id,
            "user_id": user_id,
            "type": email_type,
            "subject": subject,
            "trigger": trigger,
            "mail_ref": mail_id,
            "sent_at": firestore.SERVER_TIMESTAMP
        }
        get_db().collection(EMAIL_LOGS_COLLECTION).document(log_id).set(log_data)
        return FirestoreDB._read_back(EMAIL_LOGS_COLLECTION, log_id)

    @staticmethod
    async def get_user_email_logs(user_id: str, limit: int = 50) -> List[Dict]:
        """Get this user's email send history"""
        query = get_db().collection(EMAIL_LOGS_COLLECTION).where('user_id', '==', user_id)
        query = query.order_by('sent_at', direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        logs = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            logs.append(data)
        return logs

    # ============ LEADERBOARD ============
    
    @staticmethod
    async def get_leaderboard(limit: int = 100) -> List[Dict]:
        """Get leaderboard sorted by score"""
        profiles_ref = get_db().collection(PROFILES_COLLECTION).order_by('total_score', direction=firestore.Query.DESCENDING).limit(limit)
        docs = profiles_ref.stream()
        leaderboard = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            leaderboard.append(data)
        return leaderboard
    
    @staticmethod
    async def get_user_rank(user_id: str) -> int:
        """Get user's rank on leaderboard"""
        profile = await FirestoreDB.get_profile(user_id)
        if not profile:
            return 0
        
        # Count users with higher score
        higher_scores = get_db().collection(PROFILES_COLLECTION).where('total_score', '>', profile.get('total_score', 0)).stream()
        rank = len(list(higher_scores)) + 1
        return rank
