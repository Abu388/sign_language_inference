from pydantic import BaseModel
from typing import Optional

class PredictionResponse(BaseModel):
    success: bool
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    full_sentence: Optional[str] = None   # if frontend sends existing sentence
    error: Optional[str] = None