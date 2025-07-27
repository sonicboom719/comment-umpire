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
    # 現在のスクリプトの位置から相対パスを計算
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # app/api -> app -> backend
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    
    try:
        # core_prompt.txtを読み込み
        core_prompt_path = os.path.join(backend_dir, "core_prompt.txt")
        with open(core_prompt_path, "r", encoding="utf-8") as f:
            core_prompt = f.read()
    except FileNotFoundError:
        # backendディレクトリになければ、親ディレクトリも試す
        try:
            parent_dir = os.path.dirname(backend_dir)
            core_prompt_path = os.path.join(parent_dir, "core_prompt.txt")
            with open(core_prompt_path, "r", encoding="utf-8") as f:
                core_prompt = f.read()
        except FileNotFoundError:
            core_prompt = "コアプロンプトが見つかりません"
    
    try:
        # additional_prompt.txtを読み込み
        additional_prompt_path = os.path.join(backend_dir, "additional_prompt.txt")
        with open(additional_prompt_path, "r", encoding="utf-8") as f:
            additional_prompt = f.read()
    except FileNotFoundError:
        # backendディレクトリになければ、親ディレクトリも試す
        try:
            parent_dir = os.path.dirname(backend_dir)
            additional_prompt_path = os.path.join(parent_dir, "additional_prompt.txt")
            with open(additional_prompt_path, "r", encoding="utf-8") as f:
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
    # 現在のスクリプトの位置から相対パスを計算
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    
    try:
        # additional_prompt.txtを更新
        additional_prompt_path = os.path.join(backend_dir, "additional_prompt.txt")
        
        # ファイルが存在しない場合は親ディレクトリを試す
        if not os.path.exists(additional_prompt_path):
            parent_dir = os.path.dirname(backend_dir)
            additional_prompt_path = os.path.join(parent_dir, "additional_prompt.txt")
        
        with open(additional_prompt_path, "w", encoding="utf-8") as f:
            f.write(request.additional_prompt)
        
        return {"message": "プロンプトが更新されました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プロンプト更新エラー: {str(e)}")