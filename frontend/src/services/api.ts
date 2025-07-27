import axios, { AxiosInstance } from 'axios';
import type { 
  VideoInfo, 
  CommentsResponse, 
  Comment, 
  AnalysisRequest, 
  AnalysisResult,
  ProtestRequest,
  ProtestResponse
} from '@/types';

class CommentUmpireAPI {
  private axios: AxiosInstance;

  constructor(baseURL: string = import.meta.env.VITE_API_URL || '/api') {
    this.axios = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async extractVideo(url: string): Promise<VideoInfo> {
    const response = await this.axios.post<VideoInfo>('/videos/extract', { url });
    return response.data;
  }

  async getComments(
    videoId: string, 
    pageToken?: string, 
    maxResults: number = 100
  ): Promise<CommentsResponse> {
    const params = new URLSearchParams();
    if (pageToken) params.append('page_token', pageToken);
    params.append('max_results', maxResults.toString());

    const response = await this.axios.get<CommentsResponse>(
      `/videos/${videoId}/comments?${params.toString()}`
    );
    return response.data;
  }

  async getReplies(commentId: string): Promise<Comment[]> {
    const response = await this.axios.get<Comment[]>(`/comments/${commentId}/replies`);
    return response.data;
  }

  async analyzeComment(request: AnalysisRequest): Promise<AnalysisResult> {
    const response = await this.axios.post<AnalysisResult>('/comments/analyze', request);
    return response.data;
  }

  async getPrompts(): Promise<{ core_prompt: string; additional_prompt: string }> {
    const response = await this.axios.get('/prompts');
    return response.data;
  }

  async updatePrompts(additionalPrompt: string): Promise<{ message: string }> {
    const response = await this.axios.put('/prompts', { 
      additional_prompt: additionalPrompt 
    });
    return response.data;
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.axios.get('/health');
    return response.data;
  }

  async protestJudgment(request: ProtestRequest): Promise<ProtestResponse> {
    const response = await this.axios.post<ProtestResponse>('/comments/protest', request);
    return response.data;
  }
}

export const api = new CommentUmpireAPI();
export const protestJudgment = api.protestJudgment.bind(api);
export default CommentUmpireAPI;