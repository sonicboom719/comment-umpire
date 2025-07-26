import React from 'react';
import styled from 'styled-components';
import { getCategoryColor, getCategoryTextColor } from '@/styles/colors';

interface CategoryBadgeProps {
  category: string;
  className?: string;
}

const Badge = styled.span<{ $backgroundColor: string; $textColor: string }>`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  margin-right: 8px;
  margin-bottom: 4px;
  background-color: ${props => props.$backgroundColor};
  color: ${props => props.$textColor};
`;

export const CategoryBadge: React.FC<CategoryBadgeProps> = ({ 
  category, 
  className 
}) => {
  const backgroundColor = getCategoryColor(category);
  const textColor = getCategoryTextColor(category);
  
  return (
    <Badge 
      $backgroundColor={backgroundColor}
      $textColor={textColor}
      className={className}
    >
      {category}
    </Badge>
  );
};