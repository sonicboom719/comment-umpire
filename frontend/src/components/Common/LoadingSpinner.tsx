import React from 'react';
import styled, { keyframes } from 'styled-components';

interface LoadingSpinnerProps {
  size?: number;
  color?: string;
  className?: string;
}

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const Spinner = styled.div<{ $size: number; $color: string }>`
  border: 2px solid #f3f3f3;
  border-top: 2px solid ${props => props.$color};
  border-radius: 50%;
  width: ${props => props.$size}px;
  height: ${props => props.$size}px;
  animation: ${spin} 1s linear infinite;
  margin: 0 auto;
`;

const Container = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
`;

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 40,
  color = '#2196F3',
  className
}) => {
  return (
    <Container className={className}>
      <Spinner $size={size} $color={color} />
    </Container>
  );
};