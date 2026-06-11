import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..services.video_player import VideoPlayer
from ..core.config import REPO_ROOT   # we'll add this to config

router = APIRouter()
logger = logging.getLogger(__name__)

# Instantiate the video player (can be configured)
video_player = VideoPlayer()  # uses default display_width, playback_speed

class TextToVideoRequest(BaseModel):
    text: str

class TextToVideoResponse(BaseModel):
    matched_keywords: List[str]
    video_urls: List[str]   # relative URLs like "/videos/chest/1.mp4"

@router.post("/text-to-video", response_model=TextToVideoResponse)
async def text_to_video(req: TextToVideoRequest):
    """
    Given a sentence, return the list of matched keywords and the corresponding
    video file URLs that the frontend can play.
    """
    matches = video_player.find_matches(req.text)
    if not matches:
        return TextToVideoResponse(matched_keywords=[], video_urls=[])
    # Build video URLs – assuming the frontend can access /videos/... via static serving
    video_urls = []
    for kw in matches:
        rel_path = video_player.video_map.get(kw, "")
        if rel_path:
            # Convert absolute path to URL path (e.g., /videos/chest/1.mp4)
            # Assume the videos folder is served statically at the root
            # We'll strip the repo root part and keep the relative part starting with "videos/"
            try:
                relative = rel_path.split("videos/")[-1]
                url = f"/videos/{relative}"
                video_urls.append(url)
            except:
                video_urls.append("")
    return TextToVideoResponse(matched_keywords=matches, video_urls=video_urls)