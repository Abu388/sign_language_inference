import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.audio_stt import AudioSTTService

router = APIRouter()
logger = logging.getLogger(__name__)

# Singleton instance
stt_service = AudioSTTService()

class AudioRequest(BaseModel):
    audio_base64: str   # base64-encoded WAV bytes (16kHz, mono, LINEAR16)
    lang: str = "en"

class AudioResponse(BaseModel):
    text: str
    confidence: float = 0.0  # optional, not returned by current transcribe()

@router.post("/stt-from-audio", response_model=AudioResponse)
async def stt_from_audio(req: AudioRequest):
    """
    Accept base64 audio (WAV, LINEAR16, 16kHz, mono) and return transcribed text.
    """
    import base64
    try:
        audio_bytes = base64.b64decode(req.audio_base64)
        transcript = stt_service.transcribe(audio_bytes, lang=req.lang)
        if not transcript:
            raise HTTPException(400, "No speech detected")
        return AudioResponse(text=transcript)
    except Exception as e:
        logger.exception("STT from audio failed")
        raise HTTPException(500, str(e))