import React, { useState } from 'react';
import styled from 'styled-components';
import type { Comment } from '@/types';
import { useAppStore } from '@/hooks/useAppStore';
import { api } from '@/services/api';

interface JudgeButtonProps {
  comment: Comment;
  parentComment?: Comment;
  previousReplies?: Comment[];
}

const Button = styled.button<{ $analyzing?: boolean }>`
  background-color: ${props => props.$analyzing ? '#ffa726' : '#4CAF50'};
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: ${props => props.$analyzing ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${props => props.$analyzing ? '#ffa726' : '#45a049'};
  }
  
  &:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
`;

export const JudgeButton: React.FC<JudgeButtonProps> = ({
  comment,
  parentComment,
  previousReplies
}) => {
  const [analyzing, setAnalyzing] = useState(false);
  const { 
    setAnalysisResult, 
    setAnalyzingCommentId, 
    analyzingCommentId,
    setSelectedCommentId 
  } = useAppStore();

  const handleAnalyze = async () => {
    if (analyzing || analyzingCommentId) return;

    setAnalyzing(true);
    setAnalyzingCommentId(comment.id);
    setSelectedCommentId(comment.id);
    setAnalysisResult(null);

    try {
      // 文脈コメントを構築（返信の場合）
      const contextComments: Comment[] = [];
      if (comment.parent_id && parentComment) {
        contextComments.push(parentComment);
        if (previousReplies) {
          contextComments.push(...previousReplies);
        }
      }

      const result = await api.analyzeComment({
        comment_text: comment.text,
        context_comments: contextComments.length > 0 ? contextComments : undefined
      });

      setAnalysisResult(result);
    } catch (error: any) {
      console.error('分析エラー:', error);
      // エラー時の処理（後でエラートーストなど追加可能）
    } finally {
      setAnalyzing(false);
      setAnalyzingCommentId(null);
    }
  };

  const isCurrentlyAnalyzing = analyzingCommentId === comment.id;
  const isDisabled = !!analyzingCommentId && !isCurrentlyAnalyzing;

  return (
    <Button
      onClick={handleAnalyze}
      $analyzing={isCurrentlyAnalyzing}
      disabled={isDisabled}
      title="AIでコメントを分析"
    >
      ⚖️ {isCurrentlyAnalyzing ? '分析中...' : '審判'}
    </Button>
  );
};