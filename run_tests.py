#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テスト実行用のシンプルなランナー

このスクリプトを実行することで、コメント分析機能のテストを実行できます。
"""

import os
import sys
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# テストの実行
if __name__ == "__main__":
    print("コメント分析機能のテストを開始します...")
    print("=" * 50)
    
    # 環境変数の確認
    if os.getenv('OPENAI_API_KEY'):
        print("[OK] OPENAI_API_KEY が設定されています")
    else:
        print("[WARNING] OPENAI_API_KEY が設定されていません（テストはモックで実行）")
    
    if os.getenv('YOUTUBE_API_KEY'):
        print("[OK] YOUTUBE_API_KEY が設定されています")
    else:
        print("[WARNING] YOUTUBE_API_KEY が設定されていません")
    
    print("=" * 50)
    
    try:
        # テストコードをインポートして実行
        from test_comment_analysis import run_tests
        run_tests()
    except ImportError as e:
        print(f"テストファイルのインポートに失敗しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {e}")
        sys.exit(1)