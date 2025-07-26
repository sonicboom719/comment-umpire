# Comment Umpire

YouTube動画のコメントを表示・分析するツール集です。

## ツール一覧

1. **Streamlit Webアプリ** - YouTubeコメントを見やすく表示するWebアプリケーション
2. **CLIツール** - コメントを抽出してAIで分析・分類するPython製CLIツール

## 特徴

- YouTube Data API v3を使用したコメント抽出
- OpenAI APIを使用したコメント分析
- 強力なレート制限対策（エクスポネンシャルバックオフ、バッチ処理）
- コメントの感情分類（感想、意見、アドバイス、批判、誹謗中傷、悪口）
- グラハムの反論ピラミッドに基づく反論の質の評価
- 論理的誤謬の検出（対人論証、権威論証、ストローマン論法など）

## プロジェクト構造

```
comment_umpire/
├── streamlit_app.py       # Streamlit Webアプリ
├── requirements_streamlit.txt  # Streamlit用依存関係
├── process_json/          # CLI版（旧python_version）
│   ├── cli.py             # CLIエントリーポイント
│   ├── youtube_api.py     # YouTube API クライアント
│   ├── comment_analyzer.py # コメント分析ロジック
│   ├── config.py          # 設定ファイル
│   ├── comment_types.py   # 型定義
│   ├── requirements.txt   # CLI版依存関係
│   └── README.md          # CLI版の説明
├── .env                   # APIキー設定（要作成）
├── README.md              # このファイル
└── CLAUDE.md              # Claude Code用設定
```

## セットアップ

### 1. APIキーの取得

#### YouTube Data API v3
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択
3. 「APIとサービス」→「ライブラリ」から「YouTube Data API v3」を検索して有効化
4. 「APIとサービス」→「認証情報」でAPIキーを作成

#### OpenAI API
1. [OpenAI Platform](https://platform.openai.com/)にアクセス
2. アカウントを作成またはログイン
3. 「API keys」セクションで新しいAPIキーを作成

### 2. 環境設定

```bash
# .envファイルを作成してAPIキーを設定
# .envファイルに以下を記載：
# YOUTUBE_API_KEY=your_youtube_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here（CLI版で使用）
```

## Streamlit Webアプリの使用方法

### インストール

```bash
# 依存関係のインストール
pip install -r requirements_streamlit.txt

# アプリの起動
streamlit run streamlit_app.py
```

### 機能

- YouTube URLを入力してコメントを取得
- 親コメント50件ずつ表示
- 返信は「返信を表示」ボタンで動的ロード
- 「さらにコメントを読み込む」ボタンで追加の親コメントを取得
- プロフィール画像、いいね数、投稿日時を表示

## CLI版の使用方法

### インストール

```bash
cd process_json

# 依存関係のインストール
pip install -r requirements.txt
```

### コメントの抽出

```bash
# 基本的な使用方法
python cli.py extract [YOUTUBE_URL]

# オプション付き
python cli.py extract [YOUTUBE_URL] -o comments.json --limit 100
```

### コメントの分析

```bash
# 基本的な使用方法
python cli.py analyze comments.json

# オプション付き
python cli.py analyze comments.json -o analysis_result.json --limit 10
```

### 分析結果の表示

```bash
# 基本的な使用方法
python cli.py show analysis_result.json

# フィルタリング
python cli.py show analysis_result.json --category 批判
python cli.py show analysis_result.json --counter-only
python cli.py show analysis_result.json --fallacy 対人論証
```

## レート制限対策

### バッチ処理
- 5件のコメントを1つのAPIリクエストで処理
- API使用量を大幅に削減

### 待機時間
- リクエスト間: 3秒
- バッチ間: 10秒
- エラー時: 30秒から開始し、エクスポネンシャルバックオフで最大5分まで増加

### リトライ機能
- 最大5回まで自動リトライ
- 429エラー（レート制限）を自動的に処理

### 設定の調整

`python_version/config.py`で各種パラメータを調整できます：

```python
'rate_limit': {
    'retry_count': 5,        # リトライ回数
    'batch_size': 5,         # バッチサイズ
    'batch_delay': 10000,    # バッチ間待機時間（ミリ秒）
    'exponential_backoff': {
        'base_wait': 30000,  # 初回待機時間（ミリ秒）
        'max_wait': 300000,  # 最大待機時間（ミリ秒）
        'multiplier': 2      # 増加倍率
    }
}
```

## 出力例

### カテゴリー別分類
```
感想: 45件 (45.0%)
意見: 25件 (25.0%)
アドバイス: 15件 (15.0%)
批判: 10件 (10.0%)
誹謗中傷: 3件 (3.0%)
悪口: 2件 (2.0%)
```

### 反論の階層（グラハムのピラミッド）
```
DH0: 罵倒: 2件
DH1: 人格攻撃: 3件
DH2: 口調への反応: 5件
DH3: 反論: 8件
DH4: 反駁: 4件
DH5: 論破: 2件
DH6: 中心論点の論破: 1件
```

### 論理的誤謬
```
対人論証: 5件
権威論証: 3件
ストローマン論法: 2件
お前だって論法: 1件
滑り坂論法: 1件
```

## 注意事項

- APIの使用量に注意してください（特にOpenAI API）
- 大量のコメントを分析する場合は、`--limit`オプションで制限することを推奨
- レート制限エラーが頻発する場合は、設定ファイルで待機時間を調整してください
- YouTube APIの日次クォータは10,000ユニットです
- OpenAI APIの利用には料金が発生します

## トラブルシューティング

### レート制限エラーが続く場合
1. 設定ファイルでバッチサイズを小さくする（例: 3件）
2. 待機時間を長くする（例: batch_delay を 20000ms に）
3. OpenAI APIの使用量制限を確認する

### コメントが取得できない場合
- 動画のコメントが無効になっていないか確認
- APIキーが正しく設定されているか確認
- YouTube APIのクォータが残っているか確認

### API Error 500の対処法
- 自動リトライ機能により最大5回まで再試行されます
- エラーが続く場合は時間を置いてから再実行してください

## ライセンス

このプロジェクトはMITライセンスで公開されています。