import json
import os
from typing import List, Tuple
from openai import OpenAI

from app.models.comment import Comment, AnalysisRequest, AnalysisResult

class AnalysisService:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.core_prompt, self.additional_prompt = self.load_prompts()
    
    def load_prompts(self) -> Tuple[str, str]:
        """プロンプトをハードコードで返す"""
        core_prompt = """あなたは「コメント審判」として、YouTube動画のコメントを分析するAIアシスタントです。
与えられたコメントテキストを以下の19種類のカテゴリから該当するものすべてを選択し、JSON形式で分析結果を返してください。

## カテゴリ一覧
1. 皮肉 (irony) - 遠回しな批判や当てこすり
2. 嘲笑 (mockery) - 相手をあざ笑う、バカにする
3. 感想 (impression) - 個人的な感想や意見
4. 意見 (opinion) - 論理的な意見や主張
5. アドバイス (advice) - 建設的な提案やアドバイス
6. 批判 (criticism) - 理性的な批判
7. 誹謗中傷 (defamation) - 根拠のない悪口
8. 悪口 (insult) - 直接的な罵倒
9. 侮辱 (humiliation) - 相手の尊厳を傷つける発言
10. 上から目線 (condescending) - 見下した態度
11. 論点すり替え (strawman) - 話題を逸らす
12. 攻撃的 (aggressive) - 敵対的で攻撃的
13. 賞賛 (praise) - 褒める、評価する
14. 感謝 (gratitude) - 感謝の表現
15. 情報提供 (informative) - 有益な情報の共有
16. 問題提起 (problem_raising) - 議論すべき問題の指摘
17. 正論 (valid_point) - 筋の通った正しい意見
18. 差別的 (discriminatory) - 差別的な発言
19. 共感 (empathy) - 相手への共感や理解

## グラハムの反論ヒエラルキー
コメントが反論や批判の場合、以下のレベルで評価してください：
- Lv1: 罵倒 (name_calling) - ただの悪口
- Lv2: 人格攻撃 (ad_hominem) - 発言者への攻撃
- Lv3: 口調批判 (tone_policing) - 言い方への批判
- Lv4: 反論 (contradiction) - 根拠なき否定
- Lv5: 反証 (counter_argument) - 根拠ある反論
- Lv6: 論点反駁 (refutation) - 核心部分への反論
- Lv7: 主眼論破 (central_point_refutation) - 最重要点の論破

## 論理的誤謬
以下の論理的誤謬が含まれているか確認してください：
- 対人論証 (ad_hominem_fallacy) - 人格攻撃で論点をそらす
- 権威論証 (appeal_to_authority) - 権威を盾に主張する
- ストローマン論法 (strawman_argument) - 相手の主張を歪曲して攻撃
- お前だって論法 (whataboutism) - 相手の非を指摘して自己正当化
- 滑り坂論法 (slippery_slope) - 極端な結果を想定して反対

{context_section}

分析対象のコメント: "{comment_text}"

## 出力形式
必ず以下のJSON形式で回答してください：
{{
  "categories": ["該当するカテゴリ名の配列"],
  "graham_hierarchy": {{
    "level": レベル番号（1-7）またはnull,
    "type": "タイプ名（英語）"またはnull
  }},
  "logical_fallacies": ["該当する論理的誤謬の配列"],
  "summary": "50文字以内の分析サマリー"
}}"""
        
        additional_prompt = ""
        
        return core_prompt, additional_prompt
    
    def build_context_section(self, context_comments: List[Comment]) -> str:
        """文脈情報セクションを構築"""
        if not context_comments:
            return ""
        
        context_section = "【文脈情報】\n"
        
        for i, comment in enumerate(context_comments):
            if i == 0:
                context_section += f"親コメント: \"{comment.text}\" (投稿者: {comment.author})\n"
            else:
                context_section += f"前の返信{i}: \"{comment.text}\" (投稿者: {comment.author})\n"
        
        context_section += "\n上記の文脈を考慮して、以下のコメントを分析してください。\n"
        return context_section
    
    async def analyze_comment(self, request: AnalysisRequest) -> AnalysisResult:
        """コメントを分析"""
        context_section = ""
        if request.context_comments:
            context_section = self.build_context_section(request.context_comments)
        
        prompt = self.core_prompt.format(
            context_section=context_section,
            comment_text=request.comment_text
        )
        
        if self.additional_prompt.strip():
            prompt += f"\n\n【追加指示】\n{self.additional_prompt}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたはYouTubeコメントを分析する専門家です。指定された形式でJSON応答を返してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # JSONの抽出
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = content[json_start:json_end]
                result_data = json.loads(json_str)
                
                # 新しいJSON形式に対応
                graham_hierarchy = result_data.get("graham_hierarchy", {})
                graham_text = None
                if graham_hierarchy and graham_hierarchy.get("level"):
                    level = graham_hierarchy.get("level")
                    type_name = graham_hierarchy.get("type", "")
                    graham_text = f"Lv{level}: {type_name}"
                
                return AnalysisResult(
                    category=result_data.get("categories", []),
                    is_counter=graham_hierarchy.get("level") is not None,
                    graham_hierarchy=graham_text,
                    logical_fallacy="|".join(result_data.get("logical_fallacies", [])) if result_data.get("logical_fallacies") else None,
                    validity_assessment="中程度",
                    explanation=result_data.get("summary", ""),
                    validity_reason=result_data.get("summary", "")
                )
            else:
                raise ValueError("有効なJSON応答が得られませんでした")
        
        except Exception as e:
            raise ValueError(f"分析エラー: {str(e)}")