from firebase_admin import storage
from datetime import timedelta
import uuid
from typing import Optional

class FirebaseStorage:
    """Firebase Storage operations"""
    
    @staticmethod
    def get_bucket():
        """Get the default Firebase Storage bucket"""
        return storage.bucket()
    
    @staticmethod
    def upload_file(file_content: bytes, destination_path: str, content_type: str = "application/octet-stream") -> str:
        """
        Upload a file to Firebase Storage
        
        Args:
            file_content: The file content as bytes
            destination_path: The destination path in storage (e.g., 'users/user_id/plants/image.jpg')
            content_type: The MIME type of the file
            
        Returns:
            The public URL of the uploaded file
        """
        bucket = FirebaseStorage.get_bucket()
        blob = bucket.blob(destination_path)
        blob.upload_from_string(file_content, content_type=content_type)
        
        # Make the blob publicly accessible
        blob.make_public()
        
        return blob.public_url
    
    @staticmethod
    def generate_signed_url(file_path: str, expiration_minutes: int = 60) -> str:
        """
        Generate a signed URL for a file (for private access)
        
        Args:
            file_path: The path to the file in storage
            expiration_minutes: How long the URL should be valid (in minutes)
            
        Returns:
            A signed URL that allows temporary access to the file
        """
        bucket = FirebaseStorage.get_bucket()
        blob = bucket.blob(file_path)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )
        
        return url
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file from Firebase Storage
        
        Args:
            file_path: The path to the file in storage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            bucket = FirebaseStorage.get_bucket()
            blob = bucket.blob(file_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    @staticmethod
    def upload_plant_image(user_id: str, plant_id: str, file_content: bytes, content_type: str) -> str:
        """
        Upload a plant image
        
        Args:
            user_id: The user's ID
            plant_id: The plant's ID
            file_content: The image file content
            content_type: The MIME type of the image
            
        Returns:
            The public URL of the uploaded image
        """
        file_extension = content_type.split('/')[-1]
        timestamp = str(uuid.uuid4())
        destination_path = f"users/{user_id}/plants/{plant_id}/{timestamp}.{file_extension}"
        
        return FirebaseStorage.upload_file(file_content, destination_path, content_type)
    
    @staticmethod
    def upload_document(user_id: str, file_content: bytes, filename: str, content_type: str) -> str:
        """
        Upload a document
        
        Args:
            user_id: The user's ID
            file_content: The document file content
            filename: The original filename
            content_type: The MIME type of the document
            
        Returns:
            The public URL of the uploaded document
        """
        timestamp = str(uuid.uuid4())
        safe_filename = filename.replace(' ', '_')
        destination_path = f"users/{user_id}/documents/{timestamp}_{safe_filename}"
        
        return FirebaseStorage.upload_file(file_content, destination_path, content_type)
    
    @staticmethod
    def upload_profile_photo(user_id: str, file_content: bytes, content_type: str) -> str:
        """
        Upload a user profile photo
        
        Args:
            user_id: The user's ID
            file_content: The image file content
            content_type: The MIME type of the image
            
        Returns:
            The public URL of the uploaded profile photo
        """
        file_extension = content_type.split('/')[-1]
        destination_path = f"users/{user_id}/profile/avatar.{file_extension}"
        
        return FirebaseStorage.upload_file(file_content, destination_path, content_type)
