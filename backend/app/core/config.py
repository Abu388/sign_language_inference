from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
TEMP_DIR = PROJECT_ROOT / "temp_uploads"
TEMP_DIR.mkdir(exist_ok=True)

MAX_VIDEO_SIZE_MB = 10
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}  # added .webm
DEFAULT_CONFIDENCE_THRESHOLD = 0.6