import React from 'react';
import styled from 'styled-components';
import { useAppStore } from '@/hooks/useAppStore';

interface FloatingResultButtonProps {
  onClick: () => void;
}

const Button = styled.button<{ $isOut: boolean }>`
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: ${props => props.$isOut ? '#f44336' : '#4caf50'};
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  font-size: 2rem;
  font-weight: bold;
  cursor: pointer;
  z-index: 100;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;

  &:active {
    transform: translateX(-50%) scale(0.95);
  }

  &:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
  }

  @media (min-width: 769px) {
    display: none;
  }
`;

const BadgeText = styled.span`
  font-size: 1.2rem;
  font-weight: bold;
`;

export const FloatingResultButton: React.FC<FloatingResultButtonProps> = ({ onClick }) => {
  const { analysisResult } = useAppStore();
  
  if (!analysisResult) return null;
  
  const isOut = analysisResult.safe_or_out === 'out';
  
  return (
    <Button $isOut={isOut} onClick={onClick} title="分析結果を見る">
      <BadgeText>{isOut ? 'OUT' : 'SAFE'}</BadgeText>
    </Button>
  );
};