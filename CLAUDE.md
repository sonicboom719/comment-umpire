# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

YouTube Comment Analyzer - YouTube動画のコメントを抽出してAIで分析するPython製CLIツール

## 開発環境

- プラットフォーム: Windows (win32)
- 作業ディレクトリ: C:\Project\ArgumentChecker
- Python 3.8以上のプロジェクト

## 主要コマンド

```bash
# Python版のディレクトリに移動
cd python_version

# 依存関係のインストール
pip install -r requirements.txt

# コメント抽出
python cli.py extract [YOUTUBE_URL]

# コメント分析
python cli.py analyze comments.json --limit 10

# テスト実行
python -m pytest
```

## プロジェクト構造

- `python_version/` - Python実装のディレクトリ
  - `cli.py` - CLIエントリーポイント
  - `youtube_api.py` - YouTube Data API v3のクライアント実装
  - `comment_analyzer.py` - OpenAI APIを使用したコメント分析
  - `config.py` - 設定ファイル（レート制限対策など）
  - `types.py` - 型定義（dataclass）

## 重要な注意事項

- YouTube Data API v3のAPIキーが必要（環境変数: YOUTUBE_API_KEY）
- OpenAI APIキーが必要（環境変数: OPENAI_API_KEY）
- APIのクォータ制限とレート制限に注意
- エラーハンドリングは日本語で実装
- バッチ処理とエクスポネンシャルバックオフでレート制限対策済み

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.