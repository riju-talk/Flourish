from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict
from ..core.auth import verify_firebase_token
from ..db.firestore import FirestoreDB

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except:
                self.disconnect(user_id)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.get("/")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    user_id: str = Depends(verify_firebase_token)
):
    """Get user notifications"""
    try:
        notifications = await FirestoreDB.get_user_notifications(user_id, unread_only, limit)
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")

@router.get("/unread-count")
async def get_unread_count(user_id: str = Depends(verify_firebase_token)):
    """Get count of unread notifications"""
    try:
        notifications = await FirestoreDB.get_user_notifications(user_id, unread_only=True, limit=100)
        return {"count": len(notifications)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unread count: {str(e)}")

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Mark a notification as read"""
    try:
        await FirestoreDB.update_notification(notification_id, {"read": True})
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")

@router.put("/mark-all-read")
async def mark_all_notifications_read(user_id: str = Depends(verify_firebase_token)):
    """Mark all notifications as read"""
    try:
        await FirestoreDB.mark_all_notifications_read(user_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark all as read: {str(e)}")

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Delete a notification"""
    try:
        await FirestoreDB.delete_notification(notification_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")

# Helper function for creating notifications
async def create_notification(user_id: str, notification_type: str, title: str, message: str):
    """Create and send a notification to a user"""
    try:
        notification = await FirestoreDB.create_notification({
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "read": False
        })
        
        # Send via WebSocket if user is connected
        await manager.send_personal_message(user_id, notification)
        
        return notification
    except Exception as e:
        print(f"Failed to create notification: {e}")
        return None
