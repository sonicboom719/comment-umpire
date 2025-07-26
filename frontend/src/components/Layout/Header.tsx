import React from 'react';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background-color: #2196F3;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Title = styled.h1`
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Icon = styled.span`
  font-size: 1.8rem;
`;

export const Header: React.FC = () => {
  return (
    <HeaderContainer>
      <Title>
        <Icon>💬</Icon>
        コメント審判 (YouTube動画からコメントを吸い上げてAI審判がジャッジします)
      </Title>
    </HeaderContainer>
  );
};