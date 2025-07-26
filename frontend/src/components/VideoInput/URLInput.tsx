import React, { useState } from 'react';
import styled from 'styled-components';
import { useAppStore } from '@/hooks/useAppStore';
import { api } from '@/services/api';

const Container = styled.div`
  margin-bottom: 2rem;
`;

const Form = styled.form`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const Input = styled.input`
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #2196F3;
  }
`;

const Button = styled.button<{ $disabled?: boolean }>`
  background-color: ${props => props.$disabled ? '#ccc' : '#2196F3'};
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: ${props => props.$disabled ? 'not-allowed' : 'pointer'};
  white-space: nowrap;
  
  &:hover {
    background-color: ${props => props.$disabled ? '#ccc' : '#1976D2'};
  }
`;

const ErrorMessage = styled.div`
  color: #f44336;
  font-size: 0.875rem;
  margin-top: 0.5rem;
`;

export const URLInput: React.FC = () => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { 
    setVideoInfo, 
    setComments, 
    setNextPageToken, 
    setIsLoadingComments,
    setSelectedCommentId,
    reset 
  } = useAppStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError('');
    reset(); // 既存データをクリア
    setSelectedCommentId(null); // 選択状態もクリア

    try {
      // 動画情報を取得
      const videoInfo = await api.extractVideo(url.trim());
      setVideoInfo(videoInfo);
      
      // コメントを取得
      setIsLoadingComments(true);
      const commentsResponse = await api.getComments(videoInfo.video_id);
      setComments(commentsResponse.comments);
      setNextPageToken(commentsResponse.next_page_token || null);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'エラーが発生しました');
    } finally {
      setLoading(false);
      setIsLoadingComments(false);
    }
  };

  return (
    <Container>
      <Form onSubmit={handleSubmit}>
        <Input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="YouTube動画のURLを入力してください"
          disabled={loading}
        />
        <Button 
          type="submit" 
          $disabled={loading || !url.trim()}
        >
          {loading ? '取得中...' : 'コメントを取得'}
        </Button>
      </Form>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
    </Container>
  );
};