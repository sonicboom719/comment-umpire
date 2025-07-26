import streamlit as st
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from datetime import datetime
import time
from dotenv import load_dotenv
from openai import OpenAI
import json
import streamlit.components.v1 as components

# .envファイルから環境変数を読み込む
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="コメント審判",
    page_icon="💬",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
    /* サイドバーの幅を広げる */
    section[data-testid="stSidebar"] {
        width: 400px !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 400px !important;
    }
    /* メインコンテンツのマージン調整 */
    .main > div {
        padding-right: 1rem;
    }
    .comment-container {
        padding: 10px 0;
        border-bottom: 1px solid #e0e0e0;
    }
    .load-more-container {
        padding: 20px;
        text-align: center;
    }
    .analysis-result {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .category-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .category-皮肉 { background-color: #FF5722; color: white; }
    .category-嘲笑 { background-color: #E91E63; color: white; }
    .category-感想 { background-color: #4CAF50; color: white; }
    .category-意見 { background-color: #2196F3; color: white; }
    .category-アドバイス { background-color: #00BCD4; color: white; }
    .category-批判 { background-color: #FF9800; color: white; }
    .category-誹謗中傷 { background-color: #F44336; color: white; }
    .category-悪口 { background-color: #9C27B0; color: white; }
    .category-侮辱 { background-color: #D32F2F; color: white; }
    .category-上から目線 { background-color: #795548; color: white; }
    .category-論点すり替え { background-color: #607D8B; color: white; }
    .category-攻撃的 { background-color: #B71C1C; color: white; }
    .category-賞賛 { background-color: #8BC34A; color: white; }
    .category-感謝 { background-color: #FFC107; color: black; }
    .category-情報提供 { background-color: #3F51B5; color: white; }
    .category-問題提起 { background-color: #FF5722; color: white; }
    .category-正論 { background-color: #009688; color: white; }
    .category-差別的 { background-color: #212121; color: white; }
    .category-共感 { background-color: #FFB6C1; color: black; }
    
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'comments' not in st.session_state:
    st.session_state.comments = []
if 'next_page_token' not in st.session_state:
    st.session_state.next_page_token = None
if 'video_id' not in st.session_state:
    st.session_state.video_id = None
if 'replies' not in st.session_state:
    st.session_state.replies = {}
if 'loading_replies' not in st.session_state:
    st.session_state.loading_replies = set()
if 'is_loading_more' not in st.session_state:
    st.session_state.is_loading_more = False
if 'displayed_count' not in st.session_state:
    st.session_state.displayed_count = 100
if 'analyzed_comment' not in st.session_state:
    st.session_state.analyzed_comment = None
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False
if 'loading_show_more' not in st.session_state:
    st.session_state.loading_show_more = False
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False
if 'pending_analysis' not in st.session_state:
    st.session_state.pending_analysis = None
if 'video_info' not in st.session_state:
    st.session_state.video_info = None

# YouTube API クライアントの初期化
@st.cache_resource
def get_youtube_client():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        st.error("YouTube API キーが設定されていません。環境変数 YOUTUBE_API_KEY を設定してください。")
        st.stop()
    return build('youtube', 'v3', developerKey=api_key)

# OpenAI クライアントの初期化
@st.cache_resource
def get_openai_client():
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

# YouTube URLからVideo IDを抽出
def extract_video_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]+)',
        r'youtube\.com\/embed\/([^&\n?]+)',
        r'youtube\.com\/v\/([^&\n?]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# コメントを取得
def fetch_comments(video_id, page_token=None, max_results=100):
    youtube = get_youtube_client()
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            pageToken=page_token,
            order="relevance"
        )
        response = request.execute()
        
        comments = []
        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'id': item['id'],
                'text': comment['textDisplay'],
                'text_original': comment['textOriginal'],
                'author': comment['authorDisplayName'],
                'author_image': comment['authorProfileImageUrl'],
                'published_at': comment['publishedAt'],
                'like_count': comment.get('likeCount', 0),
                'reply_count': item['snippet']['totalReplyCount']
            })
        
        return comments, response.get('nextPageToken')
    
    except HttpError as e:
        st.error(f"YouTube API エラー: {e}")
        return [], None

# 返信コメントを取得
def fetch_replies(parent_id):
    youtube = get_youtube_client()
    
    try:
        request = youtube.comments().list(
            part="snippet",
            parentId=parent_id,
            maxResults=100
        )
        response = request.execute()
        
        replies = []
        for item in response.get('items', []):
            comment = item['snippet']
            replies.append({
                'id': item['id'],
                'text': comment['textDisplay'],
                'text_original': comment['textOriginal'],
                'author': comment['authorDisplayName'],
                'author_image': comment['authorProfileImageUrl'],
                'published_at': comment['publishedAt'],
                'like_count': comment.get('likeCount', 0)
            })
        
        return replies
    
    except HttpError as e:
        st.error(f"返信取得エラー: {e}")
        return []

# 日時をフォーマット
def format_datetime(dt_str):
    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    return dt.strftime('%Y/%m/%d %H:%M')

# 動画情報を取得
def fetch_video_info(video_id):
    youtube = get_youtube_client()
    
    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        
        if response.get('items'):
            video = response['items'][0]['snippet']
            return {
                'title': video['title'],
                'channel_title': video['channelTitle'],
                'channel_id': video['channelId'],
                'published_at': video['publishedAt'],
                'thumbnail': video['thumbnails']['medium']['url']
            }
        return None
    
    except HttpError as e:
        st.error(f"動画情報取得エラー: {e}")
        return None

# チャンネル情報を取得
def fetch_channel_info(channel_id):
    youtube = get_youtube_client()
    
    try:
        request = youtube.channels().list(
            part="snippet",
            id=channel_id
        )
        response = request.execute()
        
        if response.get('items'):
            channel = response['items'][0]['snippet']
            return {
                'profile_image': channel['thumbnails']['default']['url']
            }
        return None
    
    except HttpError as e:
        st.error(f"チャンネル情報取得エラー: {e}")
        return None

# コアプロンプトを読み込む関数
def load_core_prompt():
    try:
        with open('core_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        st.error("core_prompt.txtファイルが見つかりません。")
        return ""
    except Exception as e:
        st.error(f"コアプロンプトファイルの読み込みエラー: {e}")
        return ""

# 追加プロンプトを読み込む関数
def load_additional_prompt():
    try:
        with open('additional_prompt.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # コメント行（#で始まる行）と空行を除去
        additional_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                additional_lines.append(line)
        
        return '\n'.join(additional_lines) if additional_lines else ""
    except FileNotFoundError:
        return ""
    except Exception as e:
        st.warning(f"追加プロンプトファイルの読み込みエラー: {e}")
        return ""

# 単一のコメントを分析
def analyze_single_comment(comment_text, context_comments=None):
    client = get_openai_client()
    if not client:
        return None
    
    # コアプロンプトを読み込み
    core_prompt = load_core_prompt()
    if not core_prompt:
        return None
    
    # 追加プロンプトを読み込み
    additional_prompt = load_additional_prompt()
    additional_section = f"\n\n【追加の分析指示】\n{additional_prompt}" if additional_prompt else ""
    
    # 文脈情報を構築
    context_section = ""
    if context_comments:
        context_section = "\n\n【文脈情報】\n以下は会話の流れです：\n"
        for i, ctx_comment in enumerate(context_comments):
            context_section += f"{i+1}. {ctx_comment['author']}: {ctx_comment['text_original']}\n"
        context_section += "\n分析対象は最後のコメントです。会話の流れを考慮して分析してください。\n"
    
    # プロンプトを構築（テンプレート文字列を使用）
    prompt = core_prompt.format(
        context_section=context_section,
        comment_text=comment_text,
        additional_section=additional_section
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "与えられたコメントを分析し、指定された形式の有効なJSONのみを返してください。categoryは該当するものを複数選択可能です（配列で返してください）。「草」「w」「笑」等が含まれる場合、文脈に応じて「嘲笑」（馬鹿にする意図）または「感想」（純粋に面白がる）を判定してください。「侮辱」は相手を見下したり軽蔑する表現、「上から目線」は偉そうな態度や高圧的な物言い、「論点すり替え」は本来の議題から話を逸らす行為、「攻撃的」は敵意や攻撃性を含む表現、「賞賛」は称賛や褒める表現、「感謝」は感謝の気持ちを表す表現、「情報提供」は新しい情報や知識を提供する内容、「問題提起」は問題点や課題を指摘する内容、「正論」は論理的で正当性のある主張、「差別的」は特定の属性に基づく偏見や差別的表現、「共感」は他者の気持ちや状況に対する理解や同調を示す表現を指します。例えば、皮肉を込めた感想の場合は[\"皮肉\", \"感想\"]のように複数を選択してください。explanationには、具体的にコメントのどの部分がなぜそのカテゴリーに分類されたのか、一般の人にも分かりやすい日本語で説明してください。技術的な用語（JSON、true/false等）は使わないでください。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        return json.loads(content)
        
    except Exception as e:
        st.error(f"分析エラー: {e}")
        return None

# コメントを表示
def display_comment(comment, is_reply=False, parent_comment=None, previous_replies=None):
    col1, col2 = st.columns([1, 20])
    
    with col1:
        st.image(comment['author_image'], width=40)
    
    with col2:
        # ヘッダー情報
        header_html = f"""
        <div style="margin-bottom: 5px;">
            <strong>{comment['author']}</strong>
            <span style="color: #666; font-size: 0.9em;">
                {format_datetime(comment['published_at'])}
            </span>
            <span style="color: #065fd4; font-size: 0.9em;">
                👍 {comment['like_count']}
            </span>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        
        # コメント本文
        st.markdown(comment['text'], unsafe_allow_html=True)
        
        # ボタンコンテナ
        button_container = st.container()
        with button_container:
            # 審判ボタンと返信ボタンを配置
            if not is_reply and comment['reply_count'] > 0:
                # 返信がある場合は両方のボタンを表示
                col1, col2, col3 = st.columns([1, 2, 10])
                with col1:
                    if st.button("⚖️ 審判", key=f"judge_{comment['id']}", help="AIでコメントを分析"):
                        # 前回の結果をクリアし、保留中の分析を設定
                        st.session_state.analyzed_comment = None
                        st.session_state.analyzing = False
                        st.session_state.pending_analysis = {
                            'comment': comment,
                            'context_comments': None  # 親コメントには文脈なし
                        }
                        st.rerun()
                
                with col2:
                    if comment['id'] in st.session_state.replies:
                        # 返信を隠すボタン
                        if st.button("▼ 返信を隠す", key=f"reply_btn_{comment['id']}"):
                            del st.session_state.replies[comment['id']]
                    else:
                        # 返信を表示するボタン
                        reply_text = f"▶ {comment['reply_count']}件の返信"
                        if st.button(reply_text, key=f"reply_btn_{comment['id']}"):
                            st.session_state.loading_replies.add(comment['id'])
                            st.rerun()
            else:
                # 返信がない場合は審判ボタンのみ
                col1, col2 = st.columns([1, 12])
                with col1:
                    if st.button("⚖️ 審判", key=f"judge_{comment['id']}", help="AIでコメントを分析"):
                        # 返信コメントの場合は文脈情報を構築
                        context_comments = None
                        if is_reply and parent_comment:
                            context_comments = [parent_comment]  # 親コメントを最初に追加
                            if previous_replies:
                                context_comments.extend(previous_replies)  # それまでの返信を追加
                        
                        # 前回の結果をクリアし、保留中の分析を設定
                        st.session_state.analyzed_comment = None
                        st.session_state.analyzing = False
                        st.session_state.pending_analysis = {
                            'comment': comment,
                            'context_comments': context_comments
                        }
                        st.rerun()

# HTMLタグを除去する関数
def remove_html_tags(text):
    """HTMLタグを除去してプレーンテキストに変換"""
    import re
    # <br>タグを改行に変換
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    # その他のHTMLタグを除去
    text = re.sub(r'<[^>]+>', '', text)
    return text

# 分析結果を表示
def display_analysis_result(comment, analysis):
    st.markdown("### 🔍 コメント分析結果")
    
    # 元のコメント表示
    with st.expander("分析対象コメント", expanded=True):
        st.markdown(f"**{comment['author']}** - {format_datetime(comment['published_at'])}")
        # HTMLタグを除去して表示
        clean_text = remove_html_tags(comment['text'])
        st.text(clean_text)
    
    # カテゴリー表示（複数対応・横並び）
    categories = analysis['category']
    if isinstance(categories, list):
        # 複数カテゴリの場合 - 横並びで表示
        category_html = ""
        for category in categories:
            category_html += f'<span class="category-badge category-{category}" style="margin-right: 8px;">{category}</span>'
        st.markdown(category_html, unsafe_allow_html=True)
    else:
        # 単一カテゴリの場合（後方互換性）
        st.markdown(f'<span class="category-badge category-{categories}">{categories}</span>', unsafe_allow_html=True)
    
    # 反論の分析
    if analysis['isCounter']:
        st.markdown("#### 🎯 反論の質（グラハムのヒエラルキー）")
        hierarchy = analysis.get('grahamHierarchy', '該当なし')
        if hierarchy != '該当なし':
            st.info(hierarchy)
    
    # 論理的誤謬（単一の値）
    fallacy = analysis.get('logicalFallacy')
    if fallacy and fallacy != 'null':
        st.markdown("#### ⚠️ 検出された論理的誤謬")
        st.warning(fallacy)
    
    # 主張の妥当性
    validity = analysis.get('validityAssessment')
    if validity and validity != '判断困難':
        st.markdown("#### 📊 主張の妥当性")
        if validity == '高い':
            st.success(f"妥当性: {validity}")
        elif validity == '中程度':
            st.info(f"妥当性: {validity}")
        elif validity == '低い':
            st.error(f"妥当性: {validity}")
        
        # 妥当性の理由
        validity_reason = analysis.get('validityReason')
        if validity_reason:
            st.markdown(f"**評価理由**: {validity_reason}")
    
    # 詳細な説明
    st.markdown("#### 📝 判定理由")
    st.markdown(analysis['explanation'])

# メインアプリ
def main():
    st.title("💬 コメント審判")
    
    # URL入力
    url_container = st.container()
    with url_container:
        col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
        with col1:
            url = st.text_input("URL", placeholder="YouTube URLを入力してください (例: https://www.youtube.com/watch?v=...)", key="url_input", label_visibility="collapsed")
        with col2:
            load_button = st.button("コメントを取得", type="primary")
    
    # 動画情報表示（URL入力ボックスの直下）
    if st.session_state.video_info:
        video_info = st.session_state.video_info
        
        # 動画情報を表示
        col1, col2 = st.columns([1, 20])
        with col1:
            if 'profile_image' in video_info:
                st.image(video_info['profile_image'], width=40)
        with col2:
            st.markdown(f"**{video_info['title']}**")
            st.markdown(f"チャンネル: {video_info['channel_title']}")
    
    # 新しいURLが入力されたら状態をリセット
    if load_button and url:
        video_id = extract_video_id(url)
        if video_id:
            if video_id != st.session_state.video_id:
                st.session_state.comments = []
                st.session_state.next_page_token = None
                st.session_state.replies = {}
                st.session_state.video_id = video_id
                st.session_state.displayed_count = 100
                st.session_state.analyzed_comment = None
                st.session_state.video_info = None
            
            # 動画情報とコメントを取得
            with st.spinner("動画情報とコメントを取得中..."):
                # 動画情報を取得
                video_info = fetch_video_info(video_id)
                if video_info:
                    # チャンネル情報も取得
                    channel_info = fetch_channel_info(video_info['channel_id'])
                    if channel_info:
                        video_info.update(channel_info)
                    st.session_state.video_info = video_info
                
                # コメント取得
                comments, next_token = fetch_comments(video_id)
                st.session_state.comments = comments
                st.session_state.next_page_token = next_token
                
                # 状態更新後に再描画を強制実行
                st.rerun()
        else:
            st.error("有効なYouTube URLを入力してください")
    
    # 保留中の分析を開始
    if st.session_state.pending_analysis:
        pending = st.session_state.pending_analysis
        st.session_state.pending_analysis = None
        st.session_state.analyzing = True
        st.session_state.analyzed_comment = {
            'comment': pending['comment'],
            'analysis': None,
            'context_comments': pending['context_comments']
        }
        st.rerun()
    
    # 分析処理
    if st.session_state.analyzing and st.session_state.analyzed_comment:
        comment_data = st.session_state.analyzed_comment
        if comment_data['analysis'] is None:
            # サイドバーにローディング表示
            with st.sidebar:
                st.markdown("### 🔍 コメント分析中...")
                with st.spinner("AIがコメントを分析しています..."):
                    # 分析実行（文脈情報を含める）
                    analysis = analyze_single_comment(
                        comment_data['comment']['text_original'], 
                        comment_data.get('context_comments')
                    )
                    st.session_state.analyzed_comment['analysis'] = analysis
                    st.session_state.analyzing = False
                    st.rerun()
    
    # 返信の動的ロード処理
    for comment_id in list(st.session_state.loading_replies):
        if comment_id not in st.session_state.replies:
            replies = fetch_replies(comment_id)
            st.session_state.replies[comment_id] = replies
            st.session_state.loading_replies.remove(comment_id)
            st.rerun()
    
    # メインコンテンツとサイドバー
    main_container = st.container()
    
    # サイドバーに分析結果を表示
    with st.sidebar:
        if st.session_state.analyzing:
            # 分析中の表示（この部分は上の分析処理で表示されるため、ここでは何もしない）
            pass
        elif st.session_state.analyzed_comment and st.session_state.analyzed_comment['analysis']:
            display_analysis_result(
                st.session_state.analyzed_comment['comment'],
                st.session_state.analyzed_comment['analysis']
            )
            
            if st.button("✖️ 閉じる"):
                st.session_state.analyzed_comment = None
                st.rerun()
        else:
            st.markdown("### 📊 コメント分析")
            st.info("コメントの「審判」ボタンをクリックすると、AIによる分析結果がここに表示されます。")
            
            # OpenAI APIキーの確認
            if not get_openai_client():
                st.warning("OpenAI APIキーが設定されていません。分析機能を使用するには環境変数 OPENAI_API_KEY を設定してください。")
    
    # コメント表示
    with main_container:
        if st.session_state.comments:
            st.divider()
            
            # 表示するコメント数を制限
            comments_to_display = st.session_state.comments[:st.session_state.displayed_count]
            
            for comment in comments_to_display:
                # 親コメント表示
                with st.container():
                    display_comment(comment)
                    
                    # 返信表示
                    if comment['id'] in st.session_state.replies:
                        # 返信用のコンテナをインデント
                        reply_container = st.container()
                        with reply_container:
                            # Streamlitのカラム機能を使ってインデント
                            reply_col1, reply_col2 = st.columns([1, 20])  # 1:20の比率でインデント
                            with reply_col1:
                                # 左側は空白（インデント効果）
                                st.markdown('<div style="height: 1px; background: #e0e0e0; width: 100%;"></div>', unsafe_allow_html=True)
                            with reply_col2:
                                # 各返信コメント
                                replies = st.session_state.replies[comment['id']]
                                for i, reply in enumerate(replies):
                                    # それまでの返信コメントを文脈として渡す
                                    previous_replies = replies[:i] if i > 0 else None
                                    display_comment(reply, is_reply=True, parent_comment=comment, previous_replies=previous_replies)
                                    if reply != replies[-1]:  # 最後以外に小さい区切り
                                        st.markdown('<hr style="margin: 10px 0; border: none; border-top: 1px solid #f0f0f0;">', unsafe_allow_html=True)
                    
                    st.divider()
            
            # さらに表示するボタン（統合版）
            show_button = (len(st.session_state.comments) > st.session_state.displayed_count or 
                          st.session_state.next_page_token)
            
            if show_button:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("さらに表示", key="unified_load_more", type="primary", use_container_width=True):
                        # ボタンクリック時に即座に処理
                        if len(st.session_state.comments) > st.session_state.displayed_count:
                            # 既に取得済みのコメントを表示
                            st.session_state.displayed_count += 100
                        elif st.session_state.next_page_token:
                            # 新しいコメントを取得
                            new_comments, next_token = fetch_comments(
                                st.session_state.video_id,
                                st.session_state.next_page_token
                            )
                            st.session_state.comments.extend(new_comments)
                            st.session_state.next_page_token = next_token
                            st.session_state.displayed_count += len(new_comments)
            

if __name__ == "__main__":
    main()