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

@router.get("", response_model=PromptsResponse)
async def get_prompts():
    """プロンプト設定を取得"""
    try:
        # core_prompt.txtを読み込み
        with open("core_prompt.txt", "r", encoding="utf-8") as f:
            core_prompt = f.read()
    except FileNotFoundError:
        core_prompt = "コアプロンプトが見つかりません"
    
    try:
        # additional_prompt.txtを読み込み
        with open("additional_prompt.txt", "r", encoding="utf-8") as f:
            additional_prompt = f.read()
    except FileNotFoundError:
        additional_prompt = ""
    
    return PromptsResponse(
        core_prompt=core_prompt,
        additional_prompt=additional_prompt
    )

@router.put("", response_model=Dict[str, str])
async def update_prompts(request: PromptsUpdateRequest):
    """追加プロンプトを更新"""
    try:
        # additional_prompt.txtを更新
        with open("additional_prompt.txt", "w", encoding="utf-8") as f:
            f.write(request.additional_prompt)
        
        return {"message": "プロンプトが更新されました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プロンプト更新エラー: {str(e)}")