# config.py
import os
from pathlib import Path 

ROOT_DIR = Path(__file__).resolve().parent

MODEL_DIR = ROOT_DIR / "models"
MODEL_PATH = MODEL_DIR / "sign_model.pt"
ENCODER_PATH = MODEL_DIR / "label_encoder.pkl"
NORM_PATH = MODEL_DIR / "norm_stats.pkl"


MP_MODEL_DIR = ROOT_DIR / "mediapipe_models"
HAND_MODEL_PATH = MP_MODEL_DIR / "hand_landmarker.task"
POSE_MODEL_PATH = MP_MODEL_DIR / "pose_landmarker_lite.task"

SEQUENCE_LENGTH = 45
INPUT_DIM = 126
D_MODEL = 256
N_HEAD = 8
N_LAYERS = 4
DIM_FF = 1024
DROPOUT = 0.1

DEVICE = "cuda" if __import__("torch").cuda.is_available() else "cpu"