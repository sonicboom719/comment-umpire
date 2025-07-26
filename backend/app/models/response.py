from pydantic import BaseModel
from typing import List, Optional
from .comment import Comment

class CommentsResponse(BaseModel):
    comments: List[Comment]
    next_page_token: Optional[str] = None
    total_count: Optional[int] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None