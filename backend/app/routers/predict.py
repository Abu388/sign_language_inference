import shutil
import logging
import os
from pathlib import Path          # <-- ADD THIS LINE
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from ..schemas.response import PredictionResponse
from ..services.inference_service import InferenceService
from ..core.config import TEMP_DIR, MAX_VIDEO_SIZE_MB, ALLOWED_VIDEO_EXTENSIONS

router = APIRouter()
logger = logging.getLogger(__name__)
inference_service = InferenceService()

@router.post("/predict", response_model=PredictionResponse)
async def predict_video(
    video: UploadFile = File(...),
    current_sentence: str = Form(default="")
):
    if not video.filename:
        raise HTTPException(400, "No file provided")

    ext = Path(video.filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type. Allowed: {ALLOWED_VIDEO_EXTENSIONS}")

    file_size = 0
    chunk_size = 1024 * 1024
    temp_path = TEMP_DIR / f"upload_{Path(video.filename).stem}_{os.getpid()}{ext}"
    with open(temp_path, "wb") as buffer:
        while chunk := await video.read(chunk_size):
            file_size += len(chunk)
            if file_size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
                temp_path.unlink(missing_ok=True)
                raise HTTPException(413, f"File too large. Max {MAX_VIDEO_SIZE_MB}MB")
            buffer.write(chunk)

    try:
        word, confidence = inference_service.predict(temp_path)
    except Exception as e:
        logger.exception("Inference failed")
        temp_path.unlink(missing_ok=True)
        return PredictionResponse(success=False, error=str(e))
    finally:
        temp_path.unlink(missing_ok=True)

    full_sentence = current_sentence.strip()
    if full_sentence:
        full_sentence = full_sentence + " " + word
    else:
        full_sentence = word

    return PredictionResponse(
        success=True,
        prediction=word,
        confidence=confidence,
        full_sentence=full_sentence
    )