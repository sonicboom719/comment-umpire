# コメント審判 (Comment Umpire) - Python+React版

YouTube動画のコメントを表示・分析するモダンなWebアプリケーション。AIを使用してコメントを詳細に分析し、19種類のカテゴリーに分類します。

## 技術スタック

### バックエンド
- **FastAPI** - 高性能なPython Webフレームワーク
- **Pydantic** - データバリデーション
- **YouTube Data API v3** - コメント取得
- **OpenAI API** - AI分析（GPT-4o-mini）

### フロントエンド
- **React 18** - UIライブラリ
- **TypeScript** - 型安全性
- **Styled Components** - CSS-in-JS
- **Zustand** - 軽量状態管理
- **React Query** - サーバー状態管理
- **Vite** - ビルドツール

## セットアップ

### 1. リポジトリのクローンと環境設定

```bash
# .envファイルを作成
cp backend/.env.example backend/.env

# APIキーを設定（backend/.env）
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. バックエンドの起動

```bash
cd backend

# 依存関係のインストール
pip install -r requirements.txt

# プロンプトファイルを配置（プロジェクトルートから）
# core_prompt.txt と additional_prompt.txt が必要

# 開発サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. フロントエンドの起動

```bash
cd frontend

# 依存関係のインストール
npm install

# 開発サーバー起動
npm run dev
```

### 4. アクセス

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs

## 主要機能

### コメント表示・分析機能
- YouTube Data API v3を使用したコメント抽出（親コメント＋返信を一括取得）
- OpenAI APIを使用したリアルタイムコメント分析
- 動画情報の表示（タイトル、チャンネル名、プロフィール画像）
- 返信コメントのインデント表示と文脈を考慮した分析
- 初回100件（親＋返信含む）、追加100件ずつのコメント表示
- 分析中のコメントをハイライト表示

### AI分析機能
- **19種類のカテゴリー分類**: 皮肉、嘲笑、感想、意見、アドバイス、批判、誹謗中傷、悪口、侮辱、上から目線、論点すり替え、攻撃的、賞賛、感謝、情報提供、問題提起、正論、差別的、共感
- **グラハムの反論ヒエラルキー**: Lv1(罵倒)〜Lv7(主眼論破)による反論の質の評価
- **論理的誤謬の検出**: 対人論証、権威論証、ストローマン論法、お前だって論法、滑り坂論法
- **文脈考慮分析**: 返信コメントでは親コメントと前の返信を文脈として分析
- **複数カテゴリー対応**: 1つのコメントが複数のカテゴリーに該当する場合の処理

## プロジェクト構造

```
comment_umpire2/
├── backend/                    # Python FastAPI バックエンド
│   ├── app/
│   │   ├── main.py            # FastAPI アプリケーション
│   │   ├── models/            # Pydantic データモデル
│   │   ├── services/          # ビジネスロジック
│   │   ├── api/               # API エンドポイント
│   │   └── core/              # 設定・ユーティリティ
│   ├── requirements.txt       # Python依存関係
│   └── .env.example          # 環境変数テンプレート
├── frontend/                   # React フロントエンド
│   ├── src/
│   │   ├── components/        # React コンポーネント
│   │   ├── services/          # API クライアント
│   │   ├── hooks/             # カスタムフック（Zustand）
│   │   ├── types/             # TypeScript 型定義
│   │   ├── styles/            # スタイリング
│   │   └── utils/             # ユーティリティ関数
│   ├── package.json           # Node.js依存関係
│   └── vite.config.ts         # Vite設定
├── core_prompt.txt            # AI分析のコアプロンプト
├── additional_prompt.txt      # AI分析用カスタムプロンプト
└── README.md                  # このファイル
```

## API エンドポイント

### 動画関連
- `POST /api/videos/extract` - YouTube URL から動画情報取得
- `GET /api/videos/{video_id}/comments` - コメント取得（ページネーション）

### コメント関連
- `GET /api/comments/{comment_id}/replies` - 返信コメント取得
- `POST /api/comments/analyze` - コメント分析

### プロンプト管理
- `GET /api/prompts` - プロンプト設定取得
- `PUT /api/prompts` - プロンプト設定更新

### その他
- `GET /api/health` - ヘルスチェック

## 開発コマンド

### バックエンド
```bash
cd backend

# 開発サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 型チェック（mypyがあれば）
mypy app/
```

### フロントエンド
```bash
cd frontend

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# 型チェック
npm run type-check

# Lint
npm run lint
```

## UI/UX特徴

### レイアウト
- **メインレイアウト**: コンテンツエリア + 400px固定サイドバー
- **レスポンシブ**: モバイル対応（サイドバーが下部に移動）

### カラーシステム
- 19種類のカテゴリー専用カラーパレット
- グラハムのヒエラルキーレベル別色分け
- 論理的誤謬の視覚的表示
- 分析中のコメントを青色（#e3f2fd）でハイライト

### インタラクション
- リアルタイム分析ボタン（⚖️ 審判）
- 返信コメントの展開/折りたたみ（初回取得時から表示可能）
- 無限スクロール風の「さらに表示」

## トラブルシューティング

### コメントが取得できない場合
- YouTube APIキーが正しく設定されているか確認
- 動画のコメントが無効になっていないか確認
- APIクォータが残っているか確認

### AI分析が失敗する場合
- OpenAI APIキーが正しく設定されているか確認
- インターネット接続を確認
- OpenAI APIの使用量制限を確認

### 開発サーバーが起動しない場合
- ポート8000（バックエンド）と3000（フロントエンド）が利用可能か確認
- 依存関係が正しくインストールされているか確認

## 注意事項

### API使用料金
- **YouTube Data API v3**: 無料枠あり（日次クォータ: 10,000ユニット）
- **OpenAI API**: 使用量に応じて料金発生（gpt-4o-miniモデル使用）
- AI分析は1回につき約0.001〜0.01ドル程度

### セキュリティ
- APIキーは絶対にGitにコミットしない
- 本番環境では適切な環境変数管理を行う
- CORS設定を本番環境に合わせて調整

## ライセンス

このプロジェクトはMITライセンスで公開されています。