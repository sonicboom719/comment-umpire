import React from 'react';
import styled from 'styled-components';
import { useAppStore } from '@/hooks/useAppStore';
import { AnalysisResult } from '../Analysis/AnalysisResult';

const SidebarContainer = styled.aside`
  width: 400px;
  background-color: #f8f9fa;
  padding: 1rem;
  height: calc(100vh - 80px);
  overflow-y: auto;
  position: sticky;
  top: 80px;
  border-left: 1px solid #e0e0e0;
  
  @media (max-width: 768px) {
    display: none;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  color: #666;
  padding: 2rem;
  font-style: italic;
`;

export const Sidebar: React.FC = () => {
  const { 
    analysisResult, 
    analyzingCommentId, 
    setAnalysisResult,
    selectedCommentId,
    comments,
    replies 
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

  return (
    <SidebarContainer>
      {analyzingCommentId ? (
        <div>
          <h3>🔍 分析中...</h3>
          <p>コメントを分析しています。しばらくお待ちください。</p>
        </div>
      ) : analysisResult && selectedComment ? (
        <AnalysisResult 
          result={analysisResult} 
          commentId={selectedComment.id}
          commentText={selectedComment.text}
          onResultUpdate={setAnalysisResult}
        />
      ) : (
        <EmptyState>
          コメントの「⚖️ 審判」ボタンをクリックすると、<br />
          AI分析結果がここに表示されます。
        </EmptyState>
      )}
    </SidebarContainer>
  );
};