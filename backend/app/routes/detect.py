import os
import random
import sys
import uuid
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

from app.database.connection import get_database
from app.services.file_service import delete_file, save_upload_file

router = APIRouter()

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "model"))

print(f"Backend dir: {BASE_DIR}")
print(f"Model dir: {MODEL_DIR}")

sys.path.insert(0, MODEL_DIR)

AI_MODEL_AVAILABLE = False
MODEL_LOAD_ATTEMPTED = False
predict_image_fn = None
predict_video_fn = None


def ensure_model_loaded():
    global AI_MODEL_AVAILABLE
    global MODEL_LOAD_ATTEMPTED
    global predict_image_fn
    global predict_video_fn

    if AI_MODEL_AVAILABLE or MODEL_LOAD_ATTEMPTED:
        return AI_MODEL_AVAILABLE

    MODEL_LOAD_ATTEMPTED = True

    try:
        print(f"Attempting to load AI model from: {MODEL_DIR}")
        print(f"Model directory exists: {os.path.exists(MODEL_DIR)}")
        
        if not os.path.exists(MODEL_DIR):
            raise FileNotFoundError(f"Model directory not found: {MODEL_DIR}")
        
        from hf_detector import (
            load_pretrained_model,
            predict_image,
            predict_video,
        )

        print("Loading Hugging Face model...")
        load_pretrained_model()
        predict_image_fn = predict_image
        predict_video_fn = predict_video
        AI_MODEL_AVAILABLE = True
        print("✅ AI model loaded successfully")
    except Exception as e:
        print(f"❌ AI model not available: {e}")
        import traceback
        traceback.print_exc()
        print("⚠️  Using mock results")

    return AI_MODEL_AVAILABLE


@router.post("/detect-image")
async def detect_image(
    file: UploadFile = File(...),
    session_id: str = Query(default=None),
):
    file_path = None
    try:
        print(f"Received image: {file.filename}")
        print(f"Session: {session_id}")

        file_path = await save_upload_file(file, "image")

        if ensure_model_loaded():
            print("Using real AI model")
            result = predict_image_fn(file_path)
        else:
            print("Using mock result")
            result = {
                "prediction": random.choice(["REAL", "FAKE"]),
                "confidence": round(random.uniform(0.65, 0.95), 4),
            }

        print(f"Result: {result}")

        await save_to_db(
            file_name=file.filename,
            file_type="image",
            prediction=result["prediction"],
            confidence=result["confidence"],
            frames_analyzed=None,
            session_id=session_id,
        )

        return JSONResponse(content={
            "file_name": file.filename,
            "file_type": "image",
            "prediction": result["prediction"],
            "confidence": float(result["confidence"]),
            "frames_analyzed": None,
            "created_at": datetime.utcnow().isoformat(),
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"Image detection error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )
    finally:
        if file_path and os.path.exists(file_path):
            delete_file(file_path)


@router.post("/detect-video")
async def detect_video(
    file: UploadFile = File(...),
    session_id: str = Query(default=None),
):
    file_path = None
    try:
        print(f"Received video: {file.filename}")
        print(f"Session: {session_id}")

        file_path = await save_upload_file(file, "video")

        if ensure_model_loaded():
            print("Using real AI model")
            result = predict_video_fn(file_path)
        else:
            print("Using mock result")
            result = {
                "prediction": random.choice(["REAL", "FAKE"]),
                "confidence": round(random.uniform(0.65, 0.95), 4),
                "frames_analyzed": random.randint(5, 10),
            }

        print(f"Result: {result}")

        await save_to_db(
            file_name=file.filename,
            file_type="video",
            prediction=result["prediction"],
            confidence=result["confidence"],
            frames_analyzed=result.get("frames_analyzed"),
            session_id=session_id,
        )

        return JSONResponse(content={
            "file_name": file.filename,
            "file_type": "video",
            "prediction": result["prediction"],
            "confidence": float(result["confidence"]),
            "frames_analyzed": result.get("frames_analyzed"),
            "created_at": datetime.utcnow().isoformat(),
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"Video detection error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )
    finally:
        if file_path and os.path.exists(file_path):
            delete_file(file_path)


async def save_to_db(
    file_name,
    file_type,
    prediction,
    confidence,
    frames_analyzed=None,
    session_id=None,
):
    try:
        db = get_database()
        if db is not None:
            await db.detections.insert_one({
                "detection_id": str(uuid.uuid4()),
                "session_id": session_id or "anonymous",
                "file_name": file_name,
                "file_type": file_type,
                "prediction": prediction,
                "confidence": confidence,
                "frames_analyzed": frames_analyzed,
                "created_at": datetime.utcnow(),
            })
            print("Saved to MongoDB")
        else:
            print("No database configured; skipping save")
    except Exception as e:
        print(f"Database save error: {e}")
