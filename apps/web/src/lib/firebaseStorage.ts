import { storage } from './firebase';
import { ref, uploadBytes, getDownloadURL, deleteObject } from 'firebase/storage';

export interface UploadResult {
  url: string;
  path: string;
}

/**
 * Upload a file to Firebase Storage
 * @param file - The file to upload
 * @param path - The storage path (e.g., 'plants/plant-id/image.jpg')
 * @returns Promise with download URL and storage path
 */
export async function uploadFile(file: File, path: string): Promise<UploadResult> {
  try {
    const storageRef = ref(storage, path);
    const snapshot = await uploadBytes(storageRef, file);
    const url = await getDownloadURL(snapshot.ref);
    
    return {
      url,
      path: snapshot.ref.fullPath,
    };
  } catch (error) {
    console.error('Error uploading file:', error);
    throw new Error('Failed to upload file');
  }
}

/**
 * Upload a plant image
 * @param file - The image file to upload
 * @param plantId - The plant ID
 * @param userId - The user ID
 * @returns Promise with download URL and storage path
 */
export async function uploadPlantImage(
  file: File,
  plantId: string,
  userId: string
): Promise<UploadResult> {
  const timestamp = Date.now();
  const extension = file.name.split('.').pop();
  const path = `users/${userId}/plants/${plantId}/${timestamp}.${extension}`;
  return uploadFile(file, path);
}

/**
 * Upload a document
 * @param file - The document file to upload
 * @param userId - The user ID
 * @returns Promise with download URL and storage path
 */
export async function uploadDocument(
  file: File,
  userId: string
): Promise<UploadResult> {
  const timestamp = Date.now();
  const sanitizedFileName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_');
  const path = `users/${userId}/documents/${timestamp}_${sanitizedFileName}`;
  return uploadFile(file, path);
}

/**
 * Upload a profile photo
 * @param file - The image file to upload
 * @param userId - The user ID
 * @returns Promise with download URL and storage path
 */
export async function uploadProfilePhoto(
  file: File,
  userId: string
): Promise<UploadResult> {
  const extension = file.name.split('.').pop();
  const path = `users/${userId}/profile/avatar.${extension}`;
  return uploadFile(file, path);
}

/**
 * Delete a file from Firebase Storage
 * @param path - The storage path of the file to delete
 */
export async function deleteFile(path: string): Promise<void> {
  try {
    const storageRef = ref(storage, path);
    await deleteObject(storageRef);
  } catch (error) {
    console.error('Error deleting file:', error);
    throw new Error('Failed to delete file');
  }
}

/**
 * Get download URL for a file
 * @param path - The storage path
 * @returns Promise with the download URL
 */
export async function getFileUrl(path: string): Promise<string> {
  try {
    const storageRef = ref(storage, path);
    return await getDownloadURL(storageRef);
  } catch (error) {
    console.error('Error getting file URL:', error);
    throw new Error('Failed to get file URL');
  }
}
