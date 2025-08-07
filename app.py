import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta
from youtube_crawler import YouTubeCrawler
# plotly 대신 streamlit의 기본 차트 기능 사용
PLOTLY_AVAILABLE = False

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

# 2025년 디자인 트렌드 CSS 스타일
st.markdown("""
<style>
    /* 전체 페이지 스타일 - 2025년 트렌드 */
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 0;
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1a202c;
    }
    
    /* 스크롤바 스타일 - 미니멀 */
    ::-webkit-scrollbar {
        width: 4px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 2px;
        backdrop-filter: blur(10px);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 0, 0, 0.3);
    }
    
    /* 헤더 스타일 - 2025년 트렌드 */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a202c 0%, #4a5568 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 3rem 0 2rem 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    /* 카드 스타일 - 글래스모피즘 */
    .metric-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* 버튼 스타일 - 네오모피즘 */
    .stButton > button {
        background: linear-gradient(145deg, #ffffff, #e6e6e6);
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 600;
        color: #1a202c;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 8px 8px 16px rgba(0, 0, 0, 0.1), -8px -8px 16px rgba(255, 255, 255, 0.8);
        width: 100%;
        font-size: 1rem;
        letter-spacing: 0.01em;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 12px 12px 24px rgba(0, 0, 0, 0.15), -12px -12px 24px rgba(255, 255, 255, 0.9);
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: inset 4px 4px 8px rgba(0, 0, 0, 0.1), inset -4px -4px 8px rgba(255, 255, 255, 0.8);
    }
    
    /* 사이드바 스타일 - 글래스모피즘 */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    /* 입력 필드 스타일 - 2025년 트렌드 */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        padding: 1rem 1.25rem;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: rgba(255, 255, 255, 0.95);
        transform: translateY(-1px);
    }
    
    /* 크롤링 진행 과정 스타일 - 인터랙티브 */
    .crawling-progress {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        margin: 1rem 0;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        transition: all 0.3s ease;
        border-left: 4px solid transparent;
    }
    
    .progress-step.active {
        background: rgba(255, 255, 255, 0.2);
        border-left-color: #4ade80;
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(74, 222, 128, 0.3);
    }
    
    .progress-step.completed {
        background: rgba(255, 255, 255, 0.15);
        border-left-color: #10b981;
    }
    
    .progress-step.error {
        background: rgba(239, 68, 68, 0.1);
        border-left-color: #ef4444;
    }
    
    .step-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .step-icon.pending {
        background: rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.7);
    }
    
    .step-icon.active {
        background: #4ade80;
        color: white;
        animation: pulse 2s infinite;
    }
    
    .step-icon.completed {
        background: #10b981;
        color: white;
    }
    
    .step-icon.error {
        background: #ef4444;
        color: white;
    }
    
    .step-content {
        flex: 1;
    }
    
    .step-title {
        font-weight: 600;
        color: white;
        margin-bottom: 0.25rem;
        font-size: 1rem;
    }
    
    .step-description {
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.875rem;
        margin: 0;
    }
    
    .step-details {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
    
    /* 애니메이션 */
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(74, 222, 128, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(74, 222, 128, 0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .progress-step {
        animation: slideIn 0.5s ease-out;
    }
    
    /* 진행률 바 스타일 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4ade80, #10b981, #059669);
        border-radius: 10px;
        height: 8px;
    }
    
    .stProgress > div > div > div {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        height: 8px;
    }
    
    /* 상태 메시지 스타일 */
    .status-message {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #3182ce;
        animation: slideIn 0.3s ease-out;
    }
    
    .status-message.success {
        border-left-color: #10b981;
        background: rgba(16, 185, 129, 0.1);
    }
    
    .status-message.error {
        border-left-color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }
    
    .status-message.warning {
        border-left-color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }
    
    .status-message.info {
        border-left-color: #3182ce;
        background: rgba(49, 130, 206, 0.1);
    }
    
    /* 로딩 스피너 스타일 */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
        margin-right: 0.5rem;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 실시간 업데이트 카운터 */
    .live-counter {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 0.5rem 1rem;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
        color: white;
        animation: slideIn 0.3s ease-out;
    }
    
    .live-counter.primary {
        background: rgba(49, 130, 206, 0.2);
        border: 1px solid rgba(49, 130, 206, 0.3);
    }
    
    .live-counter.success {
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .live-counter.warning {
        background: rgba(245, 158, 11, 0.2);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    }
    
    /* 텍스트 영역 스타일 - 2025년 트렌드 */
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        padding: 1rem 1.25rem;
        font-size: 1rem;
        font-weight: 500;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: rgba(255, 255, 255, 0.95);
        transform: translateY(-1px);
    }
    
    /* 숫자 입력 필드 스타일 - 2025년 트렌드 */
    .stNumberInput > div > div > input {
        border-radius: 12px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        padding: 1rem 1.25rem;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: rgba(255, 255, 255, 0.95);
        transform: translateY(-1px);
    }
    
    /* 날짜 입력 필드 스타일 - 2025년 트렌드 */
    .stDateInput > div > div > input {
        border-radius: 12px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        padding: 1rem 1.25rem;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .stDateInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: rgba(255, 255, 255, 0.95);
        transform: translateY(-1px);
    }
    
    /* 체크박스 스타일 - 2025년 트렌드 */
    .stCheckbox > div > div > div {
        border-radius: 8px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* 성공 메시지 - 2025년 트렌드 */
    .success-message {
        background: rgba(56, 161, 105, 0.1);
        color: #1a202c;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid rgba(56, 161, 105, 0.2);
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    
    /* 정보 메시지 - 2025년 트렌드 */
    .info-message {
        background: rgba(102, 126, 234, 0.1);
        color: #1a202c;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    
    /* 경고 메시지 - 2025년 트렌드 */
    .warning-message {
        background: rgba(229, 62, 62, 0.1);
        color: #1a202c;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid rgba(229, 62, 62, 0.2);
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    
    /* 진행률 바 스타일 - 2025년 트렌드 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* 탭 스타일 - 2025년 트렌드 */
    .stTabs > div > div > div > div {
        border-radius: 12px 12px 0 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
    }
    
    /* 데이터프레임 스타일 - 2025년 트렌드 */
    .dataframe {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
    }
    
    /* 애니메이션 - 2025년 트렌드 */
    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(30px) scale(0.95); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }
    
    @keyframes slideIn {
        from { 
            opacity: 0; 
            transform: translateX(-40px) scale(0.95); 
        }
        to { 
            opacity: 1; 
            transform: translateX(0) scale(1); 
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .fade-in {
        animation: fadeIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .slide-in {
        animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .pulse {
        animation: pulse 3s infinite cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* 로딩 스피너 - 2025년 트렌드 */
    .loading-spinner {
        display: inline-block;
        width: 24px;
        height: 24px;
        border: 3px solid rgba(102, 126, 234, 0.2);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    

    
    /* 반응형 디자인 - 2025년 트렌드 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
            margin: 2rem 0 1.5rem 0;
        }
        
        .metric-card {
            padding: 1.5rem;
            border-radius: 12px;
        }
        
        .stButton > button {
            padding: 0.875rem 1.5rem;
            font-size: 0.95rem;
        }
        
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input {
            padding: 0.875rem 1rem;
            font-size: 0.95rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            font-size: 2rem;
            margin: 1.5rem 0 1rem 0;
        }
        
        .metric-card {
            padding: 1rem;
            border-radius: 10px;
        }
        
        .stButton > button {
            padding: 0.75rem 1.25rem;
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    # 2025년 트렌드 헤더
    st.markdown('<h1 class="main-header fade-in">유튜브 크롤러</h1>', unsafe_allow_html=True)
    
    # 서브타이틀
    st.markdown('<p style="text-align: center; color: #4a5568; font-size: 1.1rem; margin-bottom: 2rem; font-weight: 400;">유튜브 데이터 수집 및 분석 서비스(since 2025)</p>', unsafe_allow_html=True)
    
    # 실시간 알림 표시
    show_notifications()
    
    # 크롤링 진행 중 표시 (세션 상태 확인)
    if hasattr(st.session_state, 'crawling_completed') and not st.session_state.crawling_completed:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; text-align: center;">
            <h3 style="margin: 0 0 0.5rem 0;">🔄 크롤링이 진행 중입니다</h3>
            <p style="margin: 0; opacity: 0.9;">실제 크롤링 및 수집은 계속 진행중입니다. 페이지를 닫아도 백그라운드에서 작업이 계속됩니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 통합 레이아웃 - 상단에 설정, 하단에 크롤링과 분석을 나란히 배치
    with st.container():
        # 상단 설정 영역
        st.markdown('<h2 style="color: #1a202c; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">크롤링 설정</h2>', unsafe_allow_html=True)
        
        # 설정을 3개 컬럼으로 배치
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown('<h3 style="color: #4a5568; font-size: 1.1rem; font-weight: 500;">검색 설정</h3>', unsafe_allow_html=True)
            
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
            
            # 키워드 검증
            if not keywords:
                st.warning("⚠️ 최소 1개의 키워드를 입력해주세요.")
                st.stop()
        
        with col2:
            st.markdown('<h3 style="color: #4a5568; font-size: 1.1rem; font-weight: 500;">수집 설정</h3>', unsafe_allow_html=True)
            
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
            st.markdown('<h3 style="color: #4a5568; font-size: 1.1rem; font-weight: 500;">날짜 & 파일</h3>', unsafe_allow_html=True)
            
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
            with st.expander("고급 설정"):
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
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
    
    # 구분선
    st.markdown("---")
    
    # 크롤링 실행 버튼 (중앙 배치)
    st.markdown('<div style="text-align: center; margin: 2rem 0;">', unsafe_allow_html=True)
    if st.button("🎯 크롤링 시작", type="primary", use_container_width=False, help="설정된 조건으로 크롤링을 시작합니다"):
        # 크롤링 시작 시 세션 상태 초기화
        st.session_state.crawling_completed = False
        st.session_state.crawling_logs = []
        
        if not keywords:
            st.error("❌ 키워드를 입력해주세요.")
            st.stop()
        
        # 진행 상황 표시
        progress_bar = st.progress(0)
        
        # 실시간 로그 표시 영역
        log_container = st.container()
        
        # 크롤링 상태 표시 컨테이너
        status_container = st.container()
        
        # 실시간 통계 컨테이너
        stats_container = st.container()
        
        # 진행 단계별 상태 표시
        step_container = st.container()
        
        # 실시간 로그 메시지 저장
        if 'crawling_logs' not in st.session_state:
            st.session_state.crawling_logs = []
        
        def add_log(message, log_type="info"):
            """로그 메시지 추가"""
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = {
                'timestamp': timestamp,
                'message': message,
                'type': log_type
            }
            st.session_state.crawling_logs.append(log_entry)
            
            # 최근 20개 로그만 유지
            if len(st.session_state.crawling_logs) > 20:
                st.session_state.crawling_logs = st.session_state.crawling_logs[-20:]
        
        # 크롤러 실행
        crawler = None
        try:
            # 단계 1: 크롤러 초기화
            with step_container:
                st.markdown('<div style="background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea;">', unsafe_allow_html=True)
                st.markdown("🔬 **1단계: 크롤러 초기화 중...**", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with status_container:
                with st.spinner("🔬 크롤러를 초기화하고 있습니다..."):
                    add_log("🔬 크롤러 초기화 시작", "info")
                    
                    # 설정 적용
                    config = {
                        'max_workers': max_workers,
                        'enable_keyword_analysis': enable_keyword_analysis,
                        'excel_encoding': excel_encoding,
                        'max_comments_per_video': comments_per_video if collect_comments else 0
                    }
                    
                    crawler = YouTubeCrawler()
                    crawler.update_config(config)
                    
                    add_log("✅ 크롤러 초기화 완료", "success")
                    st.success("✅ 크롤러 초기화 완료")
            
            progress_bar.progress(0.1)
            
            # 단계 2: 영상 검색
            with step_container:
                st.markdown('<div style="background: rgba(56, 161, 105, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #38a169;">', unsafe_allow_html=True)
                st.markdown("🔍 **2단계: 영상 검색 중...**", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with status_container:
                add_log("🔍 영상 검색 시작", "info")
                st.info("🔍 영상을 검색하고 있습니다...")
            
            videos = []
            
            for i, keyword in enumerate(keywords):
                progress = 0.1 + (i / len(keywords)) * 0.4  # 10%~50%
                progress_bar.progress(progress)
                
                # 인터랙티브 진행 단계 표시
                with status_container:
                    st.info(f"🔍 '{keyword}' 검색 중... ({i+1}/{len(keywords)})")
                
                # 날짜 필터링 적용
                start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
                end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None
                
                keyword_videos = crawler.search_videos([keyword], videos_per_keyword, start_dt, end_dt)
                videos.extend(keyword_videos)
                
                # 실시간 통계 업데이트
                with stats_container:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="live-counter primary">
                            <span class="loading-spinner"></span>수집된 영상: {len(videos)}개
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="live-counter success">
                            완료된 키워드: {i+1}/{len(keywords)}
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="live-counter warning">
                            진행률: {int(progress * 100)}%
                        </div>
                        """, unsafe_allow_html=True)
                
                with status_container:
                    st.success(f"✅ '{keyword}' 검색 완료 - {len(keyword_videos)}개 영상 발견")
            
            if not videos:
                add_log("❌ 검색된 영상이 없습니다.", "error")
                st.error("❌ 검색된 영상이 없습니다.")
                return
            
            # 단계 3: 댓글 수집 (선택사항)
            all_comments = []
            if collect_comments and videos:
                with step_container:
                    st.markdown('<div style="background: rgba(245, 158, 11, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b;">', unsafe_allow_html=True)
                    st.markdown("💬 **3단계: 댓글 수집 중...**", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with status_container:
                    st.info("💬 댓글을 수집하고 있습니다...")
                
                for i, video in enumerate(videos):
                    progress = 0.5 + (i / len(videos)) * 0.4  # 50%~90%
                    progress_bar.progress(progress)
                    
                    # 인터랙티브 댓글 수집 진행 단계
                    with status_container:
                        st.info(f"💬 댓글 수집 중... ({i+1}/{len(videos)}) - {video.get('title', 'Unknown')[:30]}...")
                    
                    if video.get('video_id'):
                        try:
                            comments = crawler.get_video_comments(video['video_id'], comments_per_video)
                            all_comments.extend(comments)
                            
                            # 실시간 댓글 통계 업데이트
                            with stats_container:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown(f"""
                                    <div class="live-counter primary">
                                        수집된 영상: {len(videos)}개
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    st.markdown(f"""
                                    <div class="live-counter success">
                                        수집된 댓글: {len(all_comments)}개
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col3:
                                    st.markdown(f"""
                                    <div class="live-counter warning">
                                        진행률: {int(progress * 100)}%
                                    </div>
                                    """, unsafe_allow_html=True)
                            
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
                                        add_log("🔄 ChromeDriver 재연결 시도 중...", "info")
                                        st.info("🔄 ChromeDriver 재연결 시도 중...")
                                    crawler.close()
                                    time.sleep(2)
                                    crawler = YouTubeCrawler()
                                    crawler.update_config(config)
                                    with status_container:
                                        add_log("✅ ChromeDriver 재연결 성공", "success")
                                        st.success("✅ ChromeDriver 재연결 성공")
                                except Exception as reconnect_error:
                                    with status_container:
                                        add_log(f"❌ ChromeDriver 재연결 실패: {str(reconnect_error)}", "error")
                                        st.error(f"❌ ChromeDriver 재연결 실패: {str(reconnect_error)}")
                                    break
            
            # 단계 4: 데이터 저장
            with step_container:
                st.markdown('<div style="background: rgba(236, 72, 153, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #ec4899;">', unsafe_allow_html=True)
                st.markdown("💾 **4단계: 데이터 저장 중...**", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with status_container:
                add_log("💾 데이터 저장 시작", "info")
                st.info("💾 데이터를 저장하고 있습니다...")
            progress_bar.progress(0.95)
            
            saved_file = crawler.save_to_excel(videos, all_comments, filename)
            
            progress_bar.progress(1.0)
            with status_container:
                st.success("✅ 크롤링 완료!")
            
            if saved_file:
                st.success(f"🎉 크롤링이 완료되었습니다!")
                
                # 다운로드 버튼
                st.download_button(
                    label="📥 엑셀 파일 다운로드",
                    data=excel_buffer.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # CSV 다운로드 버튼도 추가
                if videos:
                    videos_df = pd.DataFrame(videos)
                    csv_videos = videos_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 영상 데이터 CSV 다운로드",
                        data=csv_videos,
                        file_name="videos.csv",
                        mime="text/csv"
                    )
                
                if all_comments:
                    comments_df = pd.DataFrame(all_comments)
                    csv_comments = comments_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 댓글 데이터 CSV 다운로드",
                        data=csv_comments,
                        file_name="comments.csv",
                        mime="text/csv"
                    )
                
            except Exception as excel_error:
                st.error(f"❌ 엑셀 파일 생성 오류: {str(excel_error)}")
                # CSV로 대체
                if videos:
                    videos_df = pd.DataFrame(videos)
                    csv_videos = videos_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 영상 데이터 CSV 다운로드",
                        data=csv_videos,
                        file_name="videos.csv",
                        mime="text/csv"
                    )
                
                if all_comments:
                    comments_df = pd.DataFrame(all_comments)
                    csv_comments = comments_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 댓글 데이터 CSV 다운로드",
                        data=csv_comments,
                        file_name="comments.csv",
                        mime="text/csv"
                    )
                
                # 세션 상태에 데이터 저장
                st.session_state.videos = videos
                st.session_state.comments = all_comments
                st.session_state.filename = filename
                st.session_state.start_date = start_date
                st.session_state.end_date = end_date
                
                # 크롤링 완료 상태 저장
                st.session_state.crawling_completed = True
                
        except Exception as e:
            error_msg = str(e)
            add_log(f"❌ 크롤링 중 오류 발생: {error_msg[:100]}...", "error")
            
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
                # Streamlit 기본 차트 사용
                chart_data = pd.DataFrame({
                    '키워드': list(keyword_counts.keys()),
                    '영상 수': list(keyword_counts.values())
                })
                st.bar_chart(chart_data.set_index('키워드'))
                
                # 상세 정보도 표시
                st.write("**상세 정보:**")
                for keyword, count in keyword_counts.items():
                    st.write(f"- {keyword}: {count}개")
                
                # 채널별 영상 수
                channel_counts = {}
                for video in videos:
                    channel = video.get('channel_name', 'Unknown')
                    channel_counts[channel] = channel_counts.get(channel, 0) + 1
                
                # 상위 5개 채널만 표시
                top_channels = sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                st.subheader("🏆 인기 채널 TOP 5")
                # Streamlit 기본 차트 사용
                channel_data = pd.DataFrame({
                    '채널명': [channel for channel, count in top_channels],
                    '영상 수': [count for channel, count in top_channels]
                })
                st.bar_chart(channel_data.set_index('채널명'))
                
                # 상세 정보도 표시
                st.write("**상세 정보:**")
                for i, (channel, count) in enumerate(top_channels, 1):
                    st.write(f"{i}. {channel}: {count}개")
                
                # 키워드별 인지도 분석 (개선된 버전)
                st.subheader("📊 키워드별 인지도")
                
                # 키워드별 통계 데이터 수집
                keyword_stats = {}
                for video in videos:
                    keyword = video.get('keyword', 'Unknown')
                    view_text = video.get('view_count', '0')
                    formatted_date = video.get('formatted_upload_date', 'N/A')
                    
                    if keyword not in keyword_stats:
                        keyword_stats[keyword] = {
                            'total_views': 0,
                            'video_count': 0,
                            'avg_views': 0,
                            'recent_videos': 0,  # 최근 30일 내 영상
                            'view_data': []
                        }
                    
                    # 조회수 변환
                    try:
                        if 'M' in view_text:
                            views = float(view_text.replace('M', '')) * 1000000
                        elif 'K' in view_text:
                            views = float(view_text.replace('K', '')) * 1000
                        else:
                            views = float(view_text.replace(',', ''))
                        
                        keyword_stats[keyword]['total_views'] += views
                        keyword_stats[keyword]['video_count'] += 1
                        keyword_stats[keyword]['view_data'].append(views)
                        
                        # 최근 영상 체크 (발행일이 있는 경우)
                        if formatted_date != 'N/A':
                            try:
                                video_date = datetime.strptime(formatted_date, '%Y.%m.%d')
                                days_diff = (datetime.now() - video_date).days
                                if days_diff <= 30:
                                    keyword_stats[keyword]['recent_videos'] += 1
                            except:
                                pass
                                
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