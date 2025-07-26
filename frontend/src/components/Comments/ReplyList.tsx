import React, { useState } from 'react';
import styled from 'styled-components';
import type { Comment } from '@/types';
import { useAppStore } from '@/hooks/useAppStore';
import { api } from '@/services/api';
import { CommentItem } from './CommentItem';
import { LoadingSpinner } from '../Common/LoadingSpinner';

interface ReplyListProps {
  commentId: string;
  parentComment: Comment;
  initialReplies?: Comment[];
}

const Container = styled.div`
  margin-left: 2rem;
  border-left: 2px solid #ddd;
`;

const ToggleButton = styled.button`
  background: none;
  border: none;
  color: #2196F3;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  text-align: left;
  
  &:hover {
    background-color: #f5f5f5;
  }
`;

const RepliesContainer = styled.div`
  background-color: #fafafa;
`;

export const ReplyList: React.FC<ReplyListProps> = ({ 
  commentId, 
  parentComment,
  initialReplies = []
}) => {
  const [loading, setLoading] = useState(false);
  const { 
    expandedReplies, 
    toggleReplies, 
    replies, 
    setReplies 
  } = useAppStore();
  
  const isExpanded = expandedReplies.has(commentId);
  const commentReplies = replies[commentId] || initialReplies;

  // 初期返信がある場合はストアに設定
  React.useEffect(() => {
    if (initialReplies.length > 0 && !replies[commentId]) {
      setReplies(commentId, initialReplies);
    }
  }, [commentId, initialReplies, replies, setReplies]);

  const handleToggle = async () => {
    if (!isExpanded && commentReplies.length === 0 && initialReplies.length === 0) {
      // 初回展開時で、初期返信もない場合のみAPIから取得
      setLoading(true);
      try {
        const fetchedReplies = await api.getReplies(commentId);
        setReplies(commentId, fetchedReplies);
      } catch (error: any) {
        console.error('返信取得エラー:', error);
      } finally {
        setLoading(false);
      }
    }
    
    toggleReplies(commentId);
  };

  return (
    <Container>
      <ToggleButton onClick={handleToggle}>
        {isExpanded ? '▼' : '▶'} {parentComment.reply_count}件の返信
      </ToggleButton>
      
      {isExpanded && (
        <RepliesContainer>
          {loading ? (
            <LoadingSpinner size={30} />
          ) : (
            commentReplies.map((reply, index) => (
              <CommentItem
                key={reply.id}
                comment={reply}
                isReply={true}
                parentComment={parentComment}
                previousReplies={commentReplies.slice(0, index)}
                isLast={index === commentReplies.length - 1}
              />
            ))
          )}
        </RepliesContainer>
      )}
    </Container>
  );
};