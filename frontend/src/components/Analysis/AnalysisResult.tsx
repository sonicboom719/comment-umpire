import React, { useState } from 'react';
import styled from 'styled-components';
import type { AnalysisResult as AnalysisResultType } from '@/types';
import { CategoryBadges } from './CategoryBadges';
import { GrahamHierarchy } from './GrahamHierarchy';
import { LogicalFallacy } from './LogicalFallacy';
import { UmpireJudgment } from './UmpireJudgment';
import { ProtestDialog } from './ProtestDialog';

interface AnalysisResultProps {
  result: AnalysisResultType;
  commentId: string;
  commentText: string;
  onResultUpdate: (newResult: AnalysisResultType) => void;
}

const Container = styled.div`
  background-color: #f0f2f6;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 15px;
`;

const Title = styled.h3`
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Section = styled.div`
  margin-bottom: 1rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const SectionTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  color: #555;
  font-size: 0.9rem;
  font-weight: 600;
`;

const ValidityAssessment = styled.div<{ $level: string }>`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: bold;
  background-color: ${props => {
    switch (props.$level) {
      case '高い': return '#4CAF50';
      case '中程度': return '#FF9800';
      case '低い': return '#f44336';
      default: return '#9E9E9E';
    }
  }};
  color: white;
`;

const Explanation = styled.p`
  margin: 0;
  line-height: 1.5;
  color: #333;
  font-size: 0.9rem;
`;

const ProtestButton = styled.button`
  background-color: #ff6b6b;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    background-color: #ff5252;
  }

  &:active {
    transform: translateY(1px);
  }
`;

export const AnalysisResult: React.FC<AnalysisResultProps> = ({ result, commentId, commentText, onResultUpdate }) => {
  const [showProtest, setShowProtest] = useState(false);

  return (
    <Container>
      <UmpireJudgment result={result} />
      
      <Title>
        🔍 コメント分析結果
      </Title>
      
      <Section>
        <SectionTitle>カテゴリー</SectionTitle>
        <CategoryBadges categories={result.category} />
      </Section>

      {result.is_counter && result.graham_hierarchy && (
        <Section>
          <SectionTitle>反論の質（グラハムのヒエラルキー）</SectionTitle>
          <GrahamHierarchy level={result.graham_hierarchy} />
        </Section>
      )}

      {result.logical_fallacy && result.logical_fallacy !== 'null' && (
        <Section>
          <SectionTitle>論理的誤謬</SectionTitle>
          <LogicalFallacy fallacy={result.logical_fallacy} />
        </Section>
      )}

      <Section>
        <SectionTitle>主張の妥当性</SectionTitle>
        <ValidityAssessment $level={result.validity_assessment}>
          {result.validity_assessment}
        </ValidityAssessment>
      </Section>

      <Section>
        <SectionTitle>判定理由</SectionTitle>
        <Explanation>{result.explanation}</Explanation>
      </Section>

      {result.validity_reason && (
        <Section>
          <SectionTitle>妥当性評価の理由</SectionTitle>
          <Explanation>{result.validity_reason}</Explanation>
        </Section>
      )}

      <ProtestButton onClick={() => setShowProtest(true)}>
        🚩 判定に抗議する
      </ProtestButton>

      {showProtest && (
        <ProtestDialog
          result={result}
          commentText={commentText}
          onClose={() => setShowProtest(false)}
          onResultUpdate={(newResult) => {
            onResultUpdate(newResult);
            setShowProtest(false);
          }}
        />
      )}
    </Container>
  );
};