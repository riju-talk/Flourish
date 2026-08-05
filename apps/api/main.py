from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from api.routes import plants, dashboard, chat, tasks, images, mcp, notifications, leaderboard, storage, auth, recommendations
from api.core.config import settings
from api.core.auth import verify_firebase_token
from api.services.scheduler_service import start_scheduler, stop_scheduler

# Initialize FastAPI
app = FastAPI(
    title="Flourish",
    description="Your Plant Care Companion with AI, Gamification & Real-time Notifications",
    version="1.0.0"
)

# A truly unhandled exception is caught by Starlette's ServerErrorMiddleware, which
# sits OUTSIDE CORSMiddleware - its fallback 500 response never passes back through
# CORSMiddleware, so it carries no Access-Control-Allow-Origin header. Browsers report
# that as "blocked by CORS policy" even though CORS was never the actual problem.
# (Registering @app.exception_handler(Exception) does NOT fix this - Starlette
# special-cases a handler for the base Exception into becoming ServerErrorMiddleware's
# own handler, which is still outside CORSMiddleware.) This middleware is added
# *before* CORSMiddleware below, which places it *inside* CORSMiddleware in the actual
# request pipeline, so any exception it catches turns into a normal response that
# still flows back out through CORSMiddleware and gets proper headers.
class CatchAllExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            print(f"Unhandled error on {request.method} {request.url.path}: {exc}")
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.add_middleware(CatchAllExceptionMiddleware)

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
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])  # HTTP routes each self-enforce verify_firebase_token; a router-level dependency here crashes the /ws route (HTTPBearer can't read a WebSocket's headers)
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
            "Agentic AI Plant Care Assistant (Groq + LangChain)",
            "Personalized Plant Recommendations",
            "Task Scheduling & Calendar",
            "Real-time Notifications & Email",
            "Gamification & Leaderboard",
            "MCP Server Integration"
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