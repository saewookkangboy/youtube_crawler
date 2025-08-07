import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta
from youtube_crawler import YouTubeCrawler
import plotly.express as px
import plotly.graph_objects as go

def show_notifications():
    """Streamlit 세션 상태의 알림들을 표시"""
    if 'notifications' in st.session_state and st.session_state.notifications:
        with st.expander("🔔 실시간 알림", expanded=True):
            for notification in reversed(st.session_state.notifications):
                st.markdown(f"""
                <div style="background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid #2196f3;">
                    <strong>{notification['title']}</strong><br>
                    <small style="color: #666;">{notification['timestamp']}</small><br>
                    {notification['message']}
                </div>
                """, unsafe_allow_html=True)
        
        # 알림 초기화 버튼
        if st.button("알림 지우기", key="clear_notifications"):
            st.session_state.notifications = []
            st.rerun()

# 페이지 설정
st.set_page_config(
    page_title="유튜브 크롤러",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/your-repo/youtube-crawler',
        'Report a bug': "https://github.com/your-repo/youtube-crawler/issues",
        'About': "# 유튜브 크롤러\n\n현대적인 유튜브 데이터 수집 서비스입니다."
    }
)

# Flat Modern CSS 스타일
st.markdown("""
<style>
    /* 전체 페이지 스타일 - Flat Modern */
    .main {
        background: #f8fafc;
        padding: 0;
        min-height: 100vh;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* 스크롤바 스타일 - Flat */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* 헤더 스타일 - Flat Modern */
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1a202c;
        text-align: center;
        margin: 2rem 0;
        letter-spacing: -0.025em;
    }
    
    /* 카드 스타일 - Flat Modern */
    .metric-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        text-align: center;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    /* 버튼 스타일 - Flat Modern */
    .stButton > button {
        background: #3182ce;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: white;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #2c5aa0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
        transform: translateY(-1px);
    }
    
    /* 사이드바 스타일 - Flat Modern */
    .css-1d391kg {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
        text-align: center;
    }
    
    /* 입력 필드 스타일 - Flat Modern */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        background: #ffffff;
        padding: 0.75rem;
        font-size: 0.875rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
        background: #ffffff;
    }
    
    /* 텍스트 영역 스타일 - Flat Modern */
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        background: #ffffff;
        padding: 0.75rem;
        font-size: 0.875rem;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
        background: #ffffff;
    }
    
    /* 숫자 입력 필드 스타일 - Flat Modern */
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        background: #ffffff;
        padding: 0.75rem;
        font-size: 0.875rem;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
        background: #ffffff;
    }
    
    /* 날짜 입력 필드 스타일 - Flat Modern */
    .stDateInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        background: #ffffff;
        padding: 0.75rem;
        font-size: 0.875rem;
    }
    
    .stDateInput > div > div > input:focus {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
        background: #ffffff;
    }
    
    /* 체크박스 스타일 - Flat Modern */
    .stCheckbox > div > div > div {
        border-radius: 4px;
    }
    
    /* 성공 메시지 - Flat Modern */
    .success-message {
        background: #c6f6d5;
        color: #2d3748;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #38a169;
        font-weight: 500;
    }
    
    /* 정보 메시지 - Flat Modern */
    .info-message {
        background: #bee3f8;
        color: #2d3748;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3182ce;
        font-weight: 500;
    }
    
    /* 경고 메시지 - Flat Modern */
    .warning-message {
        background: #fed7d7;
        color: #2d3748;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #e53e3e;
        font-weight: 500;
    }
    
    /* 진행률 바 스타일 - Flat Modern */
    .stProgress > div > div > div > div {
        background: #3182ce;
        border-radius: 4px;
    }
    
    /* 탭 스타일 - Flat Modern */
    .stTabs > div > div > div > div {
        border-radius: 8px 8px 0 0;
        border: 1px solid #e2e8f0;
        background: #f7fafc;
    }
    }
    
    /* 데이터프레임 스타일 */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* 애니메이션 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* 로딩 스피너 */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #4ECDC4;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 검색 설정 영역 스타일 - 반응형 */
    .search-settings-section {
        border: 1px solid #808080;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0 2rem 0;
        background: #fafafa;
        transition: all 0.3s ease;
        min-height: 250px;
        width: 100%;
        box-sizing: border-box;
    }
    
    .search-settings-section:hover {
        background: #f5f5f5;
        border-color: #666666;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* 키워드 경고 메시지 스타일 */
    .keyword-warning {
        background: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 6px;
        border: 1px solid #ffeaa7;
        margin-top: 0.5rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* 고급 설정 확장 영역 */
    .advanced-settings-expanded {
        border: 1px solid #808080;
        border-radius: 6px;
        padding: 1rem;
        margin-top: 0.5rem;
        background: #f8f9fa;
        animation: expandSettings 0.3s ease-out;
    }
    
    @keyframes expandSettings {
        from {
            opacity: 0;
            max-height: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            max-height: 500px;
            transform: translateY(0);
        }
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .search-settings-section {
            padding: 1rem;
            min-height: 200px;
            margin: 0.5rem 0 1rem 0;
        }
        
        .keyword-warning {
            padding: 0.5rem;
            font-size: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Flat Modern 헤더
    st.markdown('<h1 class="main-header fade-in">유튜브 크롤러</h1>', unsafe_allow_html=True)
    
    # 서브타이틀
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem;">유튜브 데이터 수집 및 분석 서비스(since 2025)</p>', unsafe_allow_html=True)
    
    # 실시간 알림 표시
    show_notifications()
    
    # 통합 레이아웃 - 상단에 설정, 하단에 크롤링과 분석을 나란히 배치
    with st.container():
        # 상단 설정 영역
        st.markdown('<h2 style="color: #1a202c; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">⚙️ 크롤링 설정</h2>', unsafe_allow_html=True)
        
        # 검색 설정 영역 - 전체를 테두리로 감싸기
        st.markdown('<div class="search-settings-section">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #4a5568; font-size: 1.1rem; font-weight: 500;">🔍 검색 설정</h3>', unsafe_allow_html=True)
        
        # 키워드 개수 선택
        keyword_count = st.selectbox(
            "키워드 개수",
            options=[1, 2, 3, 4, 5],
            index=2,
            help="수집할 키워드의 개수를 선택하세요"
        )
        
        # 선택된 개수만큼 키워드 입력 필드 생성
        keywords = []
        for i in range(keyword_count):
            keyword = st.text_input(
                f"키워드 {i+1}",
                placeholder=f"키워드 {i+1}을 입력하세요",
                help=f"검색할 키워드 {i+1}을 입력하세요"
            )
            if keyword.strip():
                keywords.append(keyword.strip())
        
        # 키워드 검증 - 테두리 내부에 표시
        if not keywords:
            st.markdown('<div class="keyword-warning">⚠️ 최소 1개의 키워드를 입력해주세요.</div>', unsafe_allow_html=True)
            st.stop()
        st.markdown('</div>', unsafe_allow_html=True)  # search-settings-section 닫기
        
        # 나머지 설정을 2개 컬럼으로 배치
        col2, col3 = st.columns([1, 1])
        
        with col2:
            st.markdown('<h3 style="color: #4a5568; font-size: 1.1rem; font-weight: 500;">📊 수집 설정</h3>', unsafe_allow_html=True)
            
            videos_per_keyword = st.number_input(
                "키워드당 영상 수",
                min_value=1, max_value=50, value=10,
                step=1,
                help="각 키워드당 수집할 영상의 수"
            )
            
            collect_comments = st.checkbox(
                "💬 댓글 수집",
                value=False,
                help="영상 댓글 수집 활성화"
            )
            
            if collect_comments:
                comments_per_video = st.number_input(
                    "영상당 댓글 수",
                    min_value=1, max_value=100, value=20,
                    step=1,
                    help="영상당 수집할 댓글의 수"
                )
            else:
                comments_per_video = 0
        
        with col3:
            st.markdown('<h3 style="color: #4a5568; font-size: 1.1rem; font-weight: 500;">📅 날짜 & 파일</h3>', unsafe_allow_html=True)
            
            # 날짜 필터링 설정
            use_date_filter = st.checkbox(
                "날짜 범위 설정",
                value=False,
                help="업로드 날짜로 영상 필터링"
            )
            
            start_date = None
            end_date = None
            
            if use_date_filter:
                start_date = st.date_input(
                    "시작 날짜",
                    value=datetime.now() - timedelta(days=30),
                    help="검색 시작 날짜"
                )
                end_date = st.date_input(
                    "종료 날짜",
                    value=datetime.now(),
                    help="검색 종료 날짜"
                )
            
            # 파일명 설정
            filename = st.text_input(
                "출력 파일명",
                value="youtube_data.xlsx",
                help="저장할 엑셀 파일명 (확장자 포함)"
            )
            
            # 고급 설정
            with st.expander("🔧 고급 설정"):
                st.markdown('<div class="advanced-settings-expanded">', unsafe_allow_html=True)
                enable_keyword_analysis = st.checkbox(
                    "키워드 분석",
                    value=True,
                    help="댓글에서 키워드 및 감정 분석 수행"
                )
                
                excel_encoding = st.selectbox(
                    "엑셀 인코딩",
                    options=['utf-8-sig', 'utf-8', 'cp949'],
                    index=0,
                    help="엑셀 파일 저장 시 사용할 인코딩"
                )
                
                max_workers = st.slider(
                    "동시 처리 수",
                    min_value=1, max_value=8, value=4,
                    help="동시에 처리할 작업의 수"
                )
                st.markdown('</div>', unsafe_allow_html=True)  # advanced-settings-expanded 닫기
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
    
    # 구분선
    st.markdown("---")
    
    # 크롤링 실행 버튼 (중앙 배치)
    st.markdown('<div style="text-align: center; margin: 2rem 0;">', unsafe_allow_html=True)
    if st.button("🎯 크롤링 시작", type="primary", use_container_width=False, help="설정된 조건으로 크롤링을 시작합니다"):
        if not keywords:
            st.error("❌ 키워드를 입력해주세요.")
            st.stop()
        
        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 크롤링 상태 표시 컨테이너
        status_container = st.container()
        
        # 크롤러 실행
        crawler = None
        try:
            with status_container:
                with st.spinner("🔄 크롤러를 초기화하고 있습니다..."):
                    # 설정 적용
                    config = {
                        'max_workers': max_workers,
                        'enable_keyword_analysis': enable_keyword_analysis,
                        'excel_encoding': excel_encoding,
                        'max_comments_per_video': comments_per_video if collect_comments else 0
                    }
                    
                    crawler = YouTubeCrawler()
                    crawler.update_config(config)
                    st.success("✅ 크롤러 초기화 완료")
            
            # 영상 검색
            with status_container:
                st.info("🔍 영상을 검색하고 있습니다...")
            
            videos = []
            
            for i, keyword in enumerate(keywords):
                progress = (i / len(keywords)) * 0.5  # 50%까지
                progress_bar.progress(progress)
                
                with status_container:
                    st.info(f"🔍 '{keyword}' 검색 중... ({i+1}/{len(keywords)})")
                
                # 날짜 필터링 적용
                start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
                end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None
                
                keyword_videos = crawler.search_videos([keyword], videos_per_keyword, start_dt, end_dt)
                videos.extend(keyword_videos)
                
                with status_container:
                    st.success(f"✅ '{keyword}' 검색 완료 - {len(keyword_videos)}개 영상 발견")
            
            if not videos:
                st.error("❌ 검색된 영상이 없습니다.")
                return
            
            # 댓글 수집
            all_comments = []
            if collect_comments and videos:
                with status_container:
                    st.info("💬 댓글을 수집하고 있습니다...")
                
                for i, video in enumerate(videos):
                    progress = 0.5 + (i / len(videos)) * 0.4  # 50%~90%
                    progress_bar.progress(progress)
                    
                    with status_container:
                        st.info(f"💬 댓글 수집 중... ({i+1}/{len(videos)}) - {video.get('title', 'Unknown')[:30]}...")
                    
                    if video.get('video_id'):
                        try:
                            comments = crawler.get_video_comments(video['video_id'], comments_per_video)
                            all_comments.extend(comments)
                            
                            # 댓글 수집 결과 표시
                            if comments:
                                latest_time = comments[0].get('comment_time', 'N/A') if comments else 'N/A'
                                top_likes = max([comment.get('like_count', 0) for comment in comments])
                                with status_container:
                                    st.success(f"✅ 댓글 수집 완료 - {len(comments)}개 댓글 (최신: {latest_time}, 최고 좋아요: {top_likes})")
                            else:
                                with status_container:
                                    st.warning("⚠️ 댓글 수집 완료 - 수집된 댓글이 없습니다")
                        except Exception as comment_error:
                            error_msg = str(comment_error)
                            with status_container:
                                st.error(f"❌ 댓글 수집 실패 - {video.get('title', 'Unknown')[:30]}... (오류: {error_msg[:100]}...)")
                            
                            # ChromeDriver 재연결 시도
                            if "connection" in error_msg.lower() or "webdriver" in error_msg.lower():
                                try:
                                    with status_container:
                                        st.info("🔄 ChromeDriver 재연결 시도 중...")
                                    crawler.close()
                                    time.sleep(2)
                                    crawler = YouTubeCrawler()
                                    crawler.update_config(config)
                                    with status_container:
                                        st.success("✅ ChromeDriver 재연결 성공")
                                except Exception as reconnect_error:
                                    with status_container:
                                        st.error(f"❌ ChromeDriver 재연결 실패: {str(reconnect_error)}")
                                    break
            
            # 엑셀 저장
            with status_container:
                st.info("💾 데이터를 저장하고 있습니다...")
            progress_bar.progress(0.95)
            
            saved_file = crawler.save_to_excel(videos, all_comments, filename)
            
            progress_bar.progress(1.0)
            with status_container:
                st.success("✅ 크롤링 완료!")
            
            if saved_file:
                st.success(f"🎉 크롤링이 완료되었습니다!")
                
                # 다운로드 버튼
                with open(saved_file, 'rb') as f:
                    st.download_button(
                        label="📥 엑셀 파일 다운로드",
                        data=f.read(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # 세션 상태에 데이터 저장
                st.session_state.videos = videos
                st.session_state.comments = all_comments
                st.session_state.filename = saved_file
                st.session_state.start_date = start_date
                st.session_state.end_date = end_date
                
        except Exception as e:
            error_msg = str(e)
            
            # ChromeDriver 관련 오류인지 확인
            if "chromedriver" in error_msg.lower() or "webdriver" in error_msg.lower():
                st.error("""
                ❌ ChromeDriver 오류가 발생했습니다.
                
                **해결 방법:**
                1. Chrome 브라우저가 설치되어 있는지 확인
                2. ChromeDriver가 올바르게 설치되어 있는지 확인
                3. 브라우저를 다시 시작해보세요
                
                **상세 오류:** """ + error_msg)
            else:
                st.error(f"❌ 오류가 발생했습니다: {error_msg}")
            
            # 디버깅 정보 표시
            with st.expander("🔧 디버깅 정보"):
                st.code(f"""
                오류 유형: {type(e).__name__}
                오류 메시지: {error_msg}
                ChromeDriver 경로: /opt/homebrew/bin/chromedriver
                """)
        finally:
            if crawler:
                try:
                    crawler.close()
                except:
                    pass
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 구분선
    st.markdown("---")
    
    # 결과 및 분석 영역 - 크롤링과 분석을 나란히 배치
    if 'videos' in st.session_state:
        st.markdown('<h2 style="color: #1a202c; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">📊 크롤링 결과 & 분석</h2>', unsafe_allow_html=True)
        
        videos = st.session_state.videos
        comments = st.session_state.get('comments', [])
        
        # 상단 메트릭 카드들
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="text-align: center;">
                    <h3 style="color: #FF6B6B; font-size: 2rem; margin: 0;">{len(videos)}</h3>
                    <p style="color: #666; margin: 0;">수집된 영상</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="text-align: center;">
                    <h3 style="color: #4ECDC4; font-size: 2rem; margin: 0;">{len(comments)}</h3>
                    <p style="color: #666; margin: 0;">수집된 댓글</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            unique_channels = len(set([video.get('channel_name', 'Unknown') for video in videos]))
            st.markdown(f"""
            <div class="metric-card">
                <div style="text-align: center;">
                    <h3 style="color: #FFD93D; font-size: 2rem; margin: 0;">{unique_channels}</h3>
                    <p style="color: #666; margin: 0;">채널 수</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if 'start_date' in st.session_state and 'end_date' in st.session_state:
                start_dt = st.session_state.start_date
                end_dt = st.session_state.end_date
                if start_dt and end_dt:
                    period_text = f"{start_dt.strftime('%m/%d')}~{end_dt.strftime('%m/%d')}"
                else:
                    period_text = "전체 기간"
            else:
                period_text = "전체 기간"
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="text-align: center;">
                    <h3 style="color: #A8E6CF; font-size: 2rem; margin: 0;">📅</h3>
                    <p style="color: #666; margin: 0;">{period_text}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 크롤링 결과와 분석을 나란히 배치
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.markdown('<h3 style="color: #1a202c; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">📋 수집된 데이터</h3>', unsafe_allow_html=True)
            
            # 탭 생성
            tab1, tab2 = st.tabs(["🎥 영상 목록", "💬 댓글 목록"])
            
            with tab1:
                if videos:
                    df_videos = pd.DataFrame(videos)
                    st.dataframe(df_videos, use_container_width=True)
                    
                    # CSV 다운로드
                    csv = df_videos.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 영상 데이터 CSV 다운로드",
                        data=csv,
                        file_name="videos.csv",
                        mime="text/csv"
                    )
            
            with tab2:
                if comments:
                    df_comments = pd.DataFrame(comments)
                    st.dataframe(df_comments, use_container_width=True)
                    
                    # CSV 다운로드
                    csv = df_comments.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 댓글 데이터 CSV 다운로드",
                        data=csv,
                        file_name="comments.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("💬 수집된 댓글이 없습니다.")
        
        with col_right:
            st.markdown('<h3 style="color: #1a202c; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">📈 데이터 분석</h3>', unsafe_allow_html=True)
            
            if videos:
                # 키워드별 영상 수
                keyword_counts = {}
                for video in videos:
                    keyword = video.get('keyword', 'Unknown')
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
                
                st.subheader("🔍 키워드별 영상 수")
                fig = px.bar(
                    x=list(keyword_counts.keys()),
                    y=list(keyword_counts.values()),
                    title="키워드별 수집된 영상 수",
                    color=list(keyword_counts.values()),
                    color_continuous_scale='viridis'
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # 채널별 영상 수
                channel_counts = {}
                for video in videos:
                    channel = video.get('channel_name', 'Unknown')
                    channel_counts[channel] = channel_counts.get(channel, 0) + 1
                
                # 상위 5개 채널만 표시
                top_channels = sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                st.subheader("🏆 인기 채널 TOP 5")
                fig = px.bar(
                    x=[channel for channel, count in top_channels],
                    y=[count for channel, count in top_channels],
                    title="상위 5개 채널별 영상 수",
                    color=[count for channel, count in top_channels],
                    color_continuous_scale='plasma'
                )
                fig.update_layout(height=300)
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
                
                # 키워드별 평균 조회수 (추정)
                st.subheader("📊 키워드별 인기도")
                keyword_views = {}
                for video in videos:
                    keyword = video.get('keyword', 'Unknown')
                    view_text = video.get('view_count', '0')
                    
                    # 조회수 텍스트를 숫자로 변환
                    try:
                        if 'M' in view_text:
                            views = float(view_text.replace('M', '')) * 1000000
                        elif 'K' in view_text:
                            views = float(view_text.replace('K', '')) * 1000
                        else:
                            views = float(view_text.replace(',', ''))
                        
                        if keyword not in keyword_views:
                            keyword_views[keyword] = []
                        keyword_views[keyword].append(views)
                    except:
                        continue
                
                if keyword_views:
                    avg_views = {k: sum(v)/len(v) for k, v in keyword_views.items()}
                    fig = px.bar(
                        x=list(avg_views.keys()),
                        y=list(avg_views.values()),
                        title="키워드별 평균 조회수",
                        color=list(avg_views.values()),
                        color_continuous_scale='inferno'
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
    
    # 데이터가 없을 때 안내 메시지
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: #f8fafc; border-radius: 10px; margin: 2rem 0;">
            <h3 style="color: #4a5568; margin-bottom: 1rem;">🚀 크롤링을 시작해보세요!</h3>
            <p style="color: #666; margin-bottom: 2rem;">위의 설정을 완료하고 크롤링 시작 버튼을 눌러 데이터를 수집하세요.</p>
            <div style="display: flex; justify-content: center; gap: 1rem;">
                <div style="background: #4ECDC4; color: white; padding: 0.5rem 1rem; border-radius: 5px; font-size: 0.9rem;">🔍 영상 검색</div>
                <div style="background: #FF6B6B; color: white; padding: 0.5rem 1rem; border-radius: 5px; font-size: 0.9rem;">💬 댓글 수집</div>
                <div style="background: #FFD93D; color: white; padding: 0.5rem 1rem; border-radius: 5px; font-size: 0.9rem;">📊 데이터 분석</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 