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




import argparse
import os
import re
import sys
import tempfile

import cv2
import numpy as np

# ── Video map (paths resolved from repo root, not cwd) ───────────────────────
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _video(rel: str) -> str:
    return os.path.join(REPO_ROOT, rel)


VIDEO_MAP = {
    "back":       _video("videos/back/1.mp4"),
    "breath":     _video("videos/breath/1.mp4"),
    "chest":      _video("videos/chest/1.mp4"),
    "cough":      _video("videos/cough/1.mp4"),
    "dizzy":      _video("videos/dizzy/1.mp4"),
    "doctor":     _video("videos/doctor/1.mp4"),
    "ear":        _video("videos/ear/1.mp4"),
    "emergency":  _video("videos/emergency/1.mp4"),
    "eye":        _video("videos/eye/1.mp4"),
    "fever":      _video("videos/fever/1.mp4"),
    "head":       _video("videos/head/1.mp4"),
    "headache":   _video("videos/headache/1.mp4"),
    "hello":      _video("videos/hello/1.mp4"),
    "help":       _video("videos/help/1.mp4"),
    "hurt":       _video("videos/hurt/1.mp4"),
    "injection":  _video("videos/injection/1.mp4"),
    "medicine":   _video("videos/medicine/1.mp4"),
    "pain":       _video("videos/pain/1.mp4"),
    "pregnant":   _video("videos/pregnant/1.mp4"),
    "relax":      _video("videos/relax/1.mp4"),
    "sick":       _video("videos/sick/1.mp4"),
    "surgery":    _video("videos/surgery/1.mp4"),
    "thank_you":  _video("videos/thank_you/1.mp4"),
    "throat":     _video("videos/throat/1.mp4"),
    "tired":      _video("videos/tired/1.mp4"),
    "vomit":      _video("videos/vomit/1.mp4"),
}

# ── Recording / display settings ──────────────────────────────────────────────
SAMPLE_RATE     = 16000   # Hz — Google STT works best at 16 kHz
CHANNELS        = 1
DISPLAY_WIDTH    = 360     # display width; height scales proportionally (~360×640)
PLAYBACK_SPEED   = 3.0     # 3× faster than real time (was 2×)

_stt_service = None


# Audio capture

def record_audio(sample_rate: int = SAMPLE_RATE) -> bytes | None:
    """
    Record from the default microphone until the user presses Enter.

    Returns LINEAR16 PCM bytes (16-bit, mono, 16 kHz) in a WAV container,
    or None if no audio was captured.
    """
    import io
    import threading

    try:
        import numpy as np
        import sounddevice as sd
        import soundfile as sf
    except ImportError:
        print("[ERROR] sounddevice / soundfile not installed.")
        print("        Run:  pip install sounddevice soundfile numpy")
        sys.exit(1)

    print("\n  Press ENTER to start recording …")
    try:
        input()
    except EOFError:
        return None

    frames: list = []
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


# STT — transcribe audio bytes → text

def transcribe(audio_bytes: bytes, lang: str = "en") -> str:
    """
    Send audio bytes to Google STT and return the transcript string.
    Returns '' if no speech was detected.

    Parameters
    ----------
    audio_bytes : bytes — WAV/PCM audio (LINEAR16, 16 kHz, mono)
    lang        : str   — 'en', 'am', or 'om'
    """
    global _stt_service
    try:
        from speech_service import SpeechService
    except ImportError:
        print("[ERROR] speech_service.py not found in the same folder.")
        sys.exit(1)

    if _stt_service is None:
        _stt_service = SpeechService()
    svc = _stt_service

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


# Video playback

WINDOW_NAME = "MediBridge - Text to Sign Language"


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


def _scale_frame(frame, target_size: list, display_width: int) -> tuple:
    """Downscale frame proportionally; INTER_AREA preserves detail when shrinking."""
    h, w = frame.shape[:2]
    if w <= display_width:
        return frame, w, h
    if target_size[0] is None:
        ratio = display_width / w
        target_size[0] = (display_width, int(h * ratio))
    scaled = cv2.resize(frame, target_size[0], interpolation=cv2.INTER_AREA)
    tw, th = target_size[0]
    return scaled, tw, th


