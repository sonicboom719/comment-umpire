import { useState, useEffect } from 'react';

const STORAGE_KEY = 'comment_umpire_url_history';
const MAX_HISTORY_ITEMS = 10;

interface UrlHistoryItem {
  url: string;
  title?: string;
  timestamp: number;
}

export const useUrlHistory = () => {
  const [history, setHistory] = useState<UrlHistoryItem[]>([]);

  // 初回読み込み
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setHistory(parsed);
      } catch (e) {
        console.error('Failed to parse URL history:', e);
      }
    }
  }, []);

  // 履歴に追加
  const addToHistory = (url: string, title?: string) => {
    const newItem: UrlHistoryItem = {
      url,
      title,
      timestamp: Date.now()
    };

    setHistory(prev => {
      // 既存の同じURLを削除
      const filtered = prev.filter(item => item.url !== url);
      
      // 新しいアイテムを先頭に追加
      const updated = [newItem, ...filtered].slice(0, MAX_HISTORY_ITEMS);
      
      // localStorageに保存
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      
      return updated;
    });
  };

  // 特定のアイテムを削除
  const removeFromHistory = (url: string) => {
    setHistory(prev => {
      const updated = prev.filter(item => item.url !== url);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  // 全履歴をクリア
  const clearHistory = () => {
    localStorage.removeItem(STORAGE_KEY);
    setHistory([]);
  };

  return {
    history,
    addToHistory,
    removeFromHistory,
    clearHistory
  };
};