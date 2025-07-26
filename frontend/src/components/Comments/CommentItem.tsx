import React from 'react';
import styled from 'styled-components';
import type { Comment } from '@/types';
import { useAppStore } from '@/hooks/useAppStore';
import { JudgeButton } from './JudgeButton';
import { ReplyList } from './ReplyList';

interface CommentItemProps {
  comment: Comment;
  isLast?: boolean;
  isReply?: boolean;
  parentComment?: Comment;
  previousReplies?: Comment[];
  initialReplies?: Comment[];
}

const Container = styled.div<{ $isLast?: boolean; $isReply?: boolean; $isSelected?: boolean }>`
  padding: 1rem;
  border-bottom: ${props => props.$isLast ? 'none' : '1px solid #e0e0e0'};
  margin-left: ${props => props.$isReply ? '2rem' : '0'};
  border-left: ${props => props.$isReply ? '2px solid #ddd' : 'none'};
  padding-left: ${props => props.$isReply ? '1rem' : '1rem'};
  background-color: ${props => props.$isSelected ? '#e3f2fd' : 'transparent'};
  transition: background-color 0.3s ease;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  gap: 1rem;
`;

const AuthorInfo = styled.div`
  flex: 1;
`;

const Author = styled.span`
  font-weight: bold;
  color: #333;
  font-size: 0.9rem;
`;

const Date = styled.span`
  color: #666;
  font-size: 0.8rem;
  margin-left: 0.5rem;
`;

const Text = styled.p`
  margin: 0.5rem 0;
  line-height: 1.5;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
`;

const Stats = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #666;
`;

const LikeCount = styled.span`
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 0.5rem;
  align-items: center;
`;

const formatDate = (dateString: string): string => {
  try {
    const date = new window.Date(dateString);
    const now = new window.Date();
    
    if (isNaN(date.getTime()) || isNaN(now.getTime())) {
      return dateString;
    }
    
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return '今日';
    if (diffDays === 1) return '1日前';
    if (diffDays < 30) return `${diffDays}日前`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}ヶ月前`;
    return `${Math.floor(diffDays / 365)}年前`;
  } catch (error) {
    console.error('Date formatting error:', error);
    return dateString;
  }
};

const removeHtmlTags = (text: string): string => {
  return text
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]+>/g, '');
};

export const CommentItem: React.FC<CommentItemProps> = ({ 
  comment, 
  isLast = false,
  isReply = false,
  parentComment,
  previousReplies,
  initialReplies
}) => {
  const { selectedCommentId } = useAppStore();
  const cleanText = removeHtmlTags(comment.text);
  const isSelected = selectedCommentId === comment.id;

  return (
    <>
      <Container $isLast={isLast} $isReply={isReply} $isSelected={isSelected}>
        <Header>
          <AuthorInfo>
            <Author>{comment.author}</Author>
            <Date>{formatDate(comment.published_at)}</Date>
          </AuthorInfo>
          
          <ButtonGroup>
            <JudgeButton 
              comment={comment}
              parentComment={parentComment}
              previousReplies={previousReplies}
            />
          </ButtonGroup>
        </Header>
        
        <Text>{cleanText}</Text>
        
        <Stats>
          <LikeCount>
            👍 {comment.like_count}
          </LikeCount>
          {comment.reply_count > 0 && (
            <span>💬 {comment.reply_count}件の返信</span>
          )}
        </Stats>
      </Container>
      
      {!isReply && (comment.reply_count > 0 || initialReplies?.length) && (
        <ReplyList 
          commentId={comment.id} 
          parentComment={comment}
          initialReplies={initialReplies}
        />
      )}
    </>
  );
};