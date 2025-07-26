# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

コメント審判 (Comment Umpire) - YouTube動画のコメントを表示し、AIで詳細分析するStreamlit Webアプリ

## 開発環境

- プラットフォーム: Windows (win32)
- 作業ディレクトリ: C:\Project\comment_umpire
- Python 3.8以上のプロジェクト

## 主要コマンド

```bash
# 依存関係のインストール
pip install -r requirements_streamlit.txt

# Webアプリの起動
streamlit run streamlit_app.py

# テスト実行
python run_tests.py
```

## プロジェクト構造

- `streamlit_app.py` - メインのWebアプリケーション
- `core_prompt.txt` - AI分析の基本プロンプト定義
- `additional_prompt.txt` - ユーザーカスタマイズ用プロンプト
- `test_comment_analysis.py` - テストコード
- `run_tests.py` - テスト実行スクリプト

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