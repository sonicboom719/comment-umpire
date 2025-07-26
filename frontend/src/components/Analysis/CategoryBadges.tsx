import React from 'react';
import styled from 'styled-components';
import { CategoryBadge } from '../Common/CategoryBadge';

interface CategoryBadgesProps {
  categories: string[];
}

const Container = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
`;

export const CategoryBadges: React.FC<CategoryBadgesProps> = ({ categories }) => {
  return (
    <Container>
      {categories.map((category, index) => (
        <CategoryBadge 
          key={`${category}-${index}`} 
          category={category} 
        />
      ))}
    </Container>
  );
};