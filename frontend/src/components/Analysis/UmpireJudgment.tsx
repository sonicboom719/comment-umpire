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

const UmpireImage = styled.div<{ $isOut: boolean }>`
  font-size: 4rem;
  margin-bottom: 0.5rem;
  filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.2));
`;

const JudgmentLabel = styled.div`
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
`;

// 審判のジェスチャーを表現するSVGアイコン
const SafeGesture = () => (
  <svg width="80" height="80" viewBox="0 0 100 100" fill="none">
    {/* 審判の体 */}
    <circle cx="50" cy="30" r="12" fill="#333" stroke="#000" strokeWidth="2"/>
    <rect x="42" y="40" width="16" height="35" fill="#333" stroke="#000" strokeWidth="2" rx="3"/>
    
    {/* セーフのジェスチャー（両手を横に広げる） */}
    <line x1="30" y1="50" x2="42" y2="45" stroke="#333" strokeWidth="4" strokeLinecap="round"/>
    <line x1="58" y1="45" x2="70" y2="50" stroke="#333" strokeWidth="4" strokeLinecap="round"/>
    
    {/* 顔 */}
    <circle cx="47" cy="27" r="1.5" fill="#fff"/>
    <circle cx="53" cy="27" r="1.5" fill="#fff"/>
    <path d="M 46 32 Q 50 35 54 32" stroke="#fff" strokeWidth="1.5" fill="none"/>
    
    {/* 帽子 */}
    <path d="M 38 25 Q 50 20 62 25 Q 62 22 50 18 Q 38 22 38 25" fill="#000"/>
  </svg>
);

const OutGesture = () => (
  <svg width="80" height="80" viewBox="0 0 100 100" fill="none">
    {/* 審判の体 */}
    <circle cx="50" cy="30" r="12" fill="#333" stroke="#000" strokeWidth="2"/>
    <rect x="42" y="40" width="16" height="35" fill="#333" stroke="#000" strokeWidth="2" rx="3"/>
    
    {/* アウトのジェスチャー（右手を上に突き上げる） */}
    <line x1="58" y1="45" x2="65" y2="25" stroke="#333" strokeWidth="4" strokeLinecap="round"/>
    <circle cx="65" cy="25" r="3" fill="#333"/>
    
    {/* 左手は腰に */}
    <line x1="42" y1="50" x2="38" y2="55" stroke="#333" strokeWidth="4" strokeLinecap="round"/>
    
    {/* 顔（厳しい表情） */}
    <circle cx="47" cy="27" r="1.5" fill="#fff"/>
    <circle cx="53" cy="27" r="1.5" fill="#fff"/>
    <path d="M 46 33 L 54 33" stroke="#fff" strokeWidth="1.5"/>
    
    {/* 帽子 */}
    <path d="M 38 25 Q 50 20 62 25 Q 62 22 50 18 Q 38 22 38 25" fill="#000"/>
  </svg>
);

export const UmpireJudgment: React.FC<UmpireJudgmentProps> = ({ result }) => {
  const isOut = result.safe_or_out === 'out';
  
  return (
    <Container $isOut={isOut}>
      <UmpireImage $isOut={isOut}>
        {isOut ? <OutGesture /> : <SafeGesture />}
      </UmpireImage>
      
      <JudgmentText $isOut={isOut}>
        {isOut ? '🚫 OUT!' : '✅ SAFE!'}
      </JudgmentText>
      
      <JudgmentLabel>
        審判判定: {isOut ? '不適切なコメント' : '適切なコメント'}
      </JudgmentLabel>
    </Container>
  );
};