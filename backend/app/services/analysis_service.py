import json
import os
from typing import List, Tuple
from openai import OpenAI

from app.models.comment import Comment, AnalysisRequest, AnalysisResult

class AnalysisService:
    def __init__(self, openai_api_key: str):
        print(f"Initializing AnalysisService with API key: {openai_api_key[:10]}...")
        self.client = OpenAI(api_key=openai_api_key)
        self.core_prompt, self.additional_prompt = self.load_prompts()
        print(f"Loaded prompts: core={len(self.core_prompt)} chars, additional={len(self.additional_prompt)} chars")
    
    def load_prompts(self) -> Tuple[str, str]:
        """プロンプトファイルを読み込み"""
        try:
            with open("core_prompt.txt", "r", encoding="utf-8") as f:
                core_prompt = f.read()
        except FileNotFoundError:
            core_prompt = "コアプロンプトが見つかりません"
        
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
                
                # 最新のプロンプトのJSON形式に対応
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
            print(f"Analysis error details: {type(e).__name__}: {str(e)}")
            print(f"Prompt used: {prompt[:200]}...")
            import traceback
            traceback.print_exc()
            raise ValueError(f"分析エラー: {str(e)}")