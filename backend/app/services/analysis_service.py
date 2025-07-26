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
        """プロンプトファイルを読み込み"""
        try:
            with open("core_prompt.txt", "r", encoding="utf-8") as f:
                core_prompt = f.read()
        except FileNotFoundError:
            core_prompt = """以下のYouTubeコメントを分析してください。

{context_section}

分析対象のコメント: "{comment_text}"

以下の形式でJSONを返してください。

{{
    "category": ["皮肉", "嘲笑", "感想", "意見", "アドバイス", "批判", "誹謗中傷", "悪口", "侮辱", "上から目線", "論点すり替え", "攻撃的", "賞賛", "感謝", "情報提供", "問題提起", "正論", "差別的", "共感"],
    "isCounter": true/false,
    "grahamHierarchy": "Lv1: 罵倒|Lv2: 人格攻撃|Lv3: 論調批判|Lv4: 単純否定|Lv5: 反論提示|Lv6: 論破|Lv7: 主眼論破|null",
    "logicalFallacy": "対人論証|権威論証|ストローマン論法|お前だって論法|滑り坂論法|null",
    "validityAssessment": "高い|中程度|低い|判断困難",
    "explanation": "なぜこのような判定になったのか、詳細な理由を日本語で300文字程度で説明してください。反論レベルがある場合や論理的誤謬がある場合は、それぞれの判定理由を説明してください。",
    "validityReason": "主張の妥当性について、根拠の明確さ、論理的整合性、事実との整合性の観点から100文字程度で評価理由を説明してください。"
}}"""
        
        try:
            with open("additional_prompt.txt", "r", encoding="utf-8") as f:
                additional_prompt = f.read()
        except FileNotFoundError:
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
                
                return AnalysisResult(
                    category=result_data.get("category", []),
                    is_counter=result_data.get("isCounter", False),
                    graham_hierarchy=result_data.get("grahamHierarchy"),
                    logical_fallacy=result_data.get("logicalFallacy"),
                    validity_assessment=result_data.get("validityAssessment", "判断困難"),
                    explanation=result_data.get("explanation", ""),
                    validity_reason=result_data.get("validityReason", "")
                )
            else:
                raise ValueError("有効なJSON応答が得られませんでした")
        
        except Exception as e:
            raise ValueError(f"分析エラー: {str(e)}")