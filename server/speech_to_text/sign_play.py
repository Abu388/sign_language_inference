# import cv2
# import os

# video_map = {
#     "medicine":  "videoss/medicine/1.mp4",
#     "injection": "videoss/injection/1.mp4",
#     "pregnant":  "videoss/pregnant/1.mp4",

#     "head":      "videoss/head/1.mp4",
#     "eye":       "videoss/eye/1.mp4",
#     "ear":       "videoss/ear/1.mp4",
#     "nose":      "videoss/nose/1.mp4",
#     "throat":    "videoss/throat/1.mp4",
#     "chest":     "videoss/chest/1.mp4",

#     "help":      "videoss/help/1.mp4",
#     "emergency": "videoss/emergency/1.mp4",
#     "surgery":   "videoss/surgery/1.mp4",

#     "cough":     "videoss/cough/1.mp4",

#     "doctor":    "videoss/doctor/1.mp4",

#     "pain":      "videoss/pain/1.mp4",
#     "headache":  "videoss/headache/1.mp4",
#     "dizzy":     "videoss/dizzy/1.mp4",
#     "tired":     "videoss/tired/1.mp4",

#     "chest":    "videos/chest/1.mp4",
#     "cough":    "videos/cough/1.mp4",
#     "breath":   "videos/breathe/1.mp4",
#     "vomit":    "videos/vomit/1.mp4",
#     "medicine": "videos/medicine/1.mp4",
#     "hurt":     "videos/hurt/1.mp4",
#     "sick":     "videos/sick/1.mp4",
#     "fever":    "videos/fever/1.mp4",
# }


# def draw_text_with_background(frame, text, pos, font, scale, color, thickness, bg_color, padding=6):
#     """Draw text with a filled background rectangle for readability."""
#     (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
#     x, y = pos
#     cv2.rectangle(
#         frame,
#         (x - padding, y - th - padding),
#         (x + tw + padding, y + baseline + padding),
#         bg_color,
#         -1,
#     )
#     cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


# def play_video(video_path, label, full_text):
#     """Play a sign language video with subtitle-style overlay."""

#     if not os.path.exists(video_path):
#         print(f"[WARNING] Video not found: {video_path}")
#         return

#     cap = cv2.VideoCapture(video_path)
#     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

#     if not cap.isOpened():
#         print(f"[ERROR] Could not open: {video_path}")
#         return

#     fps = cap.get(cv2.CAP_PROP_FPS)
#     delay = max(1, int((1000 / fps) / 2)) if fps > 0 else 16

#     print(f"\n  Playing sign for: [{label.upper()}]")

#     font = cv2.FONT_HERSHEY_SIMPLEX

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Resize for consistent display
#         h, w = frame.shape[:2]
#         if w > 640:
#             ratio = 640 / w
#             frame = cv2.resize(frame, (640, int(h * ratio)), interpolation=cv2.INTER_LINEAR)
#             h, w = frame.shape[:2]

#         # ── TOP OVERLAY: Full doctor sentence ──────────────────────────────
#         overlay = frame.copy()
#         bar_h = 50
#         cv2.rectangle(overlay, (0, 0), (w, bar_h), (0, 0, 0), -1)
#         cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

#         # Truncate sentence if too long for the frame width
#         sentence = f"Doctor: {full_text}"
#         max_chars = int(w / 11)
#         if len(sentence) > max_chars:
#             sentence = sentence[: max_chars - 3] + "..."

#         cv2.putText(
#             frame,
#             sentence,
#             (10, 33),
#             font,
#             0.55,
#             (255, 255, 255),
#             1,
#             cv2.LINE_AA,
#         )

#         # ── BOTTOM OVERLAY: Current sign word (subtitle style) ──────────────
#         sign_text = f"Sign: {label.upper()}"
#         (tw, th), _ = cv2.getTextSize(sign_text, font, 0.9, 2)
#         x = max(0, (w - tw) // 2)
#         y = h - 20

