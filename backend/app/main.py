from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from .routers import predict, refinement, speech, audio, text_to_video   # add new ones

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sign Language Recognition API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static videos folder (if exists)
REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
videos_path = REPO_ROOT / "videos"
if videos_path.exists():
    app.mount("/videos", StaticFiles(directory=str(videos_path)), name="videos")
    logger.info(f"Serving videos from {videos_path}")
else:
    logger.warning(f"Videos folder not found at {videos_path}")

# Include routers
app.include_router(refinement.router)   # keep your existing
app.include_router(predict.router, prefix="/api", tags=["prediction"])
app.include_router(speech.router, prefix="/api", tags=["speech"])
app.include_router(audio.router, prefix="/api", tags=["audio"])
app.include_router(text_to_video.router, prefix="/api", tags=["text-to-video"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": True}