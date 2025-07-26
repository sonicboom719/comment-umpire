import React from 'react';
import styled from 'styled-components';
import { useAppStore } from '@/hooks/useAppStore';

const Container = styled.div`
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const Thumbnail = styled.img`
  width: 120px;
  height: 90px;
  object-fit: cover;
  border-radius: 4px;
  
  @media (max-width: 768px) {
    width: 100%;
    height: auto;
    max-width: 200px;
    margin: 0 auto;
  }
`;

const Info = styled.div`
  flex: 1;
`;

const Title = styled.h2`
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  line-height: 1.4;
  color: #333;
`;

const Channel = styled.p`
  margin: 0 0 0.25rem 0;
  color: #666;
  font-weight: 500;
`;

const Date = styled.p`
  margin: 0;
  color: #999;
  font-size: 0.875rem;
`;

const formatDate = (dateString: string): string => {
  try {
    const date = new window.Date(dateString);
    if (isNaN(date.getTime())) {
      return dateString; // 無効な日付の場合は元の文字列を返す
    }
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch (error) {
    console.error('Date formatting error:', error);
    return dateString;
  }
};

export const VideoInfo: React.FC = () => {
  const { videoInfo } = useAppStore();

  if (!videoInfo) return null;

  return (
    <Container>
      <Thumbnail 
        src={videoInfo.thumbnail_url} 
        alt={videoInfo.title}
      />
      <Info>
        <Title>{videoInfo.title}</Title>
        <Channel>{videoInfo.channel_name}</Channel>
        <Date>投稿日: {formatDate(videoInfo.published_at)}</Date>
      </Info>
    </Container>
  );
};