import base64
import logging
import requests
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from ..services.speech_service import SpeechService

router = APIRouter()
logger = logging.getLogger(__name__)

try:
    speech = SpeechService()
except Exception as e:
    logger.error(f"SpeechService init failed: {e}")
    speech = None


@router.post("/interpret")
async def interpret_audio(
    audio: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("en"),
):
    if speech is None:
        raise HTTPException(503, "Speech service not available")

    try:
        audio_bytes = await audio.read()
        logger.info(
            "Interpret request: size=%d, content_type=%s, source=%s, target=%s",
            len(audio_bytes), audio.content_type, source_lang, target_lang,
        )

        if not audio_bytes:
            raise HTTPException(400, "Empty audio file received")

        # Google STT doesn't support Oromo — handle early
        if source_lang == "om":
            raise HTTPException(400, "Oromo speech recognition is not supported yet. Please select Amharic or English as the input language.")

        # Step 1: Speech-to-text
        stt_result = speech.speech_to_text(audio_bytes, source_lang=source_lang)
        transcript = stt_result["text"]

        if not transcript:
            return {
                "transcript": "",
                "translated": False,
                "translated_text": "",
                "audio_b64": "",
            }

        # Step 2: Translate if source != target
        translated = source_lang != target_lang
        translated_text = transcript
        if translated:
            trans_result = speech.translate(
                transcript, target_lang=target_lang, source_lang=source_lang
            )
            translated_text = trans_result["text"]

        # Step 3: Text-to-speech (uses local oromo_tts model when target_lang=om)
        tts_audio = speech.text_to_speech(translated_text, lang=target_lang)
        audio_b64 = base64.b64encode(tts_audio).decode("utf-8")

        return {
            "transcript": transcript,
            "translated": translated,
            "translated_text": translated_text,
            "audio_b64": audio_b64,
        }

    except requests.RequestException as e:
        logger.exception("Google API request failed")
        raise HTTPException(502, f"Upstream API error: {e}")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Interpret failed")
        raise HTTPException(500, str(e))
