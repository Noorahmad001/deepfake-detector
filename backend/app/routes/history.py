from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.database.connection import get_database
from datetime import datetime
from bson import ObjectId

router = APIRouter()


@router.get("/history")
async def get_history(
    session_id: str = Query(default=None),
    limit: int = Query(default=20)
):
    try:
        db = get_database()

        if db is None:
            return JSONResponse(content={
                "detections": [],
                "message": "Database not connected"
            })

        query = {}

        # Filter by session if provided
        if session_id:
            query["session_id"] = session_id

        cursor = db.detections.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit)

        detections = []
        async for doc in cursor:
            if "created_at" in doc and isinstance(
                doc["created_at"], datetime
            ):
                doc["created_at"] = doc["created_at"].isoformat()
            detections.append(doc)

        return JSONResponse(content={"detections": detections})

    except Exception as e:
        print(f"❌ History error: {e}")
        return JSONResponse(content={"detections": []})


@router.get("/history/clear")
async def clear_my_history(session_id: str = Query(...)):
    try:
        db = get_database()
        if db is None:
            return JSONResponse(content={"message": "No database"})

        result = await db.detections.delete_many(
            {"session_id": session_id}
        )

        return JSONResponse(content={
            "message": f"Cleared {result.deleted_count} records"
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)})


@router.get("/report/{detection_id}")
async def get_report(detection_id: str):
    try:
        db = get_database()
        if db is None:
            return JSONResponse(
                status_code=404,
                content={"detail": "Database not connected"}
            )

        doc = await db.detections.find_one(
            {"detection_id": detection_id},
            {"_id": 0}
        )

        if not doc:
            return JSONResponse(
                status_code=404,
                content={"detail": "Detection not found"}
            )

        if "created_at" in doc and isinstance(
            doc["created_at"], datetime
        ):
            doc["created_at"] = doc["created_at"].isoformat()

        return JSONResponse(content=doc)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )