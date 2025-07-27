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
                    safe_or_out=result_data.get("safeOrOut", "safe"),
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
    
    async def handle_protest(self, request) -> dict:
        """抗議に対する審判の応答を生成"""
        from app.models.comment import ProtestResponse
        
        # 会話履歴を構築
        conversation = "これまでの会話:\n"
        for msg in request.conversation_history:
            role = "ユーザー" if msg.role == "user" else "審判"
            conversation += f"{role}: {msg.content}\n"
        
        # 審判としてのプロンプトを作成
        prompt = f"""あなたはプロ野球の主審です。コメント判定に対する抗議を受けています。
実際のプロ野球審判のように、以下の特徴を持って対応してください：

1. プロフェッショナルで毅然とした態度
2. 判定の根拠を論理的に説明
3. 感情的な抗議には冷静に対処
4. 明確な証拠がある場合のみ判定を覆す
5. 必要に応じて警告を与える

【元のコメント】
"{request.comment_text}"

【元の判定結果】
- カテゴリー: {', '.join(request.original_result.category)}
- セーフ/アウト: {request.original_result.safe_or_out}
- 判定理由: {request.original_result.explanation}
- 妥当性評価: {request.original_result.validity_assessment}

{conversation}

【ユーザーからの新たな抗議】
{request.protest_message}

【判定変更の基準】
- 元の判定に明確な誤りがある場合
- 重要な文脈を見落としていた場合
- カテゴリー分類に明らかな間違いがある場合

単なる意見の相違や感情的な不満では判定を変更しません。

応答をJSON形式で返してください：
{{
    "umpireResponse": "プロ野球審判としての毅然とした応答（100-150文字）",
    "judgmentChanged": true/false,
    "newSafeOrOut": "safe/out（変更時のみ）",
    "newExplanation": "新しい判定理由（変更時のみ、100-150文字）"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "あなたは経験豊富なプロ野球の主審です。判定には絶対的な自信を持ち、論理的で公正な判断を下します。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = content[json_start:json_end]
                result_data = json.loads(json_str)
                
                protest_response = ProtestResponse(
                    umpire_response=result_data.get("umpireResponse", ""),
                    judgment_changed=result_data.get("judgmentChanged", False)
                )
                
                # 判定が変更された場合、新しい結果を作成
                if result_data.get("judgmentChanged", False):
                    new_result = request.original_result.copy()
                    new_result.safe_or_out = result_data.get("newSafeOrOut", request.original_result.safe_or_out)
                    new_result.explanation = result_data.get("newExplanation", request.original_result.explanation)
                    protest_response.new_result = new_result
                
                return protest_response
            else:
                raise ValueError("有効なJSON応答が得られませんでした")
                
        except Exception as e:
            print(f"Protest handling error: {str(e)}")
            raise ValueError(f"抗議処理エラー: {str(e)}")