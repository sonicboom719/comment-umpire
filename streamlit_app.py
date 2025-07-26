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
    page_title="Comment Umpire",
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
    .category-感想 { background-color: #4CAF50; color: white; }
    .category-意見 { background-color: #2196F3; color: white; }
    .category-アドバイス { background-color: #00BCD4; color: white; }
    .category-批判 { background-color: #FF9800; color: white; }
    .category-誹謗中傷 { background-color: #F44336; color: white; }
    .category-悪口 { background-color: #9C27B0; color: white; }
    
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
    st.session_state.displayed_count = 50
if 'analyzed_comment' not in st.session_state:
    st.session_state.analyzed_comment = None
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False
if 'loading_show_more' not in st.session_state:
    st.session_state.loading_show_more = False
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

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
def fetch_comments(video_id, page_token=None, max_results=50):
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

# 単一のコメントを分析
def analyze_single_comment(comment_text):
    client = get_openai_client()
    if not client:
        return None
    
    prompt = f"""以下のYouTubeコメントを分析してください。

コメント: "{comment_text}"

以下の形式でJSONを返してください。
【重要】categoryは必ず以下の6つのうち1つだけを選んでください：
- 感想（動画に対する感想や感動）
- 意見（投稿者の考えや主張への意見）
- アドバイス（建設的な提案や助言）
- 批判（内容への建設的な批判）
- 誹謗中傷（個人攻撃や侮辱）
- 悪口（単純な悪口や罵声）

{{
    "category": "感想|意見|アドバイス|批判|誹謗中傷|悪口",
    "isCounterArgument": true/false,
    "grahamHierarchy": "DH0: 罵倒|DH1: 人格攻撃|DH2: 口調への反応|DH3: 反論|DH4: 反駁|DH5: 論破|DH6: 中心論点の論破|該当なし",
    "logicalFallacies": {{
        "対人論証": true/false,
        "権威論証": true/false,
        "ストローマン論法": true/false,
        "お前だって論法": true/false,
        "滑り坂論法": true/false
    }},
    "explanation": "なぜこのような判定になったのか、詳細な理由を説明してください"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "与えられたコメントを分析し、指定された形式の有効なJSONのみを返してください。explanationには、具体的にコメントのどの部分がなぜそのカテゴリーに分類されたのか、一般の人にも分かりやすい日本語で説明してください。技術的な用語（JSON、true/false等）は使わないでください。"
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
def display_comment(comment, is_reply=False):
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
                        st.session_state.analyzing = True
                        st.session_state.analyzed_comment = {
                            'comment': comment,
                            'analysis': None
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
                        st.session_state.analyzing = True
                        st.session_state.analyzed_comment = {
                            'comment': comment,
                            'analysis': None
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
    
    # カテゴリー表示
    category = analysis['category']
    st.markdown(f'<span class="category-badge category-{category}">{category}</span>', unsafe_allow_html=True)
    
    # 反論の分析
    if analysis['isCounterArgument']:
        st.markdown("#### 🎯 反論の質（グラハムのヒエラルキー）")
        hierarchy = analysis.get('grahamHierarchy', '該当なし')
        if hierarchy != '該当なし':
            st.info(hierarchy)
    
    # 論理的誤謬
    fallacies = analysis['logicalFallacies']
    detected_fallacies = [k for k, v in fallacies.items() if v]
    if detected_fallacies:
        st.markdown("#### ⚠️ 検出された論理的誤謬")
        for fallacy in detected_fallacies:
            st.warning(fallacy)
    
    # 詳細な説明
    st.markdown("#### 📝 判定理由")
    st.markdown(analysis['explanation'])

# メインアプリ
def main():
    st.title("💬 Comment Umpire")
    
    # URL入力
    url_container = st.container()
    with url_container:
        col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
        with col1:
            url = st.text_input("URL", placeholder="YouTube URLを入力してください (例: https://www.youtube.com/watch?v=...)", key="url_input", label_visibility="collapsed")
        with col2:
            load_button = st.button("コメントを取得", type="primary")
    
    # 新しいURLが入力されたら状態をリセット
    if load_button and url:
        video_id = extract_video_id(url)
        if video_id:
            if video_id != st.session_state.video_id:
                st.session_state.comments = []
                st.session_state.next_page_token = None
                st.session_state.replies = {}
                st.session_state.video_id = video_id
                st.session_state.displayed_count = 50
                st.session_state.analyzed_comment = None
            
            # 初回コメント取得
            with st.spinner("コメントを取得中..."):
                comments, next_token = fetch_comments(video_id)
                st.session_state.comments = comments
                st.session_state.next_page_token = next_token
        else:
            st.error("有効なYouTube URLを入力してください")
    
    # 分析処理
    if st.session_state.analyzing and st.session_state.analyzed_comment:
        comment_data = st.session_state.analyzed_comment
        if comment_data['analysis'] is None:
            # サイドバーにローディング表示
            with st.sidebar:
                st.markdown("### 🔍 コメント分析中...")
                with st.spinner("AIがコメントを分析しています..."):
                    # 分析実行
                    analysis = analyze_single_comment(comment_data['comment']['text_original'])
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
        if st.session_state.analyzing and st.session_state.analyzed_comment and st.session_state.analyzed_comment['analysis'] is None:
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
                                for reply in st.session_state.replies[comment['id']]:
                                    with st.container():
                                        st.markdown('<div style="border-left: 3px solid #e0e0e0; padding-left: 15px; margin-bottom: 10px; background-color: #fafafa; padding: 10px; border-radius: 3px;">', unsafe_allow_html=True)
                                        display_comment(reply, is_reply=True)
                                        st.markdown('</div>', unsafe_allow_html=True)
                    
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
                            st.session_state.displayed_count += 50
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