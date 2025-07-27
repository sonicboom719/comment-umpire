from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Comment(BaseModel):
    id: str
    text: str
    author: str
    published_at: datetime
    like_count: int
    reply_count: int
    parent_id: Optional[str] = None

class VideoInfo(BaseModel):
    video_id: str
    title: str
    channel_name: str
    thumbnail_url: str
    published_at: datetime

class AnalysisRequest(BaseModel):
    comment_text: str
    context_comments: Optional[List[Comment]] = None

class AnalysisResult(BaseModel):
    category: List[str]
    is_counter: bool
    graham_hierarchy: Optional[str]
    logical_fallacy: Optional[str]
    validity_assessment: str
    safe_or_out: str
    explanation: str
    validity_reason: str