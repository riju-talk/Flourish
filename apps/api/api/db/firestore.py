from firebase_admin import firestore
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

# Get Firestore client
db = firestore.client()

# Collection names
PROFILES_COLLECTION = "profiles"
PLANTS_COLLECTION = "plants"
TASKS_COLLECTION = "care_tasks"
NOTIFICATIONS_COLLECTION = "notifications"
HEALTH_CHECKS_COLLECTION = "health_checks"

class FirestoreDB:
    """Firestore database operations"""
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())
    
    # ============ PROFILES ============
    
    @staticmethod
    async def get_profile(user_id: str) -> Optional[Dict]:
        """Get user profile"""
        doc = db.collection(PROFILES_COLLECTION).document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    @staticmethod
    async def create_profile(user_id: str, email: str, display_name: str = "", photo_url: str = "") -> Dict:
        """Create user profile"""
        profile_data = {
            "email": email,
            "display_name": display_name,
            "photo_url": photo_url,
            "total_score": 0,
            "level": 1,
            "tasks_completed": 0,
            "streak_days": 0,
            "last_activity": None,
            "achievements": [],
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        db.collection(PROFILES_COLLECTION).document(user_id).set(profile_data)
        profile_data['id'] = user_id
        return profile_data
    
    @staticmethod
    async def update_profile(user_id: str, updates: Dict) -> None:
        """Update user profile"""
        updates['updated_at'] = firestore.SERVER_TIMESTAMP
        db.collection(PROFILES_COLLECTION).document(user_id).update(updates)
    
    @staticmethod
    async def get_or_create_profile(user_id: str, email: str, display_name: str = "", photo_url: str = "") -> Dict:
        """Get existing profile or create new one"""
        profile = await FirestoreDB.get_profile(user_id)
        if not profile:
            profile = await FirestoreDB.create_profile(user_id, email, display_name, photo_url)
        return profile
    
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
        db.collection(PLANTS_COLLECTION).document(plant_id).set(plant_data)
        return plant_data
    
    @staticmethod
    async def get_plant(plant_id: str, user_id: str) -> Optional[Dict]:
        """Get a single plant"""
        doc = db.collection(PLANTS_COLLECTION).document(plant_id).get()
        if doc.exists:
            data = doc.to_dict()
            if data.get('user_id') == user_id:
                data['id'] = doc.id
                return data
        return None
    
    @staticmethod
    async def get_user_plants(user_id: str) -> List[Dict]:
        """Get all plants for a user"""
        plants_ref = db.collection(PLANTS_COLLECTION).where('user_id', '==', user_id)
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
        db.collection(PLANTS_COLLECTION).document(plant_id).update(updates)
    
    @staticmethod
    async def delete_plant(plant_id: str) -> None:
        """Delete a plant"""
        db.collection(PLANTS_COLLECTION).document(plant_id).delete()
    
    # ============ CARE TASKS ============
    
    @staticmethod
    async def create_task(task_data: Dict) -> Dict:
        """Create a care task"""
        task_id = FirestoreDB.generate_id()
        task_data.update({
            "id": task_id,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        db.collection(TASKS_COLLECTION).document(task_id).set(task_data)
        return task_data
    
    @staticmethod
    async def get_task(task_id: str) -> Optional[Dict]:
        """Get a single task"""
        doc = db.collection(TASKS_COLLECTION).document(task_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    @staticmethod
    async def get_user_tasks(user_id: str, completed: Optional[bool] = None) -> List[Dict]:
        """Get all tasks for a user"""
        query = db.collection(TASKS_COLLECTION).where('user_id', '==', user_id)
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
        tasks_ref = db.collection(TASKS_COLLECTION).where('plant_id', '==', plant_id)
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
        db.collection(TASKS_COLLECTION).document(task_id).update(updates)
    
    @staticmethod
    async def delete_task(task_id: str) -> None:
        """Delete a task"""
        db.collection(TASKS_COLLECTION).document(task_id).delete()
    
    # ============ NOTIFICATIONS ============
    
    @staticmethod
    async def create_notification(notification_data: Dict) -> Dict:
        """Create a notification"""
        notif_id = FirestoreDB.generate_id()
        notification_data.update({
            "id": notif_id,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        db.collection(NOTIFICATIONS_COLLECTION).document(notif_id).set(notification_data)
        return notification_data
    
    @staticmethod
    async def get_user_notifications(user_id: str, unread_only: bool = False, limit: int = 50) -> List[Dict]:
        """Get notifications for a user"""
        query = db.collection(NOTIFICATIONS_COLLECTION).where('user_id', '==', user_id)
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
        db.collection(NOTIFICATIONS_COLLECTION).document(notif_id).update(updates)
    
    @staticmethod
    async def delete_notification(notif_id: str) -> None:
        """Delete a notification"""
        db.collection(NOTIFICATIONS_COLLECTION).document(notif_id).delete()
    
    @staticmethod
    async def mark_all_notifications_read(user_id: str) -> None:
        """Mark all user notifications as read"""
        notifications = db.collection(NOTIFICATIONS_COLLECTION).where('user_id', '==', user_id).where('read', '==', False).stream()
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
        db.collection(HEALTH_CHECKS_COLLECTION).document(check_id).set(health_data)
        return health_data
    
    @staticmethod
    async def get_plant_health_checks(plant_id: str) -> List[Dict]:
        """Get health checks for a plant"""
        checks_ref = db.collection(HEALTH_CHECKS_COLLECTION).where('plant_id', '==', plant_id)
        docs = checks_ref.order_by('checked_at', direction=firestore.Query.DESCENDING).stream()
        checks = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            checks.append(data)
        return checks
    
    # ============ LEADERBOARD ============
    
    @staticmethod
    async def get_leaderboard(limit: int = 100) -> List[Dict]:
        """Get leaderboard sorted by score"""
        profiles_ref = db.collection(PROFILES_COLLECTION).order_by('total_score', direction=firestore.Query.DESCENDING).limit(limit)
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
        higher_scores = db.collection(PROFILES_COLLECTION).where('total_score', '>', profile.get('total_score', 0)).stream()
        rank = len(list(higher_scores)) + 1
        return rank
