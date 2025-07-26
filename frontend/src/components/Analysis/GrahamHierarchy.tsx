import React from 'react';
import styled from 'styled-components';

interface GrahamHierarchyProps {
  level: string;
}

const Container = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const LevelBadge = styled.span<{ $level: number }>`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: bold;
  color: white;
  background-color: ${props => {
    if (props.$level <= 2) return '#f44336'; // 低レベル（罵倒、人格攻撃）
    if (props.$level <= 4) return '#FF9800'; // 中レベル（論調批判、単純否定）
    return '#4CAF50'; // 高レベル（反論提示、論破、主眼論破）
  }};
`;

const Description = styled.span`
  font-size: 0.875rem;
  color: #666;
`;

const getLevelNumber = (level: string): number => {
  const match = level.match(/Lv(\d+)/);
  return match ? parseInt(match[1]) : 0;
};

const getLevelDescription = (level: string): string => {
  if (level.includes('罵倒')) return '最低レベル';
  if (level.includes('人格攻撃')) return '非常に低い';
  if (level.includes('論調批判')) return '低い';
  if (level.includes('単純否定')) return 'やや低い';
  if (level.includes('反論提示')) return '普通';
  if (level.includes('論破')) return '高い';
  if (level.includes('主眼論破')) return '最高レベル';
  return '';
};

export const GrahamHierarchy: React.FC<GrahamHierarchyProps> = ({ level }) => {
  const levelNumber = getLevelNumber(level);
  const description = getLevelDescription(level);

  return (
    <Container>
      <LevelBadge $level={levelNumber}>
        {level}
      </LevelBadge>
      {description && (
        <Description>
          ({description})
        </Description>
      )}
    </Container>
  );
};