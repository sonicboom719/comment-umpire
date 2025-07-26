import React from 'react';
import styled from 'styled-components';

interface LogicalFallacyProps {
  fallacy: string;
}

const Container = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const FallacyBadge = styled.span`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: bold;
  color: white;
  background-color: #E91E63;
`;

const Description = styled.span`
  font-size: 0.875rem;
  color: #666;
`;

const getFallacyDescription = (fallacy: string): string => {
  switch (fallacy) {
    case '対人論証':
      return '相手の人格を攻撃';
    case '権威論証':
      return '権威に頼った主張';
    case 'ストローマン論法':
      return '相手の主張を歪曲';
    case 'お前だって論法':
      return '相手も同じと指摘';
    case '滑り坂論法':
      return '極端な結果を想定';
    default:
      return '';
  }
};

export const LogicalFallacy: React.FC<LogicalFallacyProps> = ({ fallacy }) => {
  const description = getFallacyDescription(fallacy);

  return (
    <Container>
      <FallacyBadge>
        {fallacy}
      </FallacyBadge>
      {description && (
        <Description>
          ({description})
        </Description>
      )}
    </Container>
  );
};