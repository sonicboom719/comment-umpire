export const CATEGORY_COLORS = {
  '皮肉': '#FF5722',
  '嘲笑': '#E91E63', 
  '感想': '#4CAF50',
  '意見': '#2196F3',
  'アドバイス': '#00BCD4',
  '批判': '#FF9800',
  '誹謗中傷': '#F44336',
  '悪口': '#9C27B0',
  '侮辱': '#D32F2F',
  '上から目線': '#795548',
  '論点すり替え': '#607D8B',
  '攻撃的': '#B71C1C',
  '賞賛': '#8BC34A',
  '感謝': '#FFC107',
  '情報提供': '#3F51B5',
  '問題提起': '#FF5722',
  '正論': '#009688',
  '差別的': '#212121',
  '共感': '#FFB6C1',
  '質問': '#9E9E9E',
  '回答': '#03A9F4',
  '要望': '#673AB7',
  '指図': '#E64A19'
} as const;

export type CategoryType = keyof typeof CATEGORY_COLORS;

export const getCategoryColor = (category: string): string => {
  return CATEGORY_COLORS[category as CategoryType] || '#666666';
};

export const getCategoryTextColor = (category: string): string => {
  const darkCategories = ['感謝', '共感'];
  return darkCategories.includes(category) ? '#000000' : '#ffffff';
};