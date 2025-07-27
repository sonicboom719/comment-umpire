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
    import glob
    
    # 現在のワーキングディレクトリを取得
    cwd = os.getcwd()
    
    # デバッグ情報としてファイルを検索
    core_prompt_search = glob.glob("**/core_prompt.txt", recursive=True)
    additional_prompt_search = glob.glob("**/additional_prompt.txt", recursive=True)
    
    debug_info = f"CWD: {cwd}, core_prompt files: {core_prompt_search}, additional_prompt files: {additional_prompt_search}"
    
    # 上位ディレクトリを含めてファイルを探す
    core_prompt_paths = [
        "core_prompt.txt",
        "../core_prompt.txt",
        "../../core_prompt.txt",
        os.path.join(cwd, "core_prompt.txt"),
    ]
    
    # core_prompt_searchからも追加
    if core_prompt_search:
        core_prompt_paths.extend(core_prompt_search)
    
    core_prompt = None
    for path in core_prompt_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                core_prompt = f.read()
                break
        except:
            continue
    
    if core_prompt is None:
        core_prompt = f"コアプロンプトが見つかりません\n{debug_info}"
    
    # additional_prompt.txtも同様に探す
    additional_prompt_paths = [
        "additional_prompt.txt",
        "../additional_prompt.txt",
        "../../additional_prompt.txt",
        os.path.join(cwd, "additional_prompt.txt"),
    ]
    
    if additional_prompt_search:
        additional_prompt_paths.extend(additional_prompt_search)
    
    additional_prompt = None
    for path in additional_prompt_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                additional_prompt = f.read()
                break
        except:
            continue
    
    if additional_prompt is None:
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