import React from 'react';
import styled from 'styled-components';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface MainLayoutProps {
  children: React.ReactNode;
}

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const Content = styled.div`
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 1rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 0;
  }
`;

const MainContent = styled.main`
  padding: 1rem;
  overflow-x: hidden;
`;

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <Container>
      <Header />
      <Content>
        <MainContent>
          {children}
        </MainContent>
        <Sidebar />
      </Content>
    </Container>
  );
};