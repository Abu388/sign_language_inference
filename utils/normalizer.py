# utils/normalizer.py
import pickle
import numpy as np
import logging
from config import NORM_PATH

logger = logging.getLogger(__name__)

class KeypointNormalizer:
    def __init__(self):
        with open(NORM_PATH, "rb") as f:
            stats = pickle.load(f)
        self.mean = stats["mean"]
        self.std = stats["std"]
        logger.info(f"Loaded norm stats: mean shape {self.mean.shape}, std shape {self.std.shape}")

    def __call__(self, keypoints: np.ndarray) -> np.ndarray:
        # keypoints shape: (T, 126)
        original_shape = keypoints.shape
        result = (keypoints - self.mean) / self.std
        logger.debug(f"Normalizer: input {original_shape} -> output {result.shape}")
        return result