import React, { Component, ErrorInfo, ReactNode } from 'react';
import styled from 'styled-components';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

const ErrorContainer = styled.div`
  padding: 2rem;
  text-align: center;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  margin: 2rem;
`;

const ErrorTitle = styled.h2`
  color: #c00;
  margin-bottom: 1rem;
`;

const ErrorMessage = styled.pre`
  text-align: left;
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  overflow: auto;
  max-width: 100%;
`;

const ReloadButton = styled.button`
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
  
  &:hover {
    background-color: #1976D2;
  }
`;

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <ErrorContainer>
          <ErrorTitle>エラーが発生しました</ErrorTitle>
          <ErrorMessage>
            {this.state.error?.toString()}
          </ErrorMessage>
          <ReloadButton onClick={this.handleReload}>
            ページを再読み込み
          </ReloadButton>
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}