import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import type { AnalysisResult } from '@/types';
import { protestJudgment } from '@/services/api';

interface ProtestDialogProps {
  result: AnalysisResult;
  commentText: string;
  onClose: () => void;
  onResultUpdate: (newResult: AnalysisResult) => void;
}

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const Dialog = styled.div`
  background: white;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
`;

const Header = styled.div`
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 1.4rem;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #f0f0f0;
  }
`;

const ChatContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Message = styled.div<{ $isUser: boolean }>`
  align-self: ${props => props.$isUser ? 'flex-end' : 'flex-start'};
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  background-color: ${props => props.$isUser ? '#3b82f6' : '#f3f4f6'};
  color: ${props => props.$isUser ? 'white' : '#333'};
  word-wrap: break-word;
`;

const MessageAuthor = styled.div`
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 4px;
  opacity: 0.8;
`;

const InputContainer = styled.div`
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 12px;
`;

const Input = styled.textarea`
  flex: 1;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  resize: none;
  min-height: 60px;
  max-height: 120px;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: #3b82f6;
  }
`;

const SendButton = styled.button`
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #2563eb;
  }

  &:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
  }
`;

const StatusMessage = styled.div<{ $type: 'info' | 'success' | 'error' }>`
  padding: 12px;
  margin: 12px 20px;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
  background-color: ${props => {
    switch (props.$type) {
      case 'success': return '#d4edda';
      case 'error': return '#f8d7da';
      default: return '#d1ecf1';
    }
  }};
  color: ${props => {
    switch (props.$type) {
      case 'success': return '#155724';
      case 'error': return '#721c24';
      default: return '#0c5460';
    }
  }};
`;

interface ChatMessage {
  role: 'user' | 'umpire';
  content: string;
}

export const ProtestDialog: React.FC<ProtestDialogProps> = ({ 
  result, 
  commentText, 
  onClose, 
  onResultUpdate 
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<{ type: 'info' | 'success' | 'error'; message: string } | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);
    setStatus(null);

    try {
      const response = await protestJudgment({
        comment_text: commentText,
        original_result: result,
        protest_message: userMessage,
        conversation_history: messages
      });

      setMessages(prev => [...prev, { role: 'umpire', content: response.umpire_response }]);

      if (response.judgment_changed) {
        setStatus({ 
          type: 'success', 
          message: '審判が判定を変更しました！ウィンドウを閉じると新しい判定が適用されます。' 
        });
        if (response.new_result) {
          onResultUpdate(response.new_result);
        }
      }
    } catch (error) {
      setStatus({ 
        type: 'error', 
        message: 'エラーが発生しました。もう一度お試しください。' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Overlay onClick={onClose}>
      <Dialog onClick={e => e.stopPropagation()}>
        <Header>
          <Title>
            🏏 審判への抗議
          </Title>
          <CloseButton onClick={onClose}>✕</CloseButton>
        </Header>

        <ChatContainer>
          {messages.length === 0 && (
            <Message $isUser={false}>
              <MessageAuthor>審判</MessageAuthor>
              判定に対する抗議をお聞きします。どのような点にご不満がありますか？
            </Message>
          )}
          
          {messages.map((msg, index) => (
            <Message key={index} $isUser={msg.role === 'user'}>
              <MessageAuthor>{msg.role === 'user' ? 'あなた' : '審判'}</MessageAuthor>
              {msg.content}
            </Message>
          ))}
          
          {isLoading && (
            <Message $isUser={false}>
              <MessageAuthor>審判</MessageAuthor>
              考え中...
            </Message>
          )}
          
          <div ref={chatEndRef} />
        </ChatContainer>

        {status && (
          <StatusMessage $type={status.type}>
            {status.message}
          </StatusMessage>
        )}

        <InputContainer>
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="抗議内容を入力してください..."
            disabled={isLoading}
          />
          <SendButton onClick={handleSend} disabled={!input.trim() || isLoading}>
            送信
          </SendButton>
        </InputContainer>
      </Dialog>
    </Overlay>
  );
};