import React from 'react';
import styled from 'styled-components';
import type { AnalysisResult as AnalysisResultType } from '@/types';
import { AnalysisResult } from './AnalysisResult';
import { useAppStore } from '@/hooks/useAppStore';

interface AnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const Overlay = styled.div<{ $isOpen: boolean }>`
  display: ${props => props.$isOpen ? 'block' : 'none'};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 200;
  
  @media (min-width: 769px) {
    display: none;
  }
`;

const ModalContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: white;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
  
  @keyframes slideUp {
    from {
      transform: translateY(100%);
    }
    to {
      transform: translateY(0);
    }
  }
`;

const Header = styled.div`
  position: sticky;
  top: 0;
  background-color: white;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 1.2rem;
  color: #333;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  
  &:active {
    background-color: #f0f0f0;
  }
`;

const Content = styled.div`
  padding: 1rem;
  padding-bottom: 2rem;
`;

export const AnalysisModal: React.FC<AnalysisModalProps> = ({ isOpen, onClose }) => {
  const { 
    analysisResult, 
    selectedCommentId,
    comments,
    replies,
    setAnalysisResult
  } = useAppStore();

  // 親コメントから検索
  let selectedComment = comments.find(c => c.id === selectedCommentId);
  
  // 見つからない場合は返信コメントから検索
  if (!selectedComment) {
    for (const commentReplies of Object.values(replies)) {
      const reply = commentReplies.find(r => r.id === selectedCommentId);
      if (reply) {
        selectedComment = reply;
        break;
      }
    }
  }

  if (!analysisResult || !selectedComment) return null;

  return (
    <Overlay $isOpen={isOpen} onClick={onClose}>
      <ModalContainer onClick={e => e.stopPropagation()}>
        <Header>
          <Title>🔍 分析結果</Title>
          <CloseButton onClick={onClose}>✕</CloseButton>
        </Header>
        <Content>
          <AnalysisResult 
            result={analysisResult} 
            commentId={selectedComment.id}
            commentText={selectedComment.text}
            onResultUpdate={setAnalysisResult}
          />
        </Content>
      </ModalContainer>
    </Overlay>
  );
};