#         draw_text_with_background(
#             frame,
#             sign_text,
#             (x, y),
#             font,
#             scale=0.9,
#             color=(0, 255, 100),
#             thickness=2,
#             bg_color=(0, 0, 0),
#             padding=8,
#         )

#         cv2.imshow("MediBridge - Text to Sign Language", frame)

#         if cv2.waitKey(delay) & 0xFF == ord("q"):
#             cap.release()
#             cv2.destroyAllWindows()
#             return

#     cap.release()


# def find_matches(text):
#     """Substring-based search, deduplicated, order preserved."""
#     text_lower = text.lower()
#     matches = [kw for kw in video_map if kw in text_lower]
#     return list(dict.fromkeys(matches))


# def main():
#     print("=" * 55)
#     print("         MEDIBRIDGE - TEXT TO SIGN LANGUAGE")
#     print("   Press Q during video to skip  |  'exit' to quit")
#     print("=" * 55)

#     while True:
#         try:
#             text = input("\nDoctor: ").strip()
#         except EOFError:
#             break

#         if not text:
#             continue

#         if text.lower() == "exit":
#             print("Exiting MediBridge. Goodbye!")
#             break

#         matches = find_matches(text)

#         if not matches:
#             print("[!] No matching signs found in that sentence.")
#             continue

#         print(f"[✓] Detected Signs: {matches}")

#         for keyword in matches:
#             play_video(video_map[keyword], keyword, text)

#         cv2.destroyAllWindows()


# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\n[!] Interrupted.")
#     finally:
#         cv2.destroyAllWindows()



"""
sign_player.py  —  MediBridge
==============================
Text-to-sign-language video player with optional voice input.

Modes
-----
  --typed   (default) Doctor types sentences; existing behaviour unchanged.
  --voice   Doctor speaks into the microphone; STT transcribes, then signs play.
  --lang    BCP-47 language for voice input: en (default), am, om

Usage
-----
  python sign_player.py                  # typed mode
  python sign_player.py --voice          # voice mode, English
  python sign_player.py --voice --lang am  # voice mode, Amharic

Requirements
------------
  pip install opencv-python sounddevice soundfile python-dotenv requests
  .env with GOOGLE_STT_API_KEY set
"""

import argparse
import os
import sys
import tempfile

import cv2
import numpy as np

# ── Video map ─────────────────────────────────────────────────────────────────
VIDEO_MAP = {
    "chest":    "videos/chest/1.mp4",
    "cough":    "videos/cough/1.mp4",
    "breath":   "videos/breathe/1.mp4",
    "pain":     "videos/pain/1.mp4",
    "vomit":    "videos/vomit/1.mp4",
    "ear":      "videos/ear/1.mp4",
    "head":     "videos/head/1.mp4",
    "eye":      "videos/eye/1.mp4",
    "medicine": "videos/medicine/1.mp4",
    "hurt":     "videos/hurt/1.mp4",
    "sick":     "videos/sick/1.mp4",
    "fever":    "videos/fever/1.mp4",
    "throat":   "videos/throat/1.mp4",
    "surgery":  "videos/surgery/1.mp4",
}

# ── Recording settings ────────────────────────────────────────────────────────
RECORD_SECONDS  = 5       # how long to record in voice mode
SAMPLE_RATE     = 16000   # Hz — Google STT works best at 16 kHz
CHANNELS        = 1


# ══════════════════════════════════════════════════════════════════════════════
# Audio capture
# ══════════════════════════════════════════════════════════════════════════════

