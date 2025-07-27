import React from 'react';
import styled from 'styled-components';
import type { AnalysisResult } from '@/types';

interface UmpireJudgmentProps {
  result: AnalysisResult;
}

const Container = styled.div<{ $isOut: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 12px;
  background: ${props => props.$isOut 
    ? 'linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)'
    : 'linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%)'
  };
  border: 3px solid ${props => props.$isOut ? '#f44336' : '#4caf50'};
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
`;

const JudgmentText = styled.div<{ $isOut: boolean }>`
  font-size: 2rem;
  font-weight: bold;
  color: ${props => props.$isOut ? '#d32f2f' : '#388e3c'};
  margin-bottom: 1rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
`;

const UmpireImage = styled.img`
  width: 100%;
  height: 200px;
  margin-bottom: 0.5rem;
  filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.2));
  object-fit: contain;
`;

const JudgmentLabel = styled.div`
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
`;

export const UmpireJudgment: React.FC<UmpireJudgmentProps> = ({ result }) => {
  const isOut = result.safe_or_out === 'out';
  
  return (
    <Container $isOut={isOut}>
      <UmpireImage 
        src={isOut ? '/image/out.png' : '/image/safe.png'}
        alt={isOut ? 'アウト判定' : 'セーフ判定'}
      />
      
      
      <JudgmentLabel>
        審判判定: {isOut ? '不適切なコメント' : '適切なコメント'}
      </JudgmentLabel>
    </Container>
  );
};