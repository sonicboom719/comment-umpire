import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from './components/Layout/MainLayout';
import { URLInput } from './components/VideoInput/URLInput';
import { VideoInfo } from './components/VideoInput/VideoInfo';
import { CommentList } from './components/Comments/CommentList';
import { GlobalStyle } from './styles/GlobalStyle';
import { ErrorBoundary } from './components/Common/ErrorBoundary';
import { FloatingResultButton } from './components/Common/FloatingResultButton';
import { AnalysisModal } from './components/Analysis/AnalysisModal';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5分
      gcTime: 10 * 60 * 1000,   // 10分
    },
  },
});

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <GlobalStyle />
        <MainLayout>
          <URLInput />
          <VideoInfo />
          <CommentList />
        </MainLayout>
        <FloatingResultButton onClick={() => setIsModalOpen(true)} />
        <AnalysisModal 
          isOpen={isModalOpen} 
          onClose={() => setIsModalOpen(false)} 
        />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;