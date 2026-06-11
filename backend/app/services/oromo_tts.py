"""
oromo_tts.py  —  MediBridge
============================
Local Afan Oromo Text-to-Speech using Facebook MMS-TTS (facebook/mms-tts-orm).

This module provides a drop-in replacement for Google Cloud TTS for the Oromo
language, where no cloud voice exists. The model is loaded lazily on first use
and cached for the lifetime of the process.

Dependencies
------------
    pip install transformers torch scipy numpy

GPU support is automatic: the model moves to CUDA if available, otherwise CPU.
"""

from __future__ import annotations

import io
import logging
import subprocess
import threading
from functools import lru_cache
from typing import Optional

import numpy as np
import scipy.io.wavfile
import scipy.signal

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
MODEL_ID      = "facebook/mms-tts-orm"
TARGET_SAMPLE_RATE = 22050   # Standard rate; MMS native is ~16 kHz
MAX_TEXT_CHARS = 500         # Hard cap to prevent OOM on long inputs


# ── Lazy singleton — loaded once, reused across all calls 

_lock         = threading.Lock()
_oromo_tts:   Optional["OromoTTS"] = None


def get_oromo_tts() -> "OromoTTS":
    """Return the process-level OromoTTS singleton, loading it on first call."""
    global _oromo_tts
    if _oromo_tts is None:
        with _lock:                       # double-checked locking
            if _oromo_tts is None:
                _oromo_tts = OromoTTS()
    return _oromo_tts


# ── Main class 

class OromoTTS:
    """
    Wraps facebook/mms-tts-orm for production use inside MediBridge.

    Thread safety
    -------------
    PyTorch inference is not thread-safe on CPU without care.
    A per-instance lock serialises concurrent synthesize() calls.

    Usage
    -----
    >>> tts = OromoTTS()
    >>> mp3_bytes = tts.synthesize_to_mp3("Baga nagaan dhufte!")
    """

    def __init__(self, device: str = None):
        """
        Parameters
        ----------
        device : str | None
            'cuda', 'cpu', or None (auto-detect).
        """
        # Lazy imports — don't crash at module load if torch isn't installed
        try:
            import torch
            from transformers import VitsModel, AutoTokenizer
        except ImportError as exc:
            raise ImportError(
                "OromoTTS requires 'transformers' and 'torch'.\n"
                "Install them with:  pip install transformers torch"
            ) from exc

        self._torch = torch
        self._lock  = threading.Lock()

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("[OromoTTS] Loading %s on %s …", MODEL_ID, self.device)

        self.tokenizer   = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model       = (
            VitsModel.from_pretrained(MODEL_ID)
            .to(self.device)
            .eval()                        # disable dropout for inference
        )
        self.sample_rate: int = self.model.config.sampling_rate

        logger.info(
            "[OromoTTS] Ready — native sample rate %d Hz, device=%s",
            self.sample_rate, self.device
        )

    # ── Core synthesis 

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        """
        Synthesise Afan Oromo text to a waveform.

        Parameters
        ----------
        text : str
            Afan Oromo text (max MAX_TEXT_CHARS characters).

        Returns
        -------
        waveform   : np.ndarray — float32, shape (samples,)
        sample_rate: int        — native rate from the model config
        """
        text = text.strip()
        if not text:
            raise ValueError("[OromoTTS] Empty text received.")
        if len(text) > MAX_TEXT_CHARS:
            logger.warning(
                "[OromoTTS] Text truncated from %d to %d chars.",
                len(text), MAX_TEXT_CHARS
            )
            text = text[:MAX_TEXT_CHARS]

        torch = self._torch

        with self._lock:                   # serialise GPU/CPU access
            inputs = self.tokenizer(text, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                waveform_tensor = self.model(**inputs).waveform

        # waveform_tensor shape: (1, samples) or (samples,) — normalise to 1-D
        waveform = waveform_tensor.squeeze().cpu().numpy().astype(np.float32)
        return waveform, self.sample_rate

    # ── Format helpers 

    def synthesize_to_wav_bytes(self, text: str) -> bytes:
        """Synthesise text and return raw WAV bytes (PCM 16-bit)."""
        waveform, rate = self.synthesize(text)
        pcm16 = _float32_to_pcm16(waveform)

        buf = io.BytesIO()
        scipy.io.wavfile.write(buf, rate, pcm16)
        return buf.getvalue()

    def synthesize_to_mp3(self, text: str, bitrate: str = "128k") -> bytes:
        """
        Synthesise text and return MP3 bytes, compatible with the existing
        Google TTS interface (which also returns MP3).

        Parameters
        ----------
        text    : str — Afan Oromo text
        bitrate : str — MP3 bitrate passed to pydub (default '128k')

        Returns
        -------
        bytes — MP3 audio, ready to stream or save
        """
        wav_bytes = self.synthesize_to_wav_bytes(text)
        return _wav_bytes_to_mp3(wav_bytes, bitrate=bitrate)

    def synthesize_to_file(self, text: str, path: str) -> None:
        """Convenience: synthesise and write a WAV file to *path*."""
        waveform, rate = self.synthesize(text)
        pcm16 = _float32_to_pcm16(waveform)
        scipy.io.wavfile.write(path, rate, pcm16)
        logger.info("[OromoTTS] Wrote WAV to %s", path)


# ── Private helpers ───────────────────────────────────────────────────────────

def _float32_to_pcm16(waveform: np.ndarray) -> np.ndarray:
    """Convert float32 waveform [-1, 1] to int16 PCM, clipping to be safe."""
    clipped = np.clip(waveform, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16)


def _wav_bytes_to_mp3(wav_bytes: bytes, bitrate: str = "128k") -> bytes:
    """
    Convert WAV bytes → MP3 bytes using ffmpeg directly.

    Falls back gracefully: if ffmpeg is not available, returns the
    original WAV bytes with a warning so audio still works, just as WAV.
    """
    try:
        proc = subprocess.run(
            ["ffmpeg", "-y", "-i", "pipe:0", "-f", "mp3", "-b:a", bitrate, "pipe:1"],
            input=wav_bytes,
            capture_output=True,
            timeout=30,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout
        logger.warning(
            "[OromoTTS] ffmpeg conversion failed (return code %d) — "
            "returning WAV instead of MP3.",
            proc.returncode,
        )
    except FileNotFoundError:
        logger.warning(
            "[OromoTTS] ffmpeg not found — returning WAV instead of MP3. "
            "Install ffmpeg and ensure it is on your PATH."
        )
    except Exception as exc:
        logger.warning(
            "[OromoTTS] ffmpeg conversion error: %s — returning WAV.",
            exc,
        )

    return wav_bytes