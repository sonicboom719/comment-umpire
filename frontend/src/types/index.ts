export interface Comment {
  id: string;
  text: string;
  author: string;
  published_at: string;
  like_count: number;
  reply_count: number;
  parent_id?: string;
}

export interface VideoInfo {
  video_id: string;
  title: string;
  channel_name: string;
  thumbnail_url: string;
  published_at: string;
}

export interface AnalysisRequest {
  comment_text: string;
  context_comments?: Comment[];
}

export interface AnalysisResult {
  category: string[];
  is_counter: boolean;
  graham_hierarchy?: string;
  logical_fallacy?: string;
  validity_assessment: string;
  safe_or_out: string;
  explanation: string;
  validity_reason: string;
}

export interface CommentsResponse {
  comments: Comment[];
  next_page_token?: string;
  total_count?: number;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
}

export interface ProtestRequest {
  comment_text: string;
  original_result: AnalysisResult;
  protest_message: string;
  conversation_history: Array<{
    role: 'user' | 'umpire';
    content: string;
  }>;
}

export interface ProtestResponse {
  umpire_response: string;
  judgment_changed: boolean;
  new_result?: AnalysisResult;
}