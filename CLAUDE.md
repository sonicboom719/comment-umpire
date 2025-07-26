# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

コメント審判 (Comment Umpire) - YouTube動画のコメントを表示し、AIで詳細分析するStreamlit Webアプリ

## 開発環境とセットアップ

- **プラットフォーム**: Windows (win32)
- **作業ディレクトリ**: C:\Project\comment_umpire2
- **Python**: 3.8以上

### 必要な環境変数 (.envファイル)
```
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## 主要コマンド

```bash
# 依存関係のインストール
pip install -r requirements_streamlit.txt

# Webアプリの起動
streamlit run streamlit_app.py

# テスト実行（推奨）
python run_tests.py

# 直接テスト実行
python test_comment_analysis.py

# pytest使用時
pytest test_comment_analysis.py -v
```

## アーキテクチャ概要

### コア機能
- **YouTube API統合**: コメント取得とバッチ処理（親コメント＋返信を一括取得、初回100件、追加100件ずつ）
- **AI分析エンジン**: OpenAI GPT-4o-miniを使用したコメント分析
- **プロンプトシステム**: core_prompt.txt（基本）+ additional_prompt.txt（カスタム）

### 分析機能
1. **19種類カテゴリー分類**: 皮肉、嘲笑、感想、意見、アドバイス、批判、誹謗中傷、悪口、侮辱、上から目線、論点すり替え、攻撃的、賞賛、感謝、情報提供、問題提起、正論、差別的、共感
2. **グラハムの反論ヒエラルキー**: Lv1(罵倒)〜Lv7(主眼論破)による反論の質の評価
3. **論理的誤謬検出**: 対人論証、権威論証、ストローマン論法、お前だって論法、滑り坂論法
4. **文脈考慮分析**: 返信コメントでは親コメントと前の返信を文脈として分析

### データフロー
1. **YouTube URL入力** → **YouTube Data API** → **コメント取得**
2. **コメント選択** → **AI分析（OpenAI API）** → **結果表示（サイドバー）**
3. **返信展開** → **文脈付きAI分析** → **階層表示**

## ファイル構造と責務

- `streamlit_app.py` - メインWebアプリ（UI、API統合、分析ロジック）
- `core_prompt.txt` - AI分析のコアプロンプト（JSON形式指定、カテゴリー定義）
- `additional_prompt.txt` - カスタム分析指示（ユーザー編集可能）
- `test_comment_analysis.py` - 分析機能の包括的テスト（モック対応）
- `run_tests.py` - テスト実行ランナー（環境変数チェック付き）

## 重要な技術的考慮事項

### API制限とレート制限
- YouTube Data API v3: 日次クォータ10,000ユニット
- OpenAI API: 使用量課金（1分析約0.001〜0.01ドル）
- レート制限対策: エクスポネンシャルバックオフ実装済み

### テスト戦略
- モック機能によりAPIキーなしでのテスト実行可能
- 19カテゴリー × 7ヒエラルキーレベル × 5論理的誤謬の全パターンテスト
- 文脈考慮分析（返信コメント）のテスト

### UIとUX設計
- サイドバー幅400px（分析結果表示用）
- 返信コメントのインデント表示（初回取得時から表示）
- カテゴリーバッジの色分け表示
- リアルタイム分析ボタン（⚖️ 審判）
- 分析中のコメントを青色（#e3f2fd）でハイライト表示

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.