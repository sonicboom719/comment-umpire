from fastapi import APIRouter, HTTPException, Depends
from typing import List
import os

from app.models.comment import Comment, AnalysisRequest, AnalysisResult
from app.models.response import ErrorResponse
from app.services.youtube_service import YouTubeService
from app.services.analysis_service import AnalysisService

router = APIRouter()

def get_youtube_service():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="YouTube API キーが設定されていません")
    return YouTubeService(api_key)

def get_analysis_service():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API キーが設定されていません")
    return AnalysisService(api_key)

@router.get("/{comment_id}/replies", response_model=List[Comment])
async def get_comment_replies(
    comment_id: str,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """コメントの返信を取得"""
    try:
        replies = youtube_service.get_replies(comment_id)
        return replies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予期しないエラー: {str(e)}")

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_comment(
    request: AnalysisRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """コメントをAI分析"""
    try:
        print(f"Analyzing comment: {request.comment_text[:50]}...")
        result = await analysis_service.analyze_comment(request)
        print(f"Analysis completed successfully")
        return result
    except ValueError as e:
        print(f"ValueError in analyze_comment: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in analyze_comment: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"予期しないエラー: {str(e)}")