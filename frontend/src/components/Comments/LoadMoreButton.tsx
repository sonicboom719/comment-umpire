import React, { useState } from 'react';
import styled from 'styled-components';
import { useAppStore } from '@/hooks/useAppStore';
import { api } from '@/services/api';

const Container = styled.div`
  padding: 20px;
  text-align: center;
`;

const Button = styled.button<{ $disabled?: boolean }>`
  background-color: ${props => props.$disabled ? '#ccc' : '#2196F3'};
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: ${props => props.$disabled ? 'not-allowed' : 'pointer'};
  
  &:hover {
    background-color: ${props => props.$disabled ? '#ccc' : '#1976D2'};
  }
`;

const Message = styled.p`
  color: #666;
  font-style: italic;
  margin-top: 1rem;
`;

export const LoadMoreButton: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { 
    videoInfo,
    nextPageToken, 
    addComments, 
    setNextPageToken,
    isLoadingMore,
    setIsLoadingMore 
  } = useAppStore();

  const handleLoadMore = async () => {
    if (!videoInfo || !nextPageToken || loading) return;

    setLoading(true);
    setIsLoadingMore(true);

    try {
      const response = await api.getComments(
        videoInfo.video_id, 
        nextPageToken
      );
      
      addComments(response.comments);
      setNextPageToken(response.next_page_token || null);
    } catch (error: any) {
      console.error('追加コメント取得エラー:', error);
    } finally {
      setLoading(false);
      setIsLoadingMore(false);
    }
  };

  if (!videoInfo) return null;

  if (!nextPageToken) {
    return (
      <Container>
        <Message>すべてのコメントを表示しました</Message>
      </Container>
    );
  }

  return (
    <Container>
      <Button 
        onClick={handleLoadMore}
        $disabled={loading || isLoadingMore}
      >
        {loading || isLoadingMore ? '読み込み中...' : 'さらに表示'}
      </Button>
    </Container>
  );
};