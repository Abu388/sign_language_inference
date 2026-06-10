# utils/keypoint_extractor.py
import math
import threading
import logging
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from config import HAND_MODEL_PATH, POSE_MODEL_PATH, SEQUENCE_LENGTH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_thread_local = threading.local()

def _get_detectors():
    """Create or return thread‑local MediaPipe detectors."""
    if hasattr(_thread_local, "hand_detector"):
        return _thread_local.hand_detector, _thread_local.pose_detector

    # Verify model files exist
    if not HAND_MODEL_PATH.exists():
        raise FileNotFoundError(f"Hand landmarker model not found: {HAND_MODEL_PATH}")
    if not POSE_MODEL_PATH.exists():
        raise FileNotFoundError(f"Pose landmarker model not found: {POSE_MODEL_PATH}")

    # Try GPU first, fallback to CPU
    for use_gpu in (True, False):
        try:
            delegate = mp_python.BaseOptions.Delegate.GPU if use_gpu else mp_python.BaseOptions.Delegate.CPU
            hand_opts = vision.HandLandmarkerOptions(
                base_options=mp_python.BaseOptions(
                    model_asset_path=str(HAND_MODEL_PATH),
                    delegate=delegate
                ),
                num_hands=2,
                min_hand_presence_confidence=0.5,
            )
            pose_opts = vision.PoseLandmarkerOptions(
                base_options=mp_python.BaseOptions(
                    model_asset_path=str(POSE_MODEL_PATH),
                    delegate=delegate
                ),
                min_pose_presence_confidence=0.5,
            )
            _thread_local.hand_detector = vision.HandLandmarker.create_from_options(hand_opts)
            _thread_local.pose_detector = vision.PoseLandmarker.create_from_options(pose_opts)
            logger.info(f"MediaPipe detectors created using {'GPU' if use_gpu else 'CPU'} delegate")
            break
        except Exception as e:
            logger.warning(f"Failed to create detectors with {'GPU' if use_gpu else 'CPU'}: {e}")
            continue
    else:
        # If both attempts fail
        raise RuntimeError("Could not initialize MediaPipe detectors (both GPU and CPU failed).")

    return _thread_local.hand_detector, _thread_local.pose_detector


def extract_keypoints_from_video(video_path: str) -> np.ndarray:
    """
    Extract a fixed‑length sequence of keypoints from a video file.
    Returns array of shape (SEQUENCE_LENGTH, 126) or None if fails.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames < 10:
        cap.release()
        logger.warning(f"Video too short: {total_frames} frames")
        return None

    # Seek to middle window (or read all if short)
    if total_frames > SEQUENCE_LENGTH:
        start_frame = (total_frames - SEQUENCE_LENGTH) // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        frames_to_read = SEQUENCE_LENGTH
    else:
        frames_to_read = total_frames

    try:
        hand_det, pose_det = _get_detectors()
    except Exception as e:
        cap.release()
        logger.error(f"Detector creation failed: {e}")
        raise   # Re-raise to be caught by caller

    keypoints_list = []
    last_anchor = (0.5, 0.5, 0.0)
    last_scale = 0.2

    for _ in range(frames_to_read):
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        hand_result = hand_det.detect(mp_image)
        pose_result = pose_det.detect(mp_image)

        anchor, scale = last_anchor, last_scale
        if pose_result.pose_landmarks and len(pose_result.pose_landmarks[0]) > 12:
            lm = pose_result.pose_landmarks[0]
            left = lm[11]
            right = lm[12]
            anchor = (
                (left.x + right.x) / 2,
                (left.y + right.y) / 2,
                (left.z + right.z) / 2,
            )
            dx = left.x - right.x
            dy = left.y - right.y
            dz = left.z - right.z
            scale = math.sqrt(dx*dx + dy*dy + dz*dz) if (dx*dx+dy*dy+dz*dz) > 0 else last_scale

        lh = np.zeros(63, dtype=np.float32)
        rh = np.zeros(63, dtype=np.float32)
        if hand_result.hand_landmarks:
            for hand_lms, handedness in zip(hand_result.hand_landmarks, hand_result.handedness):
                coords = []
                for lm in hand_lms:
                    coords.extend([
                        (lm.x - anchor[0]) / scale,
                        (lm.y - anchor[1]) / scale,
                        (lm.z - anchor[2]) / scale
                    ])
                arr = np.array(coords, dtype=np.float32)
                if handedness[0].category_name.lower() == "left":
                    lh = arr
                else:
                    rh = arr

        keypoints_list.append(np.concatenate([lh, rh]))
        last_anchor, last_scale = anchor, scale

    cap.release()

    if len(keypoints_list) < 10:
        return None

    seq = np.array(keypoints_list, dtype=np.float32)
    # Pad or truncate to SEQUENCE_LENGTH
    if len(seq) < SEQUENCE_LENGTH:
        pad = np.tile(seq[-1], (SEQUENCE_LENGTH - len(seq), 1))
        seq = np.vstack([seq, pad])
    elif len(seq) > SEQUENCE_LENGTH:
        seq = seq[:SEQUENCE_LENGTH]

    return seq