import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { useAppStore } from '@/hooks/useAppStore';
import { useUrlHistory } from '@/hooks/useUrlHistory';
import { api } from '@/services/api';

const Container = styled.div`
  margin-bottom: 2rem;
  position: relative;
`;

const Form = styled.form`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const InputWrapper = styled.div`
  flex: 1;
  position: relative;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #2196F3;
  }
`;

const HistoryDropdown = styled.div<{ $show: boolean }>`
  display: ${props => props.$show ? 'block' : 'none'};
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 50;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const HistoryItem = styled.div`
  padding: 0.75rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
  
  &:hover {
    background-color: #f5f5f5;
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const HistoryUrl = styled.div`
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.9rem;
  color: #333;
`;

const HistoryTitle = styled.div`
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const DeleteButton = styled.button`
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0.25rem;
  margin-left: 0.5rem;
  font-size: 1.2rem;
  
  &:hover {
    color: #f44336;
  }
`;

const ClearHistoryButton = styled.button`
  width: 100%;
  padding: 0.5rem;
  background-color: #f5f5f5;
  border: none;
  border-top: 1px solid #ddd;
  color: #666;
  cursor: pointer;
  font-size: 0.85rem;
  
  &:hover {
    background-color: #e0e0e0;
  }
`;

const Button = styled.button<{ $disabled?: boolean }>`
  background-color: ${props => props.$disabled ? '#ccc' : '#2196F3'};
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: ${props => props.$disabled ? 'not-allowed' : 'pointer'};
  white-space: nowrap;
  
  &:hover {
    background-color: ${props => props.$disabled ? '#ccc' : '#1976D2'};
  }
`;

const ErrorMessage = styled.div`
  color: #f44336;
  font-size: 0.875rem;
  margin-top: 0.5rem;
`;

export const URLInput: React.FC = () => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [filteredHistory, setFilteredHistory] = useState<any[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const { history, addToHistory, removeFromHistory, clearHistory } = useUrlHistory();
  
  const { 
    setVideoInfo, 
    setComments, 
    setNextPageToken, 
    setIsLoadingComments,
    setSelectedCommentId,
    reset 
  } = useAppStore();

  // 履歴のフィルタリング
  const handleInputChange = (value: string) => {
    setUrl(value);
    if (value.trim()) {
      const filtered = history.filter(item => 
        item.url.toLowerCase().includes(value.toLowerCase()) ||
        (item.title && item.title.toLowerCase().includes(value.toLowerCase()))
      );
      setFilteredHistory(filtered);
      setShowHistory(filtered.length > 0);
    } else {
      setFilteredHistory(history);
      setShowHistory(history.length > 0);
    }
  };

  // 履歴項目の選択
  const handleSelectHistory = (historyUrl: string) => {
    setUrl(historyUrl);
    setShowHistory(false);
  };

  // 履歴項目の削除
  const handleDeleteHistory = (e: React.MouseEvent, historyUrl: string) => {
    e.stopPropagation();
    removeFromHistory(historyUrl);
    setFilteredHistory(prev => prev.filter(item => item.url !== historyUrl));
  };

  // 外側クリックで履歴を閉じる
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
          inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setShowHistory(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError('');
    reset(); // 既存データをクリア
    setSelectedCommentId(null); // 選択状態もクリア

    try {
      // 動画情報を取得
      const videoInfo = await api.extractVideo(url.trim());
      setVideoInfo(videoInfo);
      
      // 履歴に追加
      addToHistory(url.trim(), videoInfo.title);
      
      // コメントを取得
      setIsLoadingComments(true);
      const commentsResponse = await api.getComments(videoInfo.video_id);
      setComments(commentsResponse.comments);
      setNextPageToken(commentsResponse.next_page_token || null);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'エラーが発生しました');
    } finally {
      setLoading(false);
      setIsLoadingComments(false);
    }
  };

  return (
    <Container>
      <Form onSubmit={handleSubmit}>
        <InputWrapper>
          <Input
            ref={inputRef}
            type="url"
            value={url}
            onChange={(e) => handleInputChange(e.target.value)}
            onFocus={() => {
              if (!url.trim()) {
                setFilteredHistory(history);
                setShowHistory(history.length > 0);
              }
            }}
            placeholder="YouTube動画のURLを入力してください"
            disabled={loading}
          />
          <HistoryDropdown ref={dropdownRef} $show={showHistory}>
            {filteredHistory.map((item) => (
              <HistoryItem 
                key={item.url}
                onClick={() => handleSelectHistory(item.url)}
              >
                <div style={{ flex: 1 }}>
                  <HistoryUrl>{item.url}</HistoryUrl>
                  {item.title && <HistoryTitle>{item.title}</HistoryTitle>}
                </div>
                <DeleteButton 
                  onClick={(e) => handleDeleteHistory(e, item.url)}
                  title="履歴から削除"
                >
                  ×
                </DeleteButton>
              </HistoryItem>
            ))}
            {history.length > 0 && (
              <ClearHistoryButton onClick={() => {
                clearHistory();
                setShowHistory(false);
              }}>
                履歴をすべてクリア
              </ClearHistoryButton>
            )}
          </HistoryDropdown>
        </InputWrapper>
        <Button 
          type="submit" 
          $disabled={loading || !url.trim()}
        >
          {loading ? '取得中...' : 'コメントを取得'}
        </Button>
      </Form>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
    </Container>
  );
};