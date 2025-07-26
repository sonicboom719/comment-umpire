import React from 'react';
import styled from 'styled-components';
import { useAppStore } from '@/hooks/useAppStore';
import { CommentItem } from './CommentItem';
import { LoadMoreButton } from './LoadMoreButton';
import { LoadingSpinner } from '../Common/LoadingSpinner';

const Container = styled.div`
  margin-bottom: 2rem;
`;

const CommentsHeader = styled.h3`
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.2rem;
`;

const CommentsList = styled.div`
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const EmptyState = styled.div`
  padding: 2rem;
  text-align: center;
  color: #666;
`;

export const CommentList: React.FC = () => {
  const { 
    comments, 
    isLoadingComments, 
    videoInfo 
  } = useAppStore();

  if (!videoInfo) return null;

  if (isLoadingComments) {
    return (
      <Container>
        <CommentsHeader>コメント</CommentsHeader>
        <LoadingSpinner />
      </Container>
    );
  }

  if (comments.length === 0) {
    return (
      <Container>
        <CommentsHeader>コメント</CommentsHeader>
        <CommentsList>
          <EmptyState>
            コメントが見つかりませんでした。
          </EmptyState>
        </CommentsList>
      </Container>
    );
  }

  return (
    <Container>
      <CommentsHeader>
        コメント ({comments.filter(c => !c.parent_id).length}件)
      </CommentsHeader>
      
      <CommentsList>
        {comments.map((comment, index) => {
          // 親コメントのみ表示（返信は親コメント内で表示）
          if (!comment.parent_id) {
            // このコメントの返信を取得
            const replies = comments.filter(c => c.parent_id === comment.id);
            
            return (
              <CommentItem 
                key={comment.id} 
                comment={comment}
                isLast={index === comments.length - 1}
                initialReplies={replies}
              />
            );
          }
          return null;
        })}
      </CommentsList>
      
      <LoadMoreButton />
    </Container>
  );
};