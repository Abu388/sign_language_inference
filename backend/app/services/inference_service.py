import sys
from pathlib import Path

# Add project root to sys.path BEFORE importing inference
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import logging
from inference import SignLanguageInference

logger = logging.getLogger(__name__)

class InferenceService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Loading SignLanguageInference model (singleton)...")
            cls._instance = super().__new__(cls)
            cls._instance.model = SignLanguageInference(debug_shapes=False)
        return cls._instance

    def predict(self, video_path: Path) -> tuple[str, float]:
        word, conf = self.model.predict_video(str(video_path))
        return word, conf