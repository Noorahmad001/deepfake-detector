import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from app.config.settings import settings

# Allowed file types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", 
    "image/webp", "image/bmp"
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/avi", "video/mov", 
    "video/mkv", "video/webm", "video/quicktime"
}

async def save_upload_file(file: UploadFile, file_type: str) -> str:
    """
    Saves uploaded file to disk and returns the file path.
    """
    # Make sure uploads folder exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Validate file type
    if file_type == "image":
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed: JPG, PNG, WEBP, BMP"
            )
        max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024

    elif file_type == "video":
        if file.content_type not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid video type. Allowed: MP4, AVI, MOV, MKV"
            )
        max_size = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024

    # Generate unique filename to avoid conflicts
    extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size for {file_type} is {settings.MAX_IMAGE_SIZE_MB if file_type == 'image' else settings.MAX_VIDEO_SIZE_MB}MB"
        )

    # Save file to disk
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    print(f"✅ File saved: {file_path}")
    return file_path


def delete_file(file_path: str):
    """
    Deletes a file from disk after processing.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  File deleted: {file_path}")
    except Exception as e:
        print(f"⚠️  Could not delete file: {e}")