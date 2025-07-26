from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os

from app.models.comment import VideoInfo
from app.models.response import CommentsResponse, ErrorResponse
from app.services.youtube_service import YouTubeService

router = APIRouter()

class VideoExtractRequest(BaseModel):
    url: str

def get_youtube_service():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="YouTube API キーが設定されていません")
    return YouTubeService(api_key)

@router.post("/extract", response_model=VideoInfo)
async def extract_video_info(
    request: VideoExtractRequest,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """YouTube URLから動画情報を抽出"""
    try:
        video_id = youtube_service.extract_video_id(request.url)
        video_info = youtube_service.get_video_info(video_id)
        return video_info
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予期しないエラー: {str(e)}")

@router.get("/{video_id}/comments", response_model=CommentsResponse)
async def get_video_comments(
    video_id: str,
    page_token: str = None,
    max_results: int = 100,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """動画のコメントを取得"""
    try:
        comments, next_page_token = youtube_service.get_comments(
            video_id, page_token, max_results
        )
        return CommentsResponse(
            comments=comments,
            next_page_token=next_page_token,
            total_count=len(comments)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予期しないエラー: {str(e)}")