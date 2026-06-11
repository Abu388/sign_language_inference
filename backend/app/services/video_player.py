"""
Text‑to‑Sign‑Language video player service.
Matches keywords in a sentence and plays corresponding sign videos.
"""
import os
import re
import logging
import cv2
from typing import List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Repository root (where the `videos/` folder lives)
REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

def _video_path(rel: str) -> str:
    """Resolve video path relative to repo root."""
    return str(REPO_ROOT / rel)


# Cleaned video map (no duplicates, paths resolved once)
VIDEO_MAP = {
    "back":       _video_path("videos/back/1.mp4"),
    "breath":     _video_path("videos/breath/1.mp4"),
    "chest":      _video_path("videos/chest/1.mp4"),
    "cough":      _video_path("videos/cough/1.mp4"),
    "dizzy":      _video_path("videos/dizzy/1.mp4"),
    "doctor":     _video_path("videos/doctor/1.mp4"),
    "ear":        _video_path("videos/ear/1.mp4"),
    "emergency":  _video_path("videos/emergency/1.mp4"),
    "eye":        _video_path("videos/eye/1.mp4"),
    "fever":      _video_path("videos/fever/1.mp4"),
    "head":       _video_path("videos/head/1.mp4"),
    "headache":   _video_path("videos/headache/1.mp4"),
    "hello":      _video_path("videos/hello/1.mp4"),
    "help":       _video_path("videos/help/1.mp4"),
    "hurt":       _video_path("videos/hurt/1.mp4"),
    "injection":  _video_path("videos/injection/1.mp4"),
    "medicine":   _video_path("videos/medicine/1.mp4"),
    "nose":       _video_path("videos/nose/1.mp4"),
    "pain":       _video_path("videos/pain/1.mp4"),
    "pregnant":   _video_path("videos/pregnant/1.mp4"),
    "relax":      _video_path("videos/relax/1.mp4"),
    "sick":       _video_path("videos/sick/1.mp4"),
    "surgery":    _video_path("videos/surgery/1.mp4"),
    "thank_you":  _video_path("videos/thank_you/1.mp4"),
    "throat":     _video_path("videos/throat/1.mp4"),
    "tired":      _video_path("videos/tired/1.mp4"),
    "vomit":      _video_path("videos/vomit/1.mp4"),
}

DEFAULT_DISPLAY_WIDTH = 360
DEFAULT_PLAYBACK_SPEED = 3.0  # 3× faster than real time


class VideoPlayer:
    """Play sign language videos based on keyword matches from text."""

    def __init__(self, video_map: dict = None,
                 display_width: int = DEFAULT_DISPLAY_WIDTH,
                 playback_speed: float = DEFAULT_PLAYBACK_SPEED):
        """
        Args:
            video_map: dict mapping keyword -> video path (default VIDEO_MAP)
            display_width: output window width in pixels (height scales)
            playback_speed: multiplier for video speed (1.0 = normal)
        """
        self.video_map = video_map or VIDEO_MAP
        self.display_width = display_width
        self.playback_speed = playback_speed
        self.window_name = "MediBridge - Text to Sign Language"

    def find_matches(self, text: str) -> List[str]:
        """
        Extract keywords from text using whole-word matching.
        Order is preserved as in VIDEO_MAP (first occurrence order).
        """
        text_lower = text.lower()
        matches = []
        for kw in self.video_map:
            if re.search(rf'\b{re.escape(kw)}\b', text_lower):
                matches.append(kw)
        return matches

    def _draw_text_with_background(self, frame, text, pos, font, scale,
                                   color, thickness, bg_color, padding=6):
        """Draw text with a filled background rectangle."""
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

    def _scale_frame(self, frame, target_size: list):
        """Downscale frame proportionally."""
        h, w = frame.shape[:2]
        if w <= self.display_width:
            return frame, w, h
        if target_size[0] is None:
            ratio = self.display_width / w
            target_size[0] = (self.display_width, int(h * ratio))
        scaled = cv2.resize(frame, target_size[0], interpolation=cv2.INTER_AREA)
        tw, th = target_size[0]
        return scaled, tw, th

    def _draw_frame(self, frame, label: str, full_text: str, font):
        """Apply subtitle overlays to a frame (in‑place)."""
        h, w = frame.shape[:2]
        bar_h = max(36, int(50 * w / 640))

        # Top black bar with doctor's sentence
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, bar_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        sentence = f"Doctor: {full_text}"
        max_chars = int(w / 11)
        if len(sentence) > max_chars:
            sentence = sentence[:max_chars - 3] + "..."
        cv2.putText(frame, sentence, (8, bar_h - 14), font, 0.5,
                    (255, 255, 255), 1, cv2.LINE_AA)

        # Bottom subtitle: current sign word
        sign_text = f"Sign: {label.upper()}"
        sign_scale = max(0.7, 0.9 * w / 640)
        (tw, _), _ = cv2.getTextSize(sign_text, font, sign_scale, 2)
        self._draw_text_with_background(
            frame, sign_text,
            (max(0, (w - tw) // 2), h - 16),
            font, scale=sign_scale, color=(0, 255, 100), thickness=2,
            bg_color=(0, 0, 0), padding=6,
        )

    def play(self, keywords: List[str], full_text: str) -> bool:
        """
        Play a sequence of sign videos for the matched keywords.
        Returns False if user pressed Q to quit, True otherwise.
        """
        if not keywords:
            return True

        # Pre‑open all video captures to minimise gaps
        queue: List[Tuple[str, cv2.VideoCapture, int]] = []
        for kw in keywords:
            path = self.video_map.get(kw)
            if not path or not os.path.exists(path):
                logger.warning("Video not found for keyword '%s': %s", kw, path)
                continue
            cap = cv2.VideoCapture(path)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if not cap.isOpened():
                logger.error("Could not open video: %s", path)
                continue
            fps = cap.get(cv2.CAP_PROP_FPS)
            delay = max(1, int((1000 / fps) / self.playback_speed)) if fps > 0 else 16
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

                frame, _, _ = self._scale_frame(frame, target_size)
                self._draw_frame(frame, kw, full_text, font)
                cv2.imshow(self.window_name, frame)

                if cv2.waitKey(delay) & 0xFF == ord('q'):
                    for _, c, _ in queue:
                        c.release()
                    cv2.destroyAllWindows()
                    return False

            cap.release()

        return True

    def run_cli(self, voice_mode: bool = False, lang: str = "en"):
        """
        Interactive command‑line loop (typed or voice) using this player.
        voice_mode requires AudioSTTService.
        """
        if voice_mode:
            try:
                from .audio_stt import AudioSTTService
                stt = AudioSTTService()
            except ImportError as e:
                print(f"Cannot start voice mode: {e}")
                return

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
                audio_bytes = stt.record_audio()
                if not audio_bytes:
                    continue
                text = stt.transcribe(audio_bytes, lang=lang)
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

            matches = self.find_matches(text)
            if not matches:
                print("  [!] No matching signs found in that sentence.")
                continue
            print(f"  [✓] Signs detected: {matches}")

            if not self.play(matches, text):
                break
            cv2.destroyAllWindows()