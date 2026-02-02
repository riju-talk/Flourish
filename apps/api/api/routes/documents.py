from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from ..services.ollama_service import OllamaService
from ..core.auth import verify_firebase_token
import PyPDF2
import io
from PIL import Image
import pytesseract

router = APIRouter()

@router.post("/analyze-document")
async def analyze_document(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_firebase_token)
):
    """
    Agentic Document Analysis: Extract plant care info from PDFs/text documents
    Users can upload plant care guides, manuals, or documents
    """
    try:
        filename = file.filename
        content_type = file.content_type
        
        # Read file content
        file_content = await file.read()
        
        # Extract text based on file type
        extracted_text = ""
        
        if content_type == "application/pdf" or filename.endswith('.pdf'):
            # Extract text from PDF
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
        
        elif content_type.startswith("text/") or filename.endswith('.txt'):
            # Plain text file
            extracted_text = file_content.decode('utf-8')
        
        elif content_type.startswith("image/"):
            # If image, could use OCR (optional - requires tesseract)
            extracted_text = f"Image file uploaded: {filename}. Image analysis requires additional setup."
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or text files.")
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")
        
        # Use Ollama to analyze the extracted text
        analysis = await OllamaService.analyze_document(extracted_text, "care_guide")
        
        return {
            "success": True,
            "filename": filename,
            "document_length": len(extracted_text),
            "analysis": analysis.get("summary", "Analysis completed"),
            "key_points": analysis.get("key_points", []),
            "watering_schedule": analysis.get("watering_schedule", "Not specified"),
            "fertilizing_schedule": analysis.get("fertilizing_schedule", "Not specified"),
            "light_requirements": analysis.get("light_requirements", "Not specified"),
            "warnings": analysis.get("warnings", []),
            "action_items": analysis.get("action_items", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Document analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze document: {str(e)}")

@router.post("/analyze-text")
async def analyze_text(
    text: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Analyze plant care text directly without file upload"""
    try:
        if len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text too short for analysis")
        
        analysis = await OllamaService.analyze_document(text, "care_guide")
        
        return {
            "success": True,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

