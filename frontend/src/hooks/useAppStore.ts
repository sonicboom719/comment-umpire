import { create } from 'zustand';
import type { VideoInfo, Comment, AnalysisResult } from '@/types';

interface AppState {
  // 動画関連
  videoInfo: VideoInfo | null;
  comments: Comment[];
  nextPageToken: string | null;
  
  // UI状態
  isLoadingComments: boolean;
  isLoadingMore: boolean;
  expandedReplies: Set<string>;
  
  // 分析関連
  analysisResult: AnalysisResult | null;
  analyzingCommentId: string | null;
  selectedCommentId: string | null;
  
  // アクション
  setVideoInfo: (info: VideoInfo | null) => void;
  setComments: (comments: Comment[]) => void;
  addComments: (comments: Comment[]) => void;
  setNextPageToken: (token: string | null) => void;
  setIsLoadingComments: (loading: boolean) => void;
  setIsLoadingMore: (loading: boolean) => void;
  toggleReplies: (commentId: string) => void;
  setAnalysisResult: (result: AnalysisResult | null) => void;
  setAnalyzingCommentId: (id: string | null) => void;
  setSelectedCommentId: (id: string | null) => void;
  
  // 返信コメント管理
  replies: Record<string, Comment[]>;
  setReplies: (commentId: string, replies: Comment[]) => void;
  
  // リセット
  reset: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // 初期状態
  videoInfo: null,
  comments: [],
  nextPageToken: null,
  isLoadingComments: false,
  isLoadingMore: false,
  expandedReplies: new Set(),
  analysisResult: null,
  analyzingCommentId: null,
  selectedCommentId: null,
  replies: {},
  
  // アクション
  setVideoInfo: (info) => set({ videoInfo: info }),
  
  setComments: (comments) => set({ comments }),
  
  addComments: (newComments) => set((state) => ({
    comments: [...state.comments, ...newComments]
  })),
  
  setNextPageToken: (token) => set({ nextPageToken: token }),
  
  setIsLoadingComments: (loading) => set({ isLoadingComments: loading }),
  
  setIsLoadingMore: (loading) => set({ isLoadingMore: loading }),
  
  toggleReplies: (commentId) => set((state) => {
    const newExpandedReplies = new Set(state.expandedReplies);
    if (newExpandedReplies.has(commentId)) {
      newExpandedReplies.delete(commentId);
    } else {
      newExpandedReplies.add(commentId);
    }
    return { expandedReplies: newExpandedReplies };
  }),
  
  setAnalysisResult: (result) => set({ analysisResult: result }),
  
  setAnalyzingCommentId: (id) => set({ analyzingCommentId: id }),
  
  setSelectedCommentId: (id) => set({ selectedCommentId: id }),
  
  setReplies: (commentId, replies) => set((state) => ({
    replies: { ...state.replies, [commentId]: replies }
  })),
  
  reset: () => set({
    videoInfo: null,
    comments: [],
    nextPageToken: null,
    isLoadingComments: false,
    isLoadingMore: false,
    expandedReplies: new Set(),
    analysisResult: null,
    analyzingCommentId: null,
    selectedCommentId: null,
    replies: {}
  })
}));