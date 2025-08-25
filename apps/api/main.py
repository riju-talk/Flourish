from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import plants, dashboard, chat, tasks, images
from api.core.config import settings

# Initialize FastAPI
app = FastAPI(
    title="PlantMind AI",
    description="Proactive AI Plant Care Agent",
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

# Include routers
app.include_router(plants.router, prefix="/api/plants", tags=["plants"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(images.router, prefix="/api/images", tags=["images"])

@app.get("/")
async def root():
    return {"message": "PlantMind AI - Your Proactive Plant Care Agent"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "PlantMind AI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )