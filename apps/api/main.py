from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routes import plants, dashboard, chat, tasks, images, mcp, documents, notifications, leaderboard, storage, auth, recommendations
from api.core.config import settings
from api.core.auth import verify_firebase_token
from api.services.scheduler_service import start_scheduler, stop_scheduler

# Initialize FastAPI
app = FastAPI(
    title="Flourish",
    description="Your Plant Care Companion with AI, Gamification & Real-time Notifications",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Startup event
@app.on_event("startup")
async def startup_event():
    print("Starting Flourish API...")
    print("Firebase Firestore ready!")
    print("No database setup needed - using Firebase!")
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()

# Include routers with authentication dependency
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])  # No auth required for profile creation
app.include_router(plants.router, prefix="/api/plants", tags=["plants"], dependencies=[Depends(verify_firebase_token)])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(verify_firebase_token)])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"], dependencies=[Depends(verify_firebase_token)])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"], dependencies=[Depends(verify_firebase_token)])
app.include_router(images.router, prefix="/api/images", tags=["images"], dependencies=[Depends(verify_firebase_token)])
app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"], dependencies=[Depends(verify_firebase_token)])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"], dependencies=[Depends(verify_firebase_token)])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"], dependencies=[Depends(verify_firebase_token)])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"], dependencies=[Depends(verify_firebase_token)])
app.include_router(storage.router, prefix="/api/storage", tags=["storage"], dependencies=[Depends(verify_firebase_token)])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"], dependencies=[Depends(verify_firebase_token)])

@app.get("/")
async def root():
    return {
        "message": "🌱 Flourish - Your Plant Care Companion",
        "version": "1.0.0",
        "features": [
            "Plant Inventory Management",
            "AI-Powered Plant Care Assistant (Ollama)",
            "Task Scheduling & Calendar",
            "Real-time Notifications",
            "Gamification & Leaderboard",
            "MCP Server Integration",
            "Document Analysis"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Flourish API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )