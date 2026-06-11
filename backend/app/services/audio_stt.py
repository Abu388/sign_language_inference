"""
Audio capture and Speech‑to‑Text service.
Uses existing SpeechService for Google STT.
"""
import logging
import sys
import threading
import io
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

# Default recording parameters
SAMPLE_RATE = 16000  # Hz – optimal for Google STT
CHANNELS = 1


class AudioSTTService:
    """Record from microphone and transcribe using SpeechService."""

    def __init__(self, speech_service=None):
        """
        Args:
            speech_service: instance of SpeechService (from speech_service.py).
                           If None, will be created on first use.
        """
        self._speech_service = speech_service

    def _get_speech_service(self):
        if self._speech_service is None:
            try:
                from .speech_service import SpeechService
                self._speech_service = SpeechService()
            except ImportError as e:
                logger.error("Failed to import SpeechService: %s", e)
                raise
        return self._speech_service

    def record_audio(self, sample_rate: int = SAMPLE_RATE) -> Optional[bytes]:
        """
        Record from default microphone until user presses Enter.

        Returns:
            WAV bytes (LINEAR16, 16kHz, mono) or None if no audio.
        """
        try:
            import sounddevice as sd
            import soundfile as sf
        except ImportError:
            logger.error("sounddevice or soundfile not installed. Run: pip install sounddevice soundfile numpy")
            sys.exit(1)

        print("\n  Press ENTER to start recording …")
        try:
            input()
        except EOFError:
            return None

        frames = []
        done = threading.Event()

        def callback(indata, _frames, _time, _status):
            frames.append(indata.copy())

        def wait_for_stop():
            try:
                input()
            except EOFError:
                pass
            finally:
                done.set()

        print("  Recording … press ENTER when done")
        stopper = threading.Thread(target=wait_for_stop, daemon=True)
        stopper.start()

        with sd.InputStream(
            samplerate=sample_rate,
            channels=CHANNELS,
            dtype="int16",
            callback=callback,
        ):
            done.wait()

        stopper.join(timeout=0.1)

        if not frames:
            print("  [!] No audio captured.")
            return None

        audio = np.concatenate(frames, axis=0)
        seconds = len(audio) / sample_rate
        print(f"  Recording complete ({seconds:.1f}s)")

        buf = io.BytesIO()
        sf.write(buf, audio, sample_rate, format="WAV", subtype="PCM_16")
        return buf.getvalue()

    def transcribe(self, audio_bytes: bytes, lang: str = "en") -> str:
        """
        Transcribe audio bytes (WebM/Opus from browser) using Google STT.
        """
        svc = self._get_speech_service()
        import base64
        import requests

        STT_URL = "https://speech.googleapis.com/v1/speech:recognize"

        def _bcp47(l: str) -> str:
            return {"en": "en-US", "am": "am-ET", "om": "om-ET"}.get(l, "en-US")

        def _alt_bcp47(primary: str) -> list:
            all_codes = ["en-US", "am-ET", "om-ET"]
            return [c for c in all_codes if c != _bcp47(primary)]

        # Browser MediaRecorder with audio/webm produces Opus in WebM container at 48kHz
        payload = {
            "config": {
                "encoding": "WEBM_OPUS",            # ← changed from LINEAR16
                "sampleRateHertz": 48000,           # ← browser default
                "languageCode": _bcp47(lang),
                "enableAutomaticPunctuation": True,
                "model": "latest_long",
                "alternativeLanguageCodes": _alt_bcp47(lang),
            },
            "audio": {"content": base64.b64encode(audio_bytes).decode()},
        }

        try:
            resp = requests.post(
                STT_URL,
                params={"key": svc.stt_key},
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error("STT request failed: %s", e)
            return ""

        results = resp.json().get("results", [])
        if not results:
            print("  [!] No speech detected — try speaking louder or closer to the mic.")
            return ""

        transcript = results[0]["alternatives"][0].get("transcript", "")
        confidence = results[0]["alternatives"][0].get("confidence", 0.0)
        print(f"  📝  Transcript ({confidence:.0%} confidence): \"{transcript}\"")
        return transcript