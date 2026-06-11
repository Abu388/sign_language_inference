import os
import logging
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from ..services.video_player import VideoPlayer, REPO_ROOT

router = APIRouter()
logger = logging.getLogger(__name__)

video_player = VideoPlayer()
VIDEOS_DIR = Path(REPO_ROOT) / "videos"

class TextToVideoRequest(BaseModel):
    text: str

class TextToVideoResponse(BaseModel):
    matched_keywords: List[str]
    video_urls: List[str]

@router.post("/text-to-video", response_model=TextToVideoResponse)
async def text_to_video(req: TextToVideoRequest):
    """
    Given a sentence, return matched keywords and their video URLs.
    """
    matches = video_player.find_matches(req.text)
    if not matches:
        return TextToVideoResponse(matched_keywords=[], video_urls=[])

    video_urls = []
    for kw in matches:
        abs_path = video_player.video_map.get(kw, "")
        if not abs_path or not os.path.exists(abs_path):
            continue
        rel = os.path.relpath(abs_path, str(VIDEOS_DIR))
        url = f"/videos/{rel}"
        video_urls.append(url)

    return TextToVideoResponse(matched_keywords=matches, video_urls=video_urls)