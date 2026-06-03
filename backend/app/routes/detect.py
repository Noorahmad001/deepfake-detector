import os
import sys
import random
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from app.services.file_service import save_upload_file, delete_file
from app.database.connection import get_database

router = APIRouter()

# ─── Model Setup ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")

print(f"📁 Backend dir: {BASE_DIR}")
print(f"📁 Model dir: {MODEL_DIR}")

sys.path.insert(0, os.path.abspath(MODEL_DIR))

AI_MODEL_AVAILABLE = False
predict_image_fn = None
predict_video_fn = None

try:
    from hf_detector import (
        load_pretrained_model,
        predict_image,
        predict_video
    )
    load_pretrained_model()
    predict_image_fn = predict_image
    predict_video_fn = predict_video
    AI_MODEL_AVAILABLE = True
    print("✅ AI Model loaded successfully")
except Exception as e:
    print(f"⚠️  AI Model not available: {e}")
    print("⚠️  Using mock results")


# ─── Image Detection ──────────────────────────────────────────────────────────
@router.post("/detect-image")
async def detect_image(
    file: UploadFile = File(...),
    session_id: str = Query(default=None)
):
    file_path = None
    try:
        print(f"📁 Received: {file.filename}")
        print(f"🔑 Session: {session_id}")

        file_path = await save_upload_file(file, "image")

        if AI_MODEL_AVAILABLE:
            print("🤖 Using real AI model")
            result = predict_image_fn(file_path)
        else:
            print("⚠️  Using mock result")
            result = {
                "prediction": random.choice(["REAL", "FAKE"]),
                "confidence": round(random.uniform(0.65, 0.95), 4)
            }

        print(f"✅ Result: {result}")

        await save_to_db(
            file_name=file.filename,
            file_type="image",
            prediction=result["prediction"],
            confidence=result["confidence"],
            frames_analyzed=None,
            session_id=session_id
        )

        return JSONResponse(content={
            "file_name": file.filename,
            "file_type": "image",
            "prediction": result["prediction"],
            "confidence": float(result["confidence"]),
            "frames_analyzed": None,
            "created_at": datetime.utcnow().isoformat()
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )
    finally:
        if file_path and os.path.exists(file_path):
            delete_file(file_path)


# ─── Video Detection ──────────────────────────────────────────────────────────
@router.post("/detect-video")
async def detect_video(
    file: UploadFile = File(...),
    session_id: str = Query(default=None)
):
    file_path = None
    try:
        print(f"📁 Received video: {file.filename}")
        print(f"🔑 Session: {session_id}")

        file_path = await save_upload_file(file, "video")

        if AI_MODEL_AVAILABLE:
            print("🤖 Using real AI model")
            result = predict_video_fn(file_path)
        else:
            print("⚠️  Using mock result")
            result = {
                "prediction": random.choice(["REAL", "FAKE"]),
                "confidence": round(random.uniform(0.65, 0.95), 4),
                "frames_analyzed": random.randint(5, 10)
            }

        print(f"✅ Result: {result}")

        await save_to_db(
            file_name=file.filename,
            file_type="video",
            prediction=result["prediction"],
            confidence=result["confidence"],
            frames_analyzed=result.get("frames_analyzed"),
            session_id=session_id
        )

        return JSONResponse(content={
            "file_name": file.filename,
            "file_type": "video",
            "prediction": result["prediction"],
            "confidence": float(result["confidence"]),
            "frames_analyzed": result.get("frames_analyzed"),
            "created_at": datetime.utcnow().isoformat()
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )
    finally:
        if file_path and os.path.exists(file_path):
            delete_file(file_path)


# ─── Save to Database ─────────────────────────────────────────────────────────
async def save_to_db(
    file_name,
    file_type,
    prediction,
    confidence,
    frames_analyzed=None,
    session_id=None
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
                "created_at": datetime.utcnow()
            })
            print("✅ Saved to MongoDB")
        else:
            print("⚠️  No database — skipping save")
    except Exception as e:
        print(f"⚠️  DB error: {e}")