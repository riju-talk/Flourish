from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import Optional
from ..core.auth import verify_firebase_token
from ..db.storage import FirebaseStorage

router = APIRouter()

@router.post("/upload/plant-image/{plant_id}")
async def upload_plant_image(
    plant_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(verify_firebase_token)
):
    """
    Upload a plant image to Firebase Storage
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Firebase Storage
        url = FirebaseStorage.upload_plant_image(
            user_id=user_id,
            plant_id=plant_id,
            file_content=file_content,
            content_type=file.content_type
        )
        
        return {
            "success": True,
            "url": url,
            "message": "Image uploaded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@router.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_firebase_token)
):
    """
    Upload a document to Firebase Storage
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to Firebase Storage
        url = FirebaseStorage.upload_document(
            user_id=user_id,
            file_content=file_content,
            filename=file.filename or "document",
            content_type=file.content_type or "application/octet-stream"
        )
        
        return {
            "success": True,
            "url": url,
            "filename": file.filename,
            "message": "Document uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@router.post("/upload/profile-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_firebase_token)
):
    """
    Upload a profile photo to Firebase Storage
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Firebase Storage
        url = FirebaseStorage.upload_profile_photo(
            user_id=user_id,
            file_content=file_content,
            content_type=file.content_type
        )
        
        return {
            "success": True,
            "url": url,
            "message": "Profile photo uploaded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload profile photo: {str(e)}")

@router.delete("/delete/{file_path:path}")
async def delete_file(
    file_path: str,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Delete a file from Firebase Storage
    Note: This checks that the file path contains the user's ID for security
    """
    try:
        # Security check: ensure the file belongs to the user
        if f"users/{user_id}/" not in file_path:
            raise HTTPException(status_code=403, detail="Unauthorized to delete this file")
        
        success = FirebaseStorage.delete_file(file_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete file")
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
