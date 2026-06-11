import base64
import logging
from fastapi import APIRouter, HTTPException
from ..schemas.speech import (
    STTRequest, STTResponse,
    TTSRequest, TTSResponse,
    TranslateRequest, TranslateResponse
)
from ..services.speech_service import SpeechService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialise the service once (uses env vars)
try:
    speech = SpeechService()
    logger.info("SpeechService initialised successfully")
except Exception as e:
    logger.error(f"SpeechService init failed: {e}")
    speech = None

@router.post("/stt", response_model=STTResponse)
async def speech_to_text(req: STTRequest):
    if speech is None:
        raise HTTPException(503, "Speech service not available")
    try:
        audio_bytes = base64.b64decode(req.audio_base64)
        result = speech.speech_to_text(
            audio_bytes,
            source_lang=req.source_lang,
            sample_rate=req.sample_rate
        )
        return STTResponse(
            text=result["text"],
            confidence=result["confidence"],
            lang=result["lang"]
        )
    except Exception as e:
        logger.exception("STT failed")
        raise HTTPException(500, str(e))

@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(req: TTSRequest):
    if speech is None:
        raise HTTPException(503, "Speech service not available")
    try:
        audio_bytes = speech.text_to_speech(
            req.text,
            lang=req.lang,
            speaking_rate=req.speaking_rate
        )
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        return TTSResponse(audio_base64=audio_b64)
    except Exception as e:
        logger.exception("TTS failed")
        raise HTTPException(500, str(e))

@router.post("/translate", response_model=TranslateResponse)
async def translate_text(req: TranslateRequest):
    if speech is None:
        raise HTTPException(503, "Speech service not available")
    try:
        result = speech.translate(
            req.text,
            target_lang=req.target_lang,
            source_lang=req.source_lang
        )
        return TranslateResponse(
            translated_text=result["text"],
            source_detected=result["source_detected"]
        )
    except Exception as e:
        logger.exception("Translation failed")
        raise HTTPException(500, str(e))