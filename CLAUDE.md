# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

コメント審判 (Comment Umpire) - YouTube動画のコメントを表示し、AIで詳細分析するFastAPI+React Webアプリケーション

## 開発環境とセットアップ

- **プラットフォーム**: Windows (win32)
- **作業ディレクトリ**: C:\Project\comment_umpire
- **Python**: 3.8以上
- **Node.js**: 18以上

### 必要な環境変数 (backend/.envファイル)
```
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## 主要コマンド

### バックエンド
```bash
cd backend

# 依存関係のインストール
pip install -r requirements.txt

# 開発サーバー起動
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### フロントエンド
```bash
cd frontend

# 依存関係のインストール
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build
```

## アーキテクチャ概要

### 技術スタック
- **バックエンド**: FastAPI, Pydantic, YouTube Data API v3, OpenAI API
- **フロントエンド**: React 18, TypeScript, Styled Components, Zustand, Vite
- **デプロイ**: Render (フロントエンド: Static Site, バックエンド: Web Service)

### コア機能
- **YouTube API統合**: コメント取得（親コメントのみ初回100件、返信は動的取得）
- **AI分析エンジン**: OpenAI GPT-4o-miniを使用したコメント分析
- **審判判定**: safe/outの視覚的判定表示（審判画像付き）
- **抗議機能**: GPT-4oによる審判との対話・再判定システム
- **プロンプトシステム**: backend/core_prompt.txt（基本）+ backend/additional_prompt.txt（カスタム）

### 分析機能
1. **19種類カテゴリー分類**: 皮肉、嘲笑、感想、意見、アドバイス、批判、誹謗中傷、悪口、侮辱、上から目線、論点すり替え、攻撃的、賞賛、感謝、情報提供、問題提起、正論、差別的、共感
2. **グラハムの反論ヒエラルキー**: Lv1(罵倒)〜Lv7(主眼論破)による反論の質の評価
3. **論理的誤謬検出**: 対人論証、権威論証、ストローマン論法、お前だって論法、滑り坂論法
4. **セーフ/アウト判定**: コメントの適切性を野球審判スタイルで判定
5. **文脈考慮分析**: 返信コメントでは親コメントと前の返信を文脈として分析

### データフロー
1. **YouTube URL入力** → **YouTube Data API** → **親コメント取得（最大100件）**
2. **返信ボタンクリック** → **返信コメント動的取得**
3. **審判ボタンクリック** → **AI分析（OpenAI API）** → **結果表示（サイドバー）**
4. **抗議ボタンクリック** → **対話モード** → **再判定（必要時）**

## ファイル構造と責務

### バックエンド (backend/)
- `app/main.py` - FastAPIアプリケーションのエントリポイント
- `app/api/` - APIエンドポイント定義
  - `videos.py` - 動画情報とコメント取得
  - `comments.py` - コメント分析と抗議処理
  - `prompts.py` - プロンプト管理
- `app/services/` - ビジネスロジック
  - `youtube_service.py` - YouTube API統合
  - `analysis_service.py` - AI分析と抗議処理（GPT-4o-mini/GPT-4o）
- `app/models/` - Pydanticモデル定義
- `core_prompt.txt` - AI分析のコアプロンプト（JSON形式、safeOrOut判定含む）
- `additional_prompt.txt` - カスタム分析指示

### フロントエンド (frontend/)
- `src/components/` - Reactコンポーネント
  - `Analysis/` - 分析結果表示（UmpireJudgment, ProtestDialog等）
  - `Comments/` - コメント表示（CommentItem, ReplyList等）
  - `Layout/` - レイアウト（Sidebar, Header等）
- `src/hooks/useAppStore.ts` - Zustand状態管理
- `src/services/api.ts` - バックエンドAPI連携
- `public/image/` - 審判画像（safe.png, out.png）

## 重要な技術的考慮事項

### API制限とレート制限
- YouTube Data API v3: 日次クォータ10,000ユニット
- OpenAI API: 使用量課金
  - GPT-4o-mini: 1分析約0.001〜0.01ドル
  - GPT-4o: 抗議処理により高コスト
- レート制限対策: エクスポネンシャルバックオフ実装済み

### UIとUX設計
- サイドバー幅400px（分析結果表示用）
- 返信コメントの動的読み込み（ボタンクリックで取得）
- カテゴリーバッジの色分け表示
- リアルタイム分析ボタン（⚖️ 審判）
- 分析中のコメントを青色（#e3f2fd）でハイライト表示
- セーフ/アウト判定の視覚的表示（審判画像付き）
- 抗議ダイアログでの対話型インタラクション

### デプロイ設定（Render）
- フロントエンド: Static Site
  - Build Command: `npm run build`
  - Publish Directory: `dist`
- バックエンド: Web Service
  - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
  - 環境変数設定必須

### 注意事項
- プロンプトファイルは`backend/`ディレクトリに配置
- 画像ファイルは`frontend/public/image/`に配置
- ブランチ名に注意（ローカル: master, リモート: main）

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.