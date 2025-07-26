import re
from datetime import datetime
from typing import List, Tuple, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.models.comment import Comment, VideoInfo

class YouTubeService:
    def __init__(self, api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def extract_video_id(self, url: str) -> str:
        """YouTube URLから動画IDを抽出"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("有効なYouTube URLではありません")
    
    def get_video_info(self, video_id: str) -> VideoInfo:
        """動画情報を取得"""
        try:
            request = self.youtube.videos().list(
                part="snippet",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                raise ValueError("動画が見つかりません")
            
            item = response['items'][0]
            snippet = item['snippet']
            
            return VideoInfo(
                video_id=video_id,
                title=snippet['title'],
                channel_name=snippet['channelTitle'],
                thumbnail_url=snippet['thumbnails']['medium']['url'],
                published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
            )
        
        except HttpError as e:
            raise ValueError(f"YouTube API エラー: {e}")
    
    def get_comments(self, video_id: str, page_token: Optional[str] = None, max_results: int = 100) -> Tuple[List[Comment], Optional[str]]:
        """動画のコメントを返信も含めて取得"""
        try:
            # まずコメントスレッドを取得
            request = self.youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=50,  # 返信を含めるため、親コメントは50件に制限
                order="time",
                pageToken=page_token
            )
            response = request.execute()
            
            comments = []
            
            for item in response['items']:
                # 親コメントを追加
                snippet = item['snippet']['topLevelComment']['snippet']
                parent_comment = Comment(
                    id=item['snippet']['topLevelComment']['id'],
                    text=snippet['textDisplay'],
                    author=snippet['authorDisplayName'],
                    published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                    like_count=snippet.get('likeCount', 0),
                    reply_count=item['snippet'].get('totalReplyCount', 0)
                )
                comments.append(parent_comment)
                
                # 返信が存在する場合は取得
                if 'replies' in item and item['replies']['comments']:
                    for reply_item in item['replies']['comments']:
                        reply_snippet = reply_item['snippet']
                        reply = Comment(
                            id=reply_item['id'],
                            text=reply_snippet['textDisplay'],
                            author=reply_snippet['authorDisplayName'],
                            published_at=datetime.fromisoformat(reply_snippet['publishedAt'].replace('Z', '+00:00')),
                            like_count=reply_snippet.get('likeCount', 0),
                            reply_count=0,
                            parent_id=parent_comment.id
                        )
                        comments.append(reply)
                
                # 100件に達したら終了
                if len(comments) >= max_results:
                    comments = comments[:max_results]
                    break
            
            next_page_token = response.get('nextPageToken')
            return comments, next_page_token
        
        except HttpError as e:
            raise ValueError(f"YouTube API エラー: {e}")
    
    def get_replies(self, comment_id: str) -> List[Comment]:
        """コメントの返信を取得"""
        try:
            request = self.youtube.comments().list(
                part="snippet",
                parentId=comment_id,
                maxResults=100
            )
            response = request.execute()
            
            replies = []
            for item in response['items']:
                snippet = item['snippet']
                reply = Comment(
                    id=item['id'],
                    text=snippet['textDisplay'],
                    author=snippet['authorDisplayName'],
                    published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                    like_count=snippet.get('likeCount', 0),
                    reply_count=0,
                    parent_id=comment_id
                )
                replies.append(reply)
            
            return replies
        
        except HttpError as e:
            raise ValueError(f"YouTube API エラー: {e}")