def record_audio(duration: int = RECORD_SECONDS,
                 sample_rate: int = SAMPLE_RATE) -> bytes:
    """
    Record *duration* seconds from the default microphone.

    Returns raw LINEAR16 PCM bytes (16-bit, mono, 16 kHz) wrapped in a
    minimal WAV container so Google STT can accept it directly.
    """
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError:
        print("[ERROR] sounddevice / soundfile not installed.")
        print("        Run:  pip install sounddevice soundfile")
        sys.exit(1)

    print(f"\n  🎙  Recording for {duration}s … speak now")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=CHANNELS,
        dtype="int16",
    )
    sd.wait()
    print("  ✓  Recording complete")

    # Write to an in-memory WAV buffer
    import io
    buf = io.BytesIO()
    sf.write(buf, audio, sample_rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# STT — transcribe audio bytes → text
# ══════════════════════════════════════════════════════════════════════════════

def transcribe(audio_bytes: bytes, lang: str = "en") -> str:
    """
    Send audio bytes to Google STT and return the transcript string.
    Returns '' if no speech was detected.

    Parameters
    ----------
    audio_bytes : bytes — WAV/PCM audio (LINEAR16, 16 kHz, mono)
    lang        : str   — 'en', 'am', or 'om'
    """
    try:
        from speech_service import SpeechService
    except ImportError:
        print("[ERROR] speech_service.py not found in the same folder.")
        sys.exit(1)

    svc = SpeechService()

    # speech_to_text() expects WebM/Opus by default from the browser.
    # Here we send LINEAR16 WAV, so we call the Google STT REST API directly
    # using the same key — matching what the test file does for the round-trip.
    import base64
    import requests
    from dotenv import load_dotenv
    load_dotenv()

    STT_URL = "https://speech.googleapis.com/v1/speech:recognize"

    # Strip the WAV header — Google STT LINEAR16 config expects raw PCM,
    # but sending the full WAV container also works; Google ignores the header.
    payload = {
        "config": {
            "encoding":                   "LINEAR16",
            "sampleRateHertz":            SAMPLE_RATE,
            "languageCode":               _bcp47(lang),
            "enableAutomaticPunctuation": True,
            "model":                      "latest_long",
            "alternativeLanguageCodes":   _alt_bcp47(lang),
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
    except requests.HTTPError as e:
        print(f"[STT ERROR] {e}\n  Response: {resp.text[:300]}")
        return ""
    except requests.RequestException as e:
        print(f"[STT ERROR] Network error: {e}")
        return ""

    results = resp.json().get("results", [])
    if not results:
        print("  [!] No speech detected — try speaking louder or closer to the mic.")
        return ""

    transcript = results[0]["alternatives"][0].get("transcript", "")
    confidence = results[0]["alternatives"][0].get("confidence", 0.0)
    print(f"  📝  Transcript ({confidence:.0%} confidence): \"{transcript}\"")
    return transcript


def _bcp47(lang: str) -> str:
    return {"en": "en-US", "am": "am-ET", "om": "om-ET"}.get(lang, "en-US")

def _alt_bcp47(primary: str) -> list:
    all_codes = ["en-US", "am-ET", "om-ET"]
    return [c for c in all_codes if c != _bcp47(primary)]


# ══════════════════════════════════════════════════════════════════════════════
# Video playback — unchanged from original
# ══════════════════════════════════════════════════════════════════════════════

def draw_text_with_background(frame, text, pos, font, scale,
                               color, thickness, bg_color, padding=6):
    """Draw text with a filled background rectangle for readability."""
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    x, y = pos
    cv2.rectangle(
        frame,
        (x - padding, y - th - padding),
        (x + tw + padding, y + baseline + padding),
        bg_color,
        -1,
    )
    cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


def play_video(video_path: str, label: str, full_text: str) -> bool:
    """
    Play a sign language video with subtitle-style overlay.
    Returns False if the user pressed Q to quit entirely.
    """
    if not os.path.exists(video_path):
        print(f"  [WARNING] Video not found: {video_path}")
        return True

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print(f"  [ERROR] Could not open: {video_path}")
        return True

    fps   = cap.get(cv2.CAP_PROP_FPS)
    delay = max(1, int((1000 / fps) / 2)) if fps > 0 else 16

    print(f"  ▶  Playing sign for: [{label.upper()}]")

    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        if w > 640:
            ratio = 640 / w
            frame = cv2.resize(frame, (640, int(h * ratio)),
                               interpolation=cv2.INTER_LINEAR)
            h, w = frame.shape[:2]

        # ── Top bar: doctor sentence ──────────────────────────────────────
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 50), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        sentence  = f"Doctor: {full_text}"
        max_chars = int(w / 11)
        if len(sentence) > max_chars:
            sentence = sentence[:max_chars - 3] + "..."

        cv2.putText(frame, sentence, (10, 33), font, 0.55,
                    (255, 255, 255), 1, cv2.LINE_AA)

        # ── Bottom bar: current sign word ─────────────────────────────────
        sign_text   = f"Sign: {label.upper()}"
        (tw, th), _ = cv2.getTextSize(sign_text, font, 0.9, 2)
        x = max(0, (w - tw) // 2)
        y = h - 20

        draw_text_with_background(
            frame, sign_text, (x, y), font,
            scale=0.9, color=(0, 255, 100), thickness=2,
            bg_color=(0, 0, 0), padding=8,
        )

        cv2.imshow("MediBridge - Text to Sign Language", frame)

        key = cv2.waitKey(delay) & 0xFF
        if key == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            return False   # signal: user wants to quit entirely

    cap.release()
    return True


# ══════════════════════════════════════════════════════════════════════════════
# Matching
# ══════════════════════════════════════════════════════════════════════════════

def find_matches(text: str) -> list[str]:
    """Substring-based keyword search, deduplicated, order preserved."""
    text_lower = text.lower()
    return list(dict.fromkeys(kw for kw in VIDEO_MAP if kw in text_lower))


# ══════════════════════════════════════════════════════════════════════════════
# Main loop
# ══════════════════════════════════════════════════════════════════════════════

def run(voice_mode: bool = False, lang: str = "en") -> None:
    lang_label = {"en": "English", "am": "Amharic", "om": "Afaan Oromo"}.get(lang, lang)

    print("=" * 55)
    print("         MEDIBRIDGE — TEXT TO SIGN LANGUAGE")
    if voice_mode:
        print(f"   Mode: VOICE ({lang_label}) — {RECORD_SECONDS}s recording per turn")
    else:
        print("   Mode: TYPED")
    print("   Press Q during video to skip  |  'exit' to quit")
    print("=" * 55)

    while True:
        # ── Get input ─────────────────────────────────────────────────────
        if voice_mode:
            try:
                input(f"\n  Press ENTER to record ({RECORD_SECONDS}s) …")
            except EOFError:
                break

            audio_bytes = record_audio()
            text        = transcribe(audio_bytes, lang=lang)

            if not text:
                continue

        else:
            try:
                text = input("\nDoctor: ").strip()
            except EOFError:
                break

            if not text:
                continue
            if text.lower() == "exit":
                print("Exiting MediBridge. Goodbye!")
                break

        # ── Match and play ────────────────────────────────────────────────
        matches = find_matches(text)

        if not matches:
            print("  [!] No matching signs found in that sentence.")
            continue

        print(f"  [✓] Signs detected: {matches}")

        for keyword in matches:
            keep_going = play_video(VIDEO_MAP[keyword], keyword, text)
            if not keep_going:
                print("  [Q] Skipped remaining signs.")
                break

        cv2.destroyAllWindows()


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MediBridge — text/voice to sign language video player"
    )
    parser.add_argument(
        "--voice", action="store_true",
        help="Use microphone input instead of typing (requires sounddevice + STT key)"
    )
    parser.add_argument(
        "--lang", default="en", choices=["en", "am", "om"],
        help="Language for voice recognition: en (default), am (Amharic), om (Oromo)"
    )
    parser.add_argument(
        "--duration", type=int, default=RECORD_SECONDS,
        help=f"Recording duration in seconds (default: {RECORD_SECONDS})"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    # Allow --duration to override the module-level constant
    RECORD_SECONDS = args.duration

    try:
        run(voice_mode=args.voice, lang=args.lang)
    except KeyboardInterrupt:
        print("\n  [!] Interrupted.")
    finally:
        cv2.destroyAllWindows()