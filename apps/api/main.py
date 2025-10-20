from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routes import plants, dashboard, chat, tasks, images
from api.core.config import settings
from api.core.auth import verify_firebase_token

# Initialize FastAPI
app = FastAPI(
    title="Flourish",
    description="Your Plant Care Companion",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with authentication dependency
app.include_router(plants.router, prefix="/api/plants", tags=["plants"], dependencies=[Depends(verify_firebase_token)])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(verify_firebase_token)])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"], dependencies=[Depends(verify_firebase_token)])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"], dependencies=[Depends(verify_firebase_token)])
app.include_router(images.router, prefix="/api/images", tags=["images"], dependencies=[Depends(verify_firebase_token)])

@app.get("/")
async def root():
    return {"message": "Flourish - Your Plant Care Companion"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Flourish"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )