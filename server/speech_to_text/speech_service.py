"""
speech_service.py  —  MediBridge
==================================
Google Cloud TTS + STT + Translation via REST API keys.
Afan Oromo TTS uses a local facebook/mms-tts-orm model (no cloud key needed).

Two separate API keys are supported:
  STT_API_KEY  — for Cloud Speech-to-Text
  TTS_API_KEY  — for Cloud Text-to-Speech
  TRANSLATE_API_KEY — can be either key; Translation API
                      is usually enabled on the same key as STT

Set in your .env file or environment:
    GOOGLE_STT_API_KEY=AIzaSy...   ← your STT key
    GOOGLE_TTS_API_KEY=AIzaSy...   ← your TTS key

Languages supported:
  en  — English
  am  — Amharic     (አማርኛ)
  om  — Afaan Oromo  ← local MMS-TTS model, no cloud voice needed
"""

import os
import base64
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── API keys — loaded from environment, never hardcoded ──────────────────────
STT_API_KEY       = os.environ.get('GOOGLE_STT_API_KEY', '')
TTS_API_KEY       = os.environ.get('GOOGLE_TTS_API_KEY', '')
TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY', '') or STT_API_KEY

# ── Language config ───────────────────────────────────────────────────────────
LANG_CONFIG = {
    'en': {
        'bcp47':        'en-US',
        'tts_name':     'en-US-Neural2-D',
        'tts_gender':   'MALE',
        'display':      'English',
        'tts_backend':  'google',   # 'google' | 'local_mms'
    },
    'am': {
        'bcp47':        'am-ET',
        'tts_name':     'am-ET-Standard-A',
        'tts_gender':   'FEMALE',
        'display':      'Amharic (አማርኛ)',
        'tts_backend':  'google',
    },
    'om': {
        'bcp47':        'om-ET',
        'tts_name':     None,           # no Google Cloud voice
        'tts_gender':   'MALE',
        'display':      'Afaan Oromo',
        'tts_backend':  'local_mms',    # ← uses facebook/mms-tts-orm
    },
}

# ── Google Cloud REST endpoints 
STT_URL       = 'https://speech.googleapis.com/v1/speech:recognize'
TTS_URL       = 'https://texttospeech.googleapis.com/v1/text:synthesize'
TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'


