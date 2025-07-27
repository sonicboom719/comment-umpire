from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
import os

router = APIRouter()

class PromptsResponse(BaseModel):
    core_prompt: str
    additional_prompt: str

class PromptsUpdateRequest(BaseModel):
    additional_prompt: str

# デフォルトのプロンプト
DEFAULT_CORE_PROMPT = """あなたは「コメント審判」として、YouTube動画のコメントを分析するAIアシスタントです。

与えられたコメントを以下の観点から分析してください：

1. カテゴリ分類（19種類）
2. グラハムの反論ヒエラルキー（該当する場合）
3. 論理的誤謬（該当する場合）

必ず指定されたJSON形式で回答してください。"""

@router.get("", response_model=PromptsResponse)
async def get_prompts():
    """プロンプト設定を取得（環境変数から）"""
    # 環境変数から取得、なければファイルから読み込みを試みる
    core_prompt = os.getenv("CORE_PROMPT", "")
    additional_prompt = os.getenv("ADDITIONAL_PROMPT", "")
    
    if not core_prompt:
        # ファイルから読み込みを試みる
        try:
            with open("core_prompt.txt", "r", encoding="utf-8") as f:
                core_prompt = f.read()
        except:
            try:
                with open("../core_prompt.txt", "r", encoding="utf-8") as f:
                    core_prompt = f.read()
            except:
                core_prompt = DEFAULT_CORE_PROMPT
    
    if not additional_prompt:
        try:
            with open("additional_prompt.txt", "r", encoding="utf-8") as f:
                additional_prompt = f.read()
        except:
            try:
                with open("../additional_prompt.txt", "r", encoding="utf-8") as f:
                    additional_prompt = f.read()
            except:
                additional_prompt = ""
    
    return PromptsResponse(
        core_prompt=core_prompt,
        additional_prompt=additional_prompt
    )

@router.put("", response_model=Dict[str, str])
async def update_prompts(request: PromptsUpdateRequest):
    """追加プロンプトを更新"""
    # 本番環境では環境変数の更新はできないため、エラーを返す
    if os.getenv("RENDER"):
        raise HTTPException(
            status_code=400, 
            detail="本番環境ではプロンプトの更新はできません。環境変数で設定してください。"
        )
    
    try:
        with open("additional_prompt.txt", "w", encoding="utf-8") as f:
            f.write(request.additional_prompt)
        return {"message": "プロンプトが更新されました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プロンプト更新エラー: {str(e)}")