def _draw_frame(frame, label: str, full_text: str, font) -> None:
    """Apply subtitle overlays to a single frame (in-place)."""
    h, w = frame.shape[:2]
    bar_h = max(36, int(50 * w / 640))

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, bar_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    sentence = f"Doctor: {full_text}"
    max_chars = int(w / 11)
    if len(sentence) > max_chars:
        sentence = sentence[:max_chars - 3] + "..."

    cv2.putText(frame, sentence, (8, bar_h - 14), font, 0.5,
                (255, 255, 255), 1, cv2.LINE_AA)

    sign_text = f"Sign: {label.upper()}"
    sign_scale = max(0.7, 0.9 * w / 640)
    (tw, _), _ = cv2.getTextSize(sign_text, font, sign_scale, 2)
    draw_text_with_background(
        frame, sign_text, (max(0, (w - tw) // 2), h - 16), font,
        scale=sign_scale, color=(0, 255, 100), thickness=2,
        bg_color=(0, 0, 0), padding=6,
    )


def play_signs(keywords: list[str], full_text: str,
               display_width: int = DISPLAY_WIDTH,
               playback_speed: float = PLAYBACK_SPEED) -> bool:
    """
    Play a sequence of sign videos with minimal gap between them.
    All videos are opened upfront so transitions are near-instant.
    Returns False if the user pressed Q to quit.
    """
    # Pre-open every matched video before playback starts
    queue: list[tuple[str, cv2.VideoCapture, int]] = []
    for kw in keywords:
        path = VIDEO_MAP[kw]
        if not os.path.exists(path):
            print(f"  [WARNING] Video not found: {path}")
            continue
        cap = cv2.VideoCapture(path)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not cap.isOpened():
            print(f"  [ERROR] Could not open: {path}")
            continue
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = max(1, int((1000 / fps) / playback_speed)) if fps > 0 else 16
        queue.append((kw, cap, delay))

    if not queue:
        return True

    font = cv2.FONT_HERSHEY_SIMPLEX

    for kw, cap, delay in queue:
        print(f"\n  Playing sign for: [{kw.upper()}]")
        target_size = [None]

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame, _, _ = _scale_frame(frame, target_size, display_width)
            _draw_frame(frame, kw, full_text, font)
            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(delay) & 0xFF == ord("q"):
                for _, c, _ in queue:
                    c.release()
                cv2.destroyAllWindows()
                return False

        cap.release()

    return True


# Matching


def find_matches(text: str) -> list[str]:
    """Whole-word keyword search, VIDEO_MAP order preserved."""
    text_lower = text.lower()
    return [
        kw for kw in VIDEO_MAP
        if re.search(rf'\b{re.escape(kw)}\b', text_lower)
    ]


# Main loop


def run(voice_mode: bool = False, lang: str = "en",
        display_width: int = DISPLAY_WIDTH,
        playback_speed: float = PLAYBACK_SPEED) -> None:
    lang_label = {"en": "English", "am": "Amharic", "om": "Afaan Oromo"}.get(lang, lang)

    print("=" * 55)
    print("         MEDIBRIDGE — TEXT TO SIGN LANGUAGE")
    if voice_mode:
        print(f"   Mode: VOICE ({lang_label}) — ENTER to start/stop recording")
    else:
        print("   Mode: TYPED")
    print("   Press Q during video to skip  |  'exit' to quit")
    print("=" * 55)

    while True:
        if voice_mode:
            audio_bytes = record_audio()
            if not audio_bytes:
                continue

            text = transcribe(audio_bytes, lang=lang)
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

        # ── Match and play 
        matches = find_matches(text)

        if not matches:
            print("  [!] No matching signs found in that sentence.")
            continue

        print(f"  [✓] Signs detected: {matches}")

        if not play_signs(matches, text,
                          display_width=display_width,
                          playback_speed=playback_speed):
            break

        cv2.destroyAllWindows()


# Entry point
# ════════════════════════════════════════════════════════════════════════════

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
        "--width", type=int, default=DISPLAY_WIDTH,
        help=f"Display width in pixels, height scales proportionally (default: {DISPLAY_WIDTH})"
    )
    parser.add_argument(
        "--speed", type=float, default=PLAYBACK_SPEED,
        help=f"Playback speed multiplier (default: {PLAYBACK_SPEED})"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    try:
        run(voice_mode=args.voice, lang=args.lang,
            display_width=args.width, playback_speed=args.speed)
    except KeyboardInterrupt:
        print("\n  [!] Interrupted.")
    finally:
        cv2.destroyAllWindows()