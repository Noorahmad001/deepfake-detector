from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# This is what we send BACK to the frontend
class DetectionResult(BaseModel):
    id: Optional[str] = None
    file_name: str
    file_type: str          # 'image' or 'video'
    prediction: str         # 'REAL' or 'FAKE'
    confidence: float       # 0.0 to 1.0
    frames_analyzed: Optional[int] = None  # for videos only
    created_at: Optional[datetime] = None

# This is what we store IN MongoDB
class DetectionRecord(BaseModel):
    file_name: str
    file_type: str
    prediction: str
    confidence: float
    frames_analyzed: Optional[int] = None
    created_at: datetime = datetime.utcnow()