class SpeechService:

    def __init__(self,
                 stt_api_key: str = None,
                 tts_api_key: str = None,
                 translate_api_key: str = None):
        """
        Parameters
        ----------
        stt_api_key       : Google API key with Speech-to-Text enabled
        tts_api_key       : Google API key with Text-to-Speech enabled
        translate_api_key : Google API key with Translation enabled
                            (defaults to stt_api_key if not provided)
        """
        self.stt_key       = stt_api_key       or STT_API_KEY
        self.tts_key       = tts_api_key       or TTS_API_KEY
        self.translate_key = translate_api_key or TRANSLATE_API_KEY

        missing = []
        if not self.stt_key:
            missing.append('GOOGLE_STT_API_KEY')
        if not self.tts_key:
            missing.append('GOOGLE_TTS_API_KEY')
        if missing:
            raise ValueError(
                f'Missing API key(s): {", ".join(missing)}\n'
                f'Set them in your .env file or environment variables.'
            )

        # Oromo TTS is loaded lazily on first use via get_oromo_tts()
        # No import here — avoids crashing if torch isn't installed yet.
        self._oromo_tts = None

    # ── Speech-to-Text 

    def speech_to_text(self,
                       audio_bytes: bytes,
                       source_lang: str = 'en',
                       sample_rate: int = 48000) -> dict:
        """
        Convert audio bytes → text using the STT API key.

        Parameters
        ----------
        audio_bytes : bytes  — WebM/Opus audio from browser MediaRecorder
        source_lang : str    — 'en', 'am', or 'om'
        sample_rate : int    — browser default is 48000

        Returns
        -------
        dict: { text, confidence, lang, raw }
        """
        lang_cfg  = LANG_CONFIG.get(source_lang, LANG_CONFIG['en'])
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

        payload = {
            'config': {
                'encoding':                   'WEBM_OPUS',
                'sampleRateHertz':            sample_rate,
                'languageCode':               lang_cfg['bcp47'],
                'enableAutomaticPunctuation': True,
                'model':                      'latest_long',
                'alternativeLanguageCodes':   _alt_languages(source_lang),
            },
            'audio': {'content': audio_b64},
        }

        response = requests.post(
            STT_URL,
            params={'key': self.stt_key},
            json=payload,
            timeout=30,
        )
        _raise_for_status(response, service='STT')
        data = response.json()

        results = data.get('results', [])
        if not results:
            return {'text': '', 'confidence': 0.0, 'lang': source_lang, 'raw': data}

        best = results[0]['alternatives'][0]
        return {
            'text':       best.get('transcript', ''),
            'confidence': round(float(best.get('confidence', 0.0)), 3),
            'lang':       source_lang,
            'raw':        data,
        }

    # ── Text-to-Speech 

    def text_to_speech(self,
                       text: str,
                       lang: str = 'en',
                       speaking_rate: float = 0.9) -> bytes:
        """
        Convert text → MP3 audio bytes.

        Routes automatically:
          • 'en' / 'am' → Google Cloud TTS (cloud)
          • 'om'        → facebook/mms-tts-orm (local model)

        Parameters
        ----------
        text          : str   — text to speak
        lang          : str   — 'en', 'am', or 'om'
        speaking_rate : float — 0.25–4.0; used only for Google TTS

        Returns
        -------
        bytes — MP3 audio ready to stream or save
        """
        lang_cfg = LANG_CONFIG.get(lang, LANG_CONFIG['en'])

        if lang_cfg['tts_backend'] == 'local_mms':
            return self._text_to_speech_local(text, lang)

        return self._text_to_speech_google(text, lang_cfg, speaking_rate)

    def _text_to_speech_google(self,
                                text: str,
                                lang_cfg: dict,
                                speaking_rate: float) -> bytes:
        """Internal: Google Cloud TTS for English and Amharic."""
        payload = {
            'input': {'text': text},
            'voice': {
                'languageCode': lang_cfg['bcp47'],
                'name':         lang_cfg['tts_name'],
                'ssmlGender':   lang_cfg['tts_gender'],
            },
            'audioConfig': {
                'audioEncoding': 'MP3',
                'speakingRate':  speaking_rate,
                'pitch':         0.0,
            },
        }

        response = requests.post(
            TTS_URL,
            params={'key': self.tts_key},
            json=payload,
            timeout=30,
        )
        _raise_for_status(response, service='TTS')
        data = response.json()
        return base64.b64decode(data.get('audioContent', ''))

    def _text_to_speech_local(self, text: str, lang: str) -> bytes:
        """
        Internal: local MMS-TTS for Oromo.

        The model is loaded lazily and cached on the instance so it's only
        downloaded once per process, even across multiple requests.
        """
        if self._oromo_tts is None:
            # Import here so the rest of the service works even if torch is
            # missing — only Oromo TTS will fail, not STT or Amharic TTS.
            try:
                from oromo_tts import get_oromo_tts
                self._oromo_tts = get_oromo_tts()
            except ImportError as exc:
                raise RuntimeError(
                    "[TTS] Oromo TTS requires 'transformers', 'torch', and "
                    "'pydub' (+ ffmpeg).\n"
                    "Install with:  pip install transformers torch pydub\n"
                    f"Original error: {exc}"
                ) from exc

        logger.info("[TTS] Synthesising Oromo text via local MMS model (%d chars)", len(text))
        return self._oromo_tts.synthesize_to_mp3(text)

    # ── Translation ───────────────────────────────────────────────────────────

    def translate(self,
                  text: str,
                  target_lang: str,
                  source_lang: str = None) -> dict:
        """
        Translate text between English, Amharic, and Afaan Oromo.

        Parameters
        ----------
        text        : str — text to translate
        target_lang : str — 'en', 'am', or 'om'
        source_lang : str — if None, Google auto-detects

        Returns
        -------
        dict: { text, source_detected, target }
        """
        params = {
            'key':    self.translate_key,
            'q':      text,
            'target': _google_lang_code(target_lang),
            'format': 'text',
        }
        if source_lang:
            params['source'] = _google_lang_code(source_lang)

        response = requests.post(TRANSLATE_URL, params=params, timeout=15)
        _raise_for_status(response, service='Translation')
        data = response.json()

        translation  = data['data']['translations'][0]
        detected_src = translation.get('detectedSourceLanguage', source_lang or 'unknown')

        return {
            'text':             translation['translatedText'],
            'source_detected':  detected_src,
            'target':           target_lang,
        }
    # ── Full pipeline helpers 

    def doctor_to_patient(self,
                          audio_bytes: bytes,
                          doctor_lang: str = 'en',
                          patient_lang: str = 'en',
                          sample_rate: int = 48000) -> dict:
        """
        Doctor speaks → STT → translate (if needed) → text for deaf patient.

        Returns
        -------
        dict: { original_text, display_text, translated, stt_confidence }
        """
        stt = self.speech_to_text(audio_bytes,
                                  source_lang=doctor_lang,
                                  sample_rate=sample_rate)
        original_text = stt['text']

        if not original_text:
            return {
                'original_text':  '',
                'display_text':   '',
                'translated':     False,
                'stt_confidence': 0.0,
            }

        if doctor_lang == patient_lang:
            display_text = original_text
            translated   = False
        else:
            trans        = self.translate(original_text,
                                          target_lang=patient_lang,
                                          source_lang=doctor_lang)
            display_text = trans['text']
            translated   = True

        return {
            'original_text':  original_text,
            'display_text':   display_text,
            'translated':     translated,
            'stt_confidence': stt['confidence'],
        }

    def signs_to_doctor(self,
                        sign_text: str,
                        patient_lang: str = 'en',
                        doctor_lang: str = 'en') -> dict:
        """
        Deaf patient's recognised signs → translate (if needed) → TTS for doctor.

        Returns
        -------
        dict: { original_text, spoken_text, audio_mp3, translated }
        """
        if patient_lang == doctor_lang:
            spoken_text = sign_text
            translated  = False
        else:
            trans       = self.translate(sign_text,
                                         target_lang=doctor_lang,
                                         source_lang=patient_lang)
            spoken_text = trans['text']
            translated  = True

        audio_mp3 = self.text_to_speech(spoken_text, lang=doctor_lang)

        return {
            'original_text': sign_text,
            'spoken_text':   spoken_text,
            'audio_mp3':     audio_mp3,
            'translated':    translated,
        }


# ── Private helpers 

def _google_lang_code(lang: str) -> str:
    """Map internal code → Google Translate language code."""
    return {'en': 'en', 'am': 'am', 'om': 'om'}.get(lang, lang)


def _alt_languages(primary: str) -> list:
    """Alternative BCP-47 codes for STT code-switching support."""
    all_langs     = ['en-US', 'am-ET', 'om-ET']
    primary_bcp47 = LANG_CONFIG.get(primary, {}).get('bcp47', 'en-US')
    return [l for l in all_langs if l != primary_bcp47]


def _raise_for_status(response: requests.Response, service: str) -> None:
    """Raise with a clear message identifying which service and key failed."""
    if response.status_code == 400:
        raise ValueError(f'[{service}] Bad request — check audio format or language code.\n'
                         f'Response: {response.text}')
    if response.status_code == 403:
        raise PermissionError(
            f'[{service}] API key rejected (403).\n'
            f'Check that the {service} API is enabled in Google Cloud Console '
            f'for the {service} key.\n'
            f'Response: {response.text}'
        )
    response.raise_for_status()