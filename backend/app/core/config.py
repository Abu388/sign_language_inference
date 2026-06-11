from pathlib import Path

# Project root: the directory containing 'backend/', 'models/', 'videos/', etc.
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Repository root (same as PROJECT_ROOT in your setup)
REPO_ROOT = PROJECT_ROOT

# Temporary upload directory (for video files)
TEMP_DIR = PROJECT_ROOT / "temp_uploads"
TEMP_DIR.mkdir(exist_ok=True)

# Video file settings
MAX_VIDEO_SIZE_MB = 10
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

# ML inference threshold
DEFAULT_CONFIDENCE_THRESHOLD = 0.6