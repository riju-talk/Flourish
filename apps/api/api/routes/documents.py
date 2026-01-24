from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from ..services.ollama_service import OllamaService
from ..core.auth import verify_firebase_token

router = APIRouter()

@router.post("/analyze-document")
async def analyze_document(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_firebase_token)
):
    """Agentic Document Analysis: Extract care info from images/PDFs"""
    try:
        # For now, we simulate the extraction logic using Ollama's vision capabilities
        # In a real setup, you'd send the file bytes to a vision model
        filename = file.filename
        content_type = file.content_type
        
        # Simulate AI analysis result
        summary = f"I've analyzed {filename}. It appears to be a care guide for a Calathea. Key findings: Needs high humidity and distilled water."
        
        return {
            "success": True,
            "filename": filename,
            "analysis": summary,
            "recommendations": [
                "Move to a humid area (bathroom or near humidifier)",
                "Avoid direct mid-day sun",
                "Ensure soil stays moist but not soggy"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
