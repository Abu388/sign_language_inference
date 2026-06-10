#!/usr/bin/env python3
# live_inference.py
import cv2
import tempfile
import time
import logging
from pathlib import Path
from inference import SignLanguageInference
from config import HAND_MODEL_PATH, POSE_MODEL_PATH, MODEL_PATH, ENCODER_PATH, NORM_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveSignRecognizer:
    def __init__(self, confidence_threshold=0.7, cooldown_frames=30, debug_shapes=False):
        # Verify all required files exist
        required_files = [MODEL_PATH, ENCODER_PATH, NORM_PATH, HAND_MODEL_PATH, POSE_MODEL_PATH]
        for f in required_files:
            if not f.exists():
                raise FileNotFoundError(f"Missing required file: {f}")

        # Load inference engine with optional shape debugging
        self.infer = SignLanguageInference(debug_shapes=debug_shapes)
        self.conf_thresh = confidence_threshold
        self.cooldown_frames = cooldown_frames

        self.sentence_words = []
        self.last_prediction = None
        self.frames_since_last_pred = 0

        self.is_recording = False
        self.video_writer = None
        self.temp_video_path = None
        self.recording_frames = 0
        self.max_recording_frames = 300   # ~10s at 30fps

    def _start_recording(self, frame, fps=30.0):
        self.temp_video_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
        h, w = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(self.temp_video_path, fourcc, fps, (w, h))
        self.is_recording = True
        self.recording_frames = 0
        logger.info("Recording started... Press SPACE to stop.")

    def _stop_recording_and_predict(self):
        if not self.is_recording or self.video_writer is None:
            return None

        self.video_writer.release()
        self.is_recording = False
        logger.info("Recording stopped. Running inference...")

        try:
            predicted_word, confidence = self.infer.predict_video(self.temp_video_path)
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            # Print full traceback for debugging
            import traceback
            traceback.print_exc()
            self._cleanup_temp_video()
            return None

        self._cleanup_temp_video()

        if confidence >= self.conf_thresh:
            if (self.last_prediction != predicted_word or
                self.frames_since_last_pred >= self.cooldown_frames):
                self.sentence_words.append(predicted_word)
                self.last_prediction = predicted_word
                self.frames_since_last_pred = 0
                logger.info(f"PREDICTION: {predicted_word} (conf={confidence:.2f})")
            else:
                logger.info(f"Ignored duplicate: {predicted_word} (cooldown)")
        else:
            logger.info(f"Low confidence ({confidence:.2f}) – not added: {predicted_word}")

        return predicted_word, confidence

    def _cleanup_temp_video(self):
        if self.temp_video_path and Path(self.temp_video_path).exists():
            Path(self.temp_video_path).unlink()
            self.temp_video_path = None

    def _draw_overlay(self, frame, mode):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

        mode_text = "RECORDING" if mode == "recording" else "IDLE"
        color = (0, 0, 255) if mode == "recording" else (0, 255, 0)
        cv2.putText(frame, f"MODE: {mode_text}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if self.sentence_words:
            last_word = self.sentence_words[-1]
            cv2.putText(frame, f"Last sign: {last_word}", (10, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        sentence = " ".join(self.sentence_words)
        max_chars = 40
        if len(sentence) > max_chars:
            sentence = sentence[:max_chars-3] + "..."
        cv2.putText(frame, f"Sentence: {sentence}", (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

        cv2.putText(frame, "S: start | SPACE: stop & predict | ESC/Q: quit",
                    (10, h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        return frame

    def run(self, camera_id=0):
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            logger.error("Cannot open webcam.")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0

        logger.info("Live sign recognition started.")
        print("Controls: [S] start recording | [SPACE] stop & predict | [ESC/Q] quit")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if self.frames_since_last_pred < self.cooldown_frames:
                self.frames_since_last_pred += 1

            if self.is_recording and self.video_writer is not None:
                self.video_writer.write(frame)
                self.recording_frames += 1
                if self.recording_frames >= self.max_recording_frames:
                    logger.info("Max recording length reached. Auto-stopping.")
                    self._stop_recording_and_predict()

            display_frame = self._draw_overlay(frame.copy(),
                                               "recording" if self.is_recording else "idle")
            cv2.imshow("Sign Language Recognition - Live", display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s') and not self.is_recording:
                self._start_recording(frame, fps)
            elif key == ord(' ') and self.is_recording:
                self._stop_recording_and_predict()
            elif key == 27 or key == ord('q'):
                break

        if self.is_recording:
            self._stop_recording_and_predict()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Set debug_shapes=True to see tensor shapes at each step
    recognizer = LiveSignRecognizer(confidence_threshold=0.6,
                                    cooldown_frames=45,
                                    debug_shapes=True)   # ← enable to trace the 4D issue
    recognizer.run()