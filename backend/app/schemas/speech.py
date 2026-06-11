from pydantic import BaseModel
from typing import Optional

class STTRequest(BaseModel):
    audio_base64: str   # WebM/Opus bytes encoded as base64
    source_lang: str = "en"
    sample_rate: int = 48000

class STTResponse(BaseModel):
    text: str
    confidence: float
    lang: str

class TTSRequest(BaseModel):
    text: str
    lang: str = "en"
    speaking_rate: float = 0.9

class TTSResponse(BaseModel):
    audio_base64: str   # MP3 bytes as base64

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    source_lang: Optional[str] = None

class TranslateResponse(BaseModel):
    translated_text: str
    source_detected: str