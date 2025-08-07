import time
import re
import subprocess
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
# beautifulsoup4는 현재 사용되지 않으므로 제거
import pandas as pd
import requests
from urllib.parse import urlparse, parse_qs
import json
import os
import pickle
import hashlib
from functools import lru_cache
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional, Any, Tuple
import gc
import random
from collections import defaultdict
import numpy as np

# 선택적 임포트 - 설치되지 않은 경우 대체 로직 사용
textblob_available = False
jieba_available = False
konlpy_available = False

try:
    from textblob import TextBlob
    textblob_available = True
except ImportError:
    pass

try:
    import jieba
    jieba_available = True
except ImportError:
    pass

try:
    from konlpy.tag import Okt
    konlpy_available = True
except ImportError:
    pass

# 로깅 설정 강화
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

class RetryManager:
    """재시도 관리 클래스"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        
    def execute_with_retry(self, func, *args, **kwargs):
        """함수를 재시도 로직과 함께 실행"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"시도 {attempt + 1} 실패: {e}. {delay:.2f}초 후 재시도...")
                    time.sleep(delay)
                else:
                    logger.error(f"최대 재시도 횟수 초과: {e}")
                    
        raise last_exception

class CacheManager:
    """캐시 관리 클래스 - 성능 개선"""
    
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self._memory_cache = {}
        self._cache_stats = {'hits': 0, 'misses': 0}
        
    def _get_cache_key(self, data: str) -> str:
        """캐시 키 생성"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 가져오기 - 메모리 캐시 우선"""
        # 메모리 캐시 확인
        if key in self._memory_cache:
            self._cache_stats['hits'] += 1
            return self._memory_cache[key]
            
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            if os.path.exists(cache_file):
                # 캐시 만료 시간 체크 (12시간으로 단축)
                if time.time() - os.path.getmtime(cache_file) < 43200:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                        # 메모리 캐시에 저장
                        self._memory_cache[key] = data
                        self._cache_stats['hits'] += 1
                        return data
                else:
                    os.remove(cache_file)  # 만료된 캐시 삭제
        except Exception as e:
            logger.warning(f"캐시 읽기 오류: {e}")
            
        self._cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, data: Any):
        """캐시에 데이터 저장 - 메모리와 파일 모두"""
        try:
            # 메모리 캐시에 저장
            self._memory_cache[key] = data
            
            # 파일 캐시에 저장
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.warning(f"캐시 저장 오류: {e}")
    
    def clear(self):
        """캐시 전체 삭제"""
        try:
            self._memory_cache.clear()
            for file in os.listdir(self.cache_dir):
                if file.endswith('.pkl'):
                    os.remove(os.path.join(self.cache_dir, file))
            logger.info("캐시가 삭제되었습니다.")
        except Exception as e:
            logger.error(f"캐시 삭제 오류: {e}")
    
    def get_stats(self) -> Dict:
        """캐시 통계 반환"""
        total = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = (self._cache_stats['hits'] / total * 100) if total > 0 else 0
        return {
            'hits': self._cache_stats['hits'],
            'misses': self._cache_stats['misses'],
            'hit_rate': f"{hit_rate:.1f}%",
            'memory_cache_size': len(self._memory_cache)
        }

class ConfigManager:
    """설정 관리 클래스 - 성능 최적화"""
    
    def __init__(self):
        self.config = {
            'max_workers': int(os.getenv('MAX_WORKERS', '6')),  # 워커 수 증가
            'timeout': int(os.getenv('TIMEOUT', '30')),
            'retry_count': int(os.getenv('RETRY_COUNT', '3')),
            'cache_enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            'headless': os.getenv('HEADLESS', 'true').lower() == 'true',
            'scroll_count': int(os.getenv('SCROLL_COUNT', '3')),  # 스크롤 수 감소로 속도 향상
            'wait_time': float(os.getenv('WAIT_TIME', '1.5')),  # 대기 시간 단축
            'max_memory_mb': int(os.getenv('MAX_MEMORY_MB', '4096')),  # 메모리 증가
            'comment_batch_size': int(os.getenv('COMMENT_BATCH_SIZE', '20')),  # 댓글 배치 크기
            'enable_keyword_analysis': os.getenv('ENABLE_KEYWORD_ANALYSIS', 'true').lower() == 'true',
            'max_comments_per_video': int(os.getenv('MAX_COMMENTS_PER_VIDEO', '100')),
            'excel_encoding': os.getenv('EXCEL_ENCODING', 'utf-8-sig'),  # 엑셀 인코딩 설정
        }
    
    def get(self, key: str, default=None):
        """설정값 가져오기"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """설정값 설정"""
        self.config[key] = value
    
    def update(self, new_config: Dict):
        """설정 업데이트"""
        self.config.update(new_config)

class PerformanceMonitor:
    """성능 모니터링 클래스 - 강화된 버전"""
    
    def __init__(self):
        self.timers = {}
        self.memory_usage = []
        self.start_time = time.time()
        self.operation_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        
    def start_timer(self, name: str):
        """타이머 시작"""
        self.timers[name] = time.time()
        self.operation_counts[name] += 1
    
    def end_timer(self, name: str):
        """타이머 종료 및 시간 반환"""
        if name in self.timers:
            elapsed = time.time() - self.timers[name]
            logger.info(f"{name} 실행 시간: {elapsed:.2f}초")
            return elapsed
        return 0
    
    def log_error(self, operation: str, error: Exception):
        """에러 로깅"""
        self.error_counts[operation] += 1
        logger.error(f"{operation} 에러: {error}")
    
    def get_metrics(self) -> Dict:
        """성능 메트릭 반환"""
        total_time = time.time() - self.start_time
        return {
            'total_time': total_time,
            'timers': self.timers.copy(),
            'memory_usage': self.memory_usage,
            'operation_counts': dict(self.operation_counts),
            'error_counts': dict(self.error_counts),
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> Dict:
        """성공률 계산"""
        rates = {}
        for operation in self.operation_counts:
            total = self.operation_counts[operation]
            errors = self.error_counts.get(operation, 0)
            success_rate = ((total - errors) / total * 100) if total > 0 else 100
            rates[operation] = f"{success_rate:.1f}%"
        return rates
    
    def log_memory_usage(self):
        """메모리 사용량 로깅"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            self.memory_usage.append({
                'timestamp': time.time(),
                'memory_mb': memory_mb
            })
            logger.info(f"메모리 사용량: {memory_mb:.1f}MB")
        except ImportError:
            logger.warning("psutil이 설치되지 않아 메모리 모니터링을 사용할 수 없습니다.")

class KeywordAnalyzer:
    """키워드 분석 클래스"""
    
    def __init__(self):
        self.okt = Okt()
        self.stop_words = self._load_stop_words()
        
    def _load_stop_words(self) -> set:
        """한국어 불용어 로드"""
        stop_words = {
            '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만', '그런데',
            '그러나', '그래서', '그런', '이런', '저런', '어떤', '무슨', '어떻게', '왜',
            '언제', '어디서', '누가', '무엇을', '어떤', '이것', '저것', '그것', '우리',
            '저희', '그들', '당신', '너희', '그녀', '그분', '이분', '저분', '이런',
            '저런', '그런', '어떤', '무슨', '어떻게', '왜', '언제', '어디서', '누가',
            '무엇을', '어떤', '이것', '저것', '그것', '우리', '저희', '그들', '당신',
            '너희', '그녀', '그분', '이분', '저분'
        }
        return stop_words
    
    def analyze_keywords(self, texts: List[str], top_n: int = 20) -> Dict:
        """텍스트에서 키워드 분석"""
        if not texts:
            return {}
            
        # 모든 텍스트 결합
        combined_text = ' '.join(texts)
        
        # 형태소 분석
        try:
            nouns = self.okt.nouns(combined_text)
            # 불용어 제거 및 길이 필터링
            filtered_nouns = [word for word in nouns if len(word) > 1 and word not in self.stop_words]
            
            # 빈도수 계산
            word_freq = defaultdict(int)
            for word in filtered_nouns:
                word_freq[word] += 1
            
            # 상위 키워드 추출
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
            
            # 감정 분석 (간단한 버전)
            sentiment_scores = []
            for text in texts[:10]:  # 처음 10개 텍스트만 분석
                try:
                    blob = TextBlob(text)
                    sentiment_scores.append(blob.sentiment.polarity)
                except:
                    sentiment_scores.append(0)
            
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
            
            return {
                'top_keywords': dict(top_keywords),
                'total_words': len(filtered_nouns),
                'unique_words': len(word_freq),
                'sentiment_score': avg_sentiment,
                'sentiment_label': self._get_sentiment_label(avg_sentiment)
            }
            
        except Exception as e:
            logger.error(f"키워드 분석 오류: {e}")
            return {}
    
    def _get_sentiment_label(self, score: float) -> str:
        """감정 점수를 라벨로 변환"""
        if score > 0.1:
            return "긍정적"
        elif score < -0.1:
            return "부정적"
        else:
            return "중립적"
            logger.warning("psutil이 설치되지 않아 메모리 사용량을 확인할 수 없습니다.")
            return 0

class YouTubeCrawler:
    def __init__(self, config: Optional[ConfigManager] = None):
        self.driver = None
        self.config = config or ConfigManager()
        self.cache = CacheManager() if self.config.get('cache_enabled') else None
        self.monitor = PerformanceMonitor()
        self.session = None
        # 안정성을 위해 max_workers를 더 낮게 설정
        max_workers = min(self.config.get('max_workers'), 2)
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="YouTubeCrawler"
        )
        self.setup_driver()
        
    def send_notification(self, title, message):
        """Streamlit 웹 알림 전송"""
        try:
            # Streamlit 세션 상태에 알림 정보 저장
            if hasattr(self, 'st_session_state'):
                if 'notifications' not in self.st_session_state:
                    self.st_session_state.notifications = []
                
                notification = {
                    'title': title,
                    'message': message,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
                self.st_session_state.notifications.append(notification)
                
                # 최대 10개 알림만 유지
                if len(self.st_session_state.notifications) > 10:
                    self.st_session_state.notifications = self.st_session_state.notifications[-10:]
                    
            logger.info(f"웹 알림 전송: {title} - {message}")
        except Exception as e:
            logger.error(f"웹 알림 전송 실패: {e}")
        
    def setup_driver(self):
        """Chrome 드라이버 설정 - 최적화됨"""
        chrome_options = Options()
        
        # 성능 최적화 옵션들
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        chrome_options.add_argument("--disable-background-mode")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-domain-reliability")
        chrome_options.add_argument("--disable-component-update")
        chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=2048")  # 메모리 사용량 감소
        chrome_options.add_argument("--disable-software-rasterizer")
        
        # 연결 및 성능 최적화
        chrome_options.add_argument("--disable-http2")  # HTTP/2 비활성화로 연결 안정성 향상
        chrome_options.add_argument("--disable-quic")   # QUIC 비활성화
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        chrome_options.add_argument("--disable-background-mode")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-domain-reliability")
        chrome_options.add_argument("--disable-component-update")
        chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=2048")
        chrome_options.add_argument("--disable-software-rasterizer")
        
        # 헤드리스 모드 설정
        if self.config.get('headless'):
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
        
        # 자동화 감지 방지
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_setting_values.plugins": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.media_stream": 2,
            "profile.default_content_setting_values.mixed_script": 2,
            "profile.default_content_setting_values.protocol_handlers": 2,
            "profile.default_content_setting_values.ppapi_broker": 2,
            "profile.default_content_setting_values.midi_sysex": 2,
            "profile.default_content_setting_values.push_messaging": 2,
            "profile.default_content_setting_values.ssl_cert_decisions": 2,
            "profile.default_content_setting_values.metro_switch_to_desktop": 2,
            "profile.default_content_setting_values.protected_media_identifier": 2,
            "profile.default_content_setting_values.app_banner": 2,
            "profile.default_content_setting_values.site_engagement": 2,
            "profile.default_content_setting_values.durable_storage": 2
        })
        
        # 오디오 관련 설정
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-audio")
        chrome_options.add_argument("--disable-audio-output")
        chrome_options.add_argument("--disable-speech-api")
        chrome_options.add_argument("--disable-speech-synthesis-api")
        
        try:
            # Streamlit Cloud 환경 감지
            if os.environ.get('STREAMLIT_SERVER_RUN_ON_IP') or os.environ.get('STREAMLIT_SERVER_PORT'):
                # Streamlit Cloud 환경에서는 시스템에 설치된 Chrome 사용
                chrome_options.binary_location = "/usr/bin/chromium"
                service = Service("/usr/bin/chromedriver")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # 로컬 환경에서는 ChromeDriverManager 사용
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 타임아웃 설정 (안정성 향상)
            timeout = min(self.config.get('timeout'), 15)
            self.driver.set_page_load_timeout(timeout)
            self.driver.implicitly_wait(timeout // 3)  # 안정적인 대기 시간
            self.driver.set_script_timeout(timeout)
            
            # 자동화 감지 방지 스크립트 실행
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko', 'en-US', 'en']})")
            
            logger.info("Chrome 드라이버 초기화 성공")
            
        except Exception as e:
            logger.error(f"ChromeDriver 초기화 실패: {e}")
            self._fallback_driver_setup(chrome_options)
    
    def _fallback_driver_setup(self, chrome_options):
        """대체 드라이버 설정"""
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            timeout = self.config.get('timeout')
            self.driver.set_page_load_timeout(timeout)
            self.driver.implicitly_wait(timeout // 3)
            self.driver.set_script_timeout(timeout)
            logger.info("시스템 ChromeDriver 사용 성공")
        except Exception as e:
            logger.error(f"시스템 ChromeDriver도 실패: {e}")
            try:
                basic_options = Options()
                basic_options.add_argument("--headless")
                basic_options.add_argument("--no-sandbox")
                basic_options.add_argument("--disable-dev-shm-usage")
                self.driver = webdriver.Chrome(options=basic_options)
                timeout = self.config.get('timeout')
                self.driver.set_page_load_timeout(timeout)
                self.driver.implicitly_wait(timeout // 3)
                logger.info("기본 설정으로 ChromeDriver 사용 성공")
            except Exception as e3:
                logger.error(f"모든 ChromeDriver 초기화 실패: {e3}")
                raise e3
    
    async def search_videos_async(self, keywords: List[str], max_videos_per_keyword: int = 10, 
                                start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        """비동기 영상 검색"""
        self.monitor.start_timer('search_videos')
        self.send_notification("유튜브 크롤러", f"{len(keywords)}개 키워드로 비동기 영상 검색을 시작합니다.")
        
        # 캐시 키 생성
        cache_key = self._get_search_cache_key(keywords, max_videos_per_keyword, start_date, end_date)
        
        # 캐시 확인
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info("캐시된 검색 결과를 사용합니다.")
                self.send_notification("유튜브 크롤러", f"캐시된 결과 사용 - {len(cached_result)}개 영상")
                return cached_result
        
        # 비동기 검색 실행
        tasks = []
        for keyword in keywords:
            task = self._search_single_keyword_async(keyword, max_videos_per_keyword, start_date, end_date)
            tasks.append(task)
        
        # 모든 검색 완료 대기
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 병합
        all_videos = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"키워드 '{keywords[i]}' 검색 실패: {result}")
                continue
            all_videos.extend(result)
        
        # 캐시 저장
        if self.cache and all_videos:
            self.cache.set(cache_key, all_videos)
        
        self.monitor.end_timer('search_videos')
        self.monitor.log_memory_usage()
        
        self.send_notification("유튜브 크롤러", f"비동기 검색 완료! 총 {len(all_videos)}개 영상을 발견했습니다.")
        return all_videos
    
    def search_videos(self, keywords: List[str], max_videos_per_keyword: int = 10, 
                     start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        """동기 영상 검색 (기존 호환성 유지)"""
        return asyncio.run(self.search_videos_async(keywords, max_videos_per_keyword, start_date, end_date))
    
    def _get_search_cache_key(self, keywords: List[str], max_videos: int, 
                            start_date: Optional[datetime], end_date: Optional[datetime]) -> str:
        """검색 캐시 키 생성"""
        cache_data = {
            'keywords': keywords,
            'max_videos': max_videos,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }
        return self.cache._get_cache_key(json.dumps(cache_data, sort_keys=True))
    
    async def _search_single_keyword_async(self, keyword: str, max_videos: int, 
                                         start_date: Optional[datetime], end_date: Optional[datetime]) -> List[Dict]:
        """단일 키워드 비동기 검색"""
        logger.info(f"키워드 '{keyword}' 비동기 검색 시작")
        
        # 캐시 확인
        cache_key = self._get_search_cache_key([keyword], max_videos, start_date, end_date)
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info(f"키워드 '{keyword}' 캐시된 결과 사용")
                return cached_result
        
        # 스레드 풀에서 실행
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor, 
            self._search_single_keyword, 
            keyword, max_videos, start_date, end_date
        )
        
        # 캐시 저장
        if self.cache and result:
            self.cache.set(cache_key, result)
        
        return result
    
    def _search_single_keyword(self, keyword: str, max_videos: int, 
                             start_date: Optional[datetime], end_date: Optional[datetime]) -> List[Dict]:
        """단일 키워드로 검색 (최적화됨)"""
        search_url = f"https://www.youtube.com/results?search_query={keyword.replace(' ', '+')}"
        
        # 날짜 필터링
        if start_date or end_date:
            search_url += f"&sp=CAI%253D"
        
        try:
            self.driver.get(search_url)
            logger.info(f"검색 URL 로딩: {search_url}")
            
            # 페이지 로딩 대기
            WebDriverWait(self.driver, self.config.get('timeout')).until(
                EC.presence_of_element_located((By.TAG_NAME, "ytd-video-renderer"))
            )
            
        except Exception as e:
            logger.error(f"페이지 로딩 오류: {e}")
            try:
                WebDriverWait(self.driver, self.config.get('timeout') // 2).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e2:
                logger.error(f"대안 페이지 로딩도 실패: {e2}")
                raise
        
        # 스크롤하여 더 많은 영상 로드
        self._scroll_page_optimized()
        
        # 영상 정보 추출
        videos = []
        video_elements = self.driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
        
        for element in video_elements[:max_videos * 2]:
            try:
                video_info = self._extract_video_info_optimized(element, keyword)
                if video_info and self._is_video_in_date_range(video_info, start_date, end_date):
                    videos.append(video_info)
                    if len(videos) >= max_videos:
                        break
            except Exception as e:
                logger.warning(f"영상 정보 추출 오류: {e}")
                continue
                
        return videos
    
    def _scroll_page_optimized(self):
        """최적화된 페이지 스크롤"""
        try:
            logger.info("최적화된 페이지 스크롤 시작...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = self.config.get('scroll_count')
            wait_time = self.config.get('wait_time')
            
            for i in range(scroll_count):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(wait_time)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    logger.info(f"스크롤 완료 (반복 {i+1})")
                    break
                last_height = new_height
                
        except Exception as e:
            logger.error(f"스크롤 중 오류: {e}")
    
    def _extract_video_info_optimized(self, element, keyword: str) -> Optional[Dict]:
        """최적화된 영상 정보 추출"""
        try:
            # 제목
            title_element = element.find_element(By.CSS_SELECTOR, "#video-title")
            title = title_element.get_attribute("title")
            
            # 링크
            video_url = title_element.get_attribute("href")
            if not video_url:
                return None
                
            # 채널명
            channel_element = element.find_element(By.CSS_SELECTOR, "#channel-name a")
            channel_name = channel_element.text
            
            # 조회수
            view_count = "N/A"
            try:
                view_element = element.find_element(By.CSS_SELECTOR, "#metadata-line span")
                view_count = view_element.text
            except:
                pass
                
            # 업로드 시간
            upload_time = "N/A"
            try:
                time_element = element.find_element(By.CSS_SELECTOR, "#metadata-line span:nth-child(2)")
                upload_time = time_element.text
            except:
                pass
                
            # 영상 ID 추출
            video_id = self._extract_video_id(video_url)
            
            # 발행일 파싱 및 포맷팅
            parsed_date = self._parse_upload_time(upload_time)
            formatted_date = parsed_date.strftime('%Y.%m.%d') if parsed_date else 'N/A'
            
            return {
                'keyword': keyword,
                'title': title,
                'channel_name': channel_name,
                'view_count': view_count,
                'upload_time': upload_time,
                'formatted_upload_date': formatted_date,
                'video_url': video_url,
                'video_id': video_id,
                'crawled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"영상 정보 추출 오류: {e}")
            return None
    
    def _extract_video_id(self, url):
        """URL에서 영상 ID 추출"""
        try:
            parsed_url = urlparse(url)
            if parsed_url.hostname == 'www.youtube.com':
                query_params = parse_qs(parsed_url.query)
                return query_params.get('v', [None])[0]
            elif parsed_url.hostname == 'youtu.be':
                return parsed_url.path[1:]
        except:
            pass
        return None
    
    def _parse_upload_time(self, time_text):
        """업로드 시간 텍스트를 datetime 객체로 변환 - 강화된 버전"""
        if not time_text or time_text == "N/A":
            return None
            
        try:
            now = datetime.now()
            
            if '초' in time_text or '분' in time_text:
                # 방금 전, N분 전, N초 전
                return now
            elif '시간' in time_text:
                # N시간 전
                hours = int(re.findall(r'(\d+)', time_text)[0])
                return now - timedelta(hours=hours)
            elif '일' in time_text:
                # N일 전
                days = int(re.findall(r'(\d+)', time_text)[0])
                return now - timedelta(days=days)
            elif '주' in time_text:
                # N주 전
                weeks = int(re.findall(r'(\d+)', time_text)[0])
                return now - timedelta(weeks=weeks)
            elif '개월' in time_text:
                # N개월 전
                months = int(re.findall(r'(\d+)', time_text)[0])
                return now - timedelta(days=months * 30)
            elif '년' in time_text:
                # N년 전
                years = int(re.findall(r'(\d+)', time_text)[0])
                return now - timedelta(days=years * 365)
            else:
                # 다양한 날짜 형식 파싱
                date_patterns = [
                    r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})',  # 2024. 1. 15.
                    r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일',  # 2024년 1월 15일
                    r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2024-01-15
                    r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2024/01/15
                ]
                
                for pattern in date_patterns:
                    date_match = re.search(pattern, time_text)
                    if date_match:
                        year, month, day = map(int, date_match.groups())
                        return datetime(year, month, day)
                        
                # 마지막 시도: 현재 시간 반환
                logger.warning(f"알 수 없는 시간 형식: {time_text}")
                return now
                
        except Exception as e:
            logger.warning(f"날짜 파싱 오류: {time_text} - {e}")
            return None
    
    def _is_video_in_date_range(self, video_info, start_date: Optional[datetime], end_date: Optional[datetime]) -> bool:
        """영상이 지정된 날짜 범위에 있는지 확인"""
        if not start_date and not end_date:
            return True
        
        upload_time_text = video_info.get('upload_time', '')
        if not upload_time_text or upload_time_text == 'N/A':
            return True  # 날짜 정보가 없으면 포함
        
        upload_date = self._parse_upload_time(upload_time_text)
        if not upload_date:
            return True  # 날짜 파싱 실패시 포함
        
        # 시작 날짜 체크
        if start_date and upload_date < start_date:
            return False
        
        # 종료 날짜 체크
        if end_date and upload_date > end_date:
            return False
        
        return True
    
    async def get_video_comments_async(self, video_id: str, max_comments: int = 50) -> List[Dict]:
        """비동기 댓글 수집"""
        self.monitor.start_timer(f'comments_{video_id}')
        
        # 캐시 확인
        cache_key = f"comments_{video_id}_{max_comments}"
        if self.cache:
            cached_comments = self.cache.get(cache_key)
            if cached_comments:
                logger.info(f"댓글 캐시 사용: {video_id}")
                return cached_comments
        
        # 스레드 풀에서 실행
        loop = asyncio.get_event_loop()
        comments = await loop.run_in_executor(
            self.executor,
            self._get_video_comments_sync,
            video_id,
            max_comments
        )
        
        # 캐시 저장
        if self.cache and comments:
            self.cache.set(cache_key, comments)
        
        self.monitor.end_timer(f'comments_{video_id}')
        return comments
    
    def get_video_comments(self, video_id: str, max_comments: int = 50) -> List[Dict]:
        """동기 댓글 수집 (기존 호환성 유지)"""
        return asyncio.run(self.get_video_comments_async(video_id, max_comments))
    
    def _get_video_comments_sync(self, video_id: str, max_comments: int = 50) -> List[Dict]:
        """동기 댓글 수집 구현"""
        comments = []
        
        try:
            # 댓글 수집 시작 알림
            self.send_notification("유튜브 크롤러", f"댓글 수집 시작 - 영상 ID: {video_id}")
            
            # 댓글 페이지 URL
            comment_url = f"https://www.youtube.com/watch?v={video_id}&disable_polymer=true"
            
            # 타임아웃 설정으로 페이지 로딩
            try:
                self.driver.get(comment_url)
                time.sleep(min(self.config.get('wait_time'), 2))  # 대기 시간 제한
            except Exception as e:
                logger.warning(f"페이지 로딩 오류: {e}")
                return comments
            
            # 자동 재생 비활성화 및 소리 끄기 (타임아웃 적용)
            try:
                self.driver.execute_script("""
                    // 자동 재생 비활성화
                    if (window.yt && window.yt.player) {
                        window.yt.player.getPlayerByElement = function() {
                            return {
                                mute: function() { console.log('Muted'); },
                                pauseVideo: function() { console.log('Paused'); },
                                setVolume: function(volume) { console.log('Volume set to 0'); }
                            };
                        };
                    }
                    
                    // 비디오 요소 찾아서 소리 끄기
                    var videos = document.querySelectorAll('video');
                    for (var i = 0; i < videos.length; i++) {
                        videos[i].muted = true;
                        videos[i].volume = 0;
                        videos[i].pause();
                    }
                    
                    // 오디오 요소 찾아서 소리 끄기
                    var audios = document.querySelectorAll('audio');
                    for (var i = 0; i < audios.length; i++) {
                        audios[i].muted = true;
                        audios[i].volume = 0;
                        audios[i].pause();
                    }
                """)
            except Exception as e:
                logger.warning(f"자동 재생 비활성화 오류: {e}")
            
            # 댓글 섹션 찾기 (타임아웃 적용)
            comment_section = None
            try:
                comment_section = self._find_comment_section()
                if comment_section:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", comment_section)
                    time.sleep(1)  # 짧은 대기 시간
            except Exception as e:
                logger.warning(f"댓글 섹션 스크롤 오류: {e}")
            
            # 댓글 로드 (타임아웃 적용)
            try:
                self._scroll_comments_optimized()
            except Exception as e:
                logger.warning(f"댓글 스크롤 오류: {e}")
            
            # 댓글 요소 찾기 (타임아웃 적용)
            comment_elements = []
            try:
                comment_elements = self._find_comment_elements()
            except Exception as e:
                logger.warning(f"댓글 요소 찾기 오류: {e}")
            
            # 댓글 정보 추출 (제한된 수만 처리)
            comment_data = []
            max_elements = min(len(comment_elements), 20)  # 최대 20개만 처리
            
            for i, element in enumerate(comment_elements[:max_elements]):
                try:
                    comment_info = self._extract_comment_info(element, video_id)
                    if comment_info:
                        comment_data.append(comment_info)
                        if len(comment_data) >= max_comments:
                            break
                except Exception as e:
                    logger.warning(f"댓글 정보 추출 오류 (인덱스 {i}): {e}")
                    continue
            
            # 댓글 정렬 및 선택
            comments = self._sort_and_select_comments(comment_data, max_comments)
            
        except Exception as e:
            logger.error(f"댓글 수집 오류 (video_id: {video_id}): {e}")
            self.send_notification("유튜브 크롤러", f"댓글 수집 오류 - {video_id}")
            
        # 댓글 수집 완료 알림
        if comments:
            latest_time = comments[0].get('comment_time', 'N/A') if comments else 'N/A'
            top_likes = max([comment.get('like_count', 0) for comment in comments])
            self.send_notification("유튜브 크롤러", f"댓글 수집 완료 - {len(comments)}개 댓글 (최신: {latest_time}, 최고 좋아요: {top_likes})")
        else:
            self.send_notification("유튜브 크롤러", "댓글 수집 완료 - 수집된 댓글이 없습니다")
            
        return comments
    
    def _find_comment_section(self):
        """댓글 섹션 찾기"""
        comment_selectors = [
            "#comments",
            "#comments-section",
            "ytd-comments#comments",
            "#content ytd-comments",
            "ytd-comments"
        ]
        
        for selector in comment_selectors:
            try:
                comment_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"댓글 섹션 찾음: {selector}")
                return comment_section
            except:
                continue
        
        logger.warning("댓글 섹션을 찾을 수 없습니다.")
        return None
    
    def _find_comment_elements(self):
        """댓글 요소 찾기 (최적화됨)"""
        # 주요 선택자만 사용
        primary_selectors = [
            "ytd-comment-renderer",
            "#comment #content"
        ]
        
        for selector in primary_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 0:
                    logger.info(f"댓글 요소 찾음: {selector} - {len(elements)}개")
                    return elements[:15]  # 최대 15개만 반환 (안정성 향상)
            except Exception as e:
                logger.warning(f"선택자 {selector} 오류: {e}")
                continue
        
        # 대체 선택자 시도
        fallback_selectors = [
            ".ytd-comment-renderer",
            "#comment-content"
        ]
        
        for selector in fallback_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 0:
                    logger.info(f"대체 댓글 요소 찾음: {selector} - {len(elements)}개")
                    return elements[:15]  # 최대 15개만 반환 (안정성 향상)
            except Exception as e:
                logger.warning(f"대체 선택자 {selector} 오류: {e}")
                continue
        
        # JavaScript로 간단한 확인 (타임아웃 적용)
        try:
            comment_count = self.driver.execute_script("""
                try {
                    var comments = document.querySelectorAll('ytd-comment-renderer');
                    return comments.length;
                } catch(e) {
                    return 0;
                }
            """)
            
            if comment_count > 0:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, "ytd-comment-renderer")
                    logger.info(f"JavaScript 확인 후 댓글 요소 찾음: {len(elements)}개")
                    return elements[:15]  # 최대 15개만 반환 (안정성 향상)
                except Exception as e:
                    logger.warning(f"JavaScript 확인 후 요소 찾기 실패: {e}")
        except Exception as e:
            logger.warning(f"JavaScript 댓글 확인 실패: {e}")
        
        logger.warning("댓글 요소를 찾을 수 없습니다.")
        return []
    
    def _extract_comment_info(self, element, video_id: str) -> Optional[Dict]:
        """댓글 정보 추출"""
        try:
            # 댓글 텍스트 추출
            text_element = element.find_element(By.CSS_SELECTOR, "#content-text")
            comment_text = text_element.text.strip()
            
            if not comment_text or len(comment_text) < 5:
                return None
            
            # 좋아요 수 추출
            like_count = self._extract_like_count(element)
            
            # 댓글의 댓글 수 추출
            reply_count = self._extract_reply_count(element)
            
            # 댓글 시간 추출
            comment_time = self._extract_comment_time(element)
            
            # 댓글에서 키워드 추출 (최대 5개)
            extracted_keywords = self._extract_comment_keywords(comment_text, max_keywords=5)
            
            # 키워드 추출 결과 로깅 (디버깅용)
            if extracted_keywords:
                logger.info(f"댓글에서 키워드 추출 성공: {extracted_keywords}")
            else:
                logger.debug(f"댓글에서 키워드 추출 실패 또는 없음: {comment_text[:50]}...")
            
            return {
                'video_id': video_id,
                'comment': comment_text,
                'extracted_keywords': extracted_keywords,
                'like_count': like_count,
                'reply_count': reply_count,
                'comment_time': comment_time,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.warning(f"댓글 정보 추출 오류: {e}")
            return None
    
    def _extract_like_count(self, element) -> int:
        """좋아요 수 추출"""
        try:
            like_element = element.find_element(By.CSS_SELECTOR, "#vote-count-middle")
            like_text = like_element.text.strip()
            if like_text:
                if 'K' in like_text:
                    return int(float(like_text.replace('K', '')) * 1000)
                elif 'M' in like_text:
                    return int(float(like_text.replace('M', '')) * 1000000)
                else:
                    return int(like_text.replace(',', ''))
        except:
            pass
        return 0
    
    def _extract_reply_count(self, element) -> int:
        """댓글의 댓글 수 추출"""
        try:
            reply_element = element.find_element(By.CSS_SELECTOR, "#reply-count")
            reply_text = reply_element.text.strip()
            if reply_text and '답글' in reply_text:
                numbers = re.findall(r'\d+', reply_text)
                if numbers:
                    return int(numbers[0])
        except:
            pass
        return 0
    
    def _extract_comment_time(self, element) -> str:
        """댓글 시간 추출"""
        try:
            time_element = element.find_element(By.CSS_SELECTOR, "#header-author #published-time-text")
            return time_element.text.strip()
        except:
            return ""
    
    def _extract_comment_keywords(self, comment_text: str, max_keywords: int = 5) -> str:
        """댓글에서 키워드 추출 (최대 5개, 콤마로 구분)"""
        try:
            if not comment_text or len(comment_text) < 3:
                return ""
            
            # Java 환경 확인 및 KoNLPy 사용
            if konlpy_available:
                try:
                    # Java 환경 확인
                    import os
                    import subprocess
                    
                    # JAVA_HOME 확인
                    java_home = os.environ.get('JAVA_HOME')
                    if not java_home:
                        # Java 설치 확인
                        try:
                            subprocess.run(['java', '-version'], capture_output=True, check=True)
                            logger.info("Java가 설치되어 있지만 JAVA_HOME이 설정되지 않음")
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            logger.warning("Java가 설치되지 않음, 기본 키워드 추출 방식 사용")
                            raise Exception("Java not available")
                    
                    from konlpy.tag import Okt
                    okt = Okt()
                    
                    # 명사 추출
                    nouns = okt.nouns(comment_text)
                    
                    # 불용어 제거 및 길이 필터링
                    stop_words = {
                        '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만', '그런데',
                        '그러나', '그래서', '그런', '이런', '저런', '어떤', '무슨', '어떻게', '왜',
                        '언제', '어디서', '누가', '무엇을', '어떤', '이것', '저것', '그것', '우리',
                        '저희', '그들', '당신', '너희', '그녀', '그분', '이분', '저분'
                    }
                    
                    filtered_nouns = [word for word in nouns if len(word) >= 2 and word not in stop_words]
                    
                    # 빈도수 계산
                    word_freq = {}
                    for word in filtered_nouns:
                        word_freq[word] = word_freq.get(word, 0) + 1
                    
                    # 빈도수 순으로 정렬하여 상위 키워드 선택
                    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                    
                    # 최대 5개까지 선택
                    selected_keywords = [word for word, freq in sorted_words[:max_keywords]]
                    
                    # 콤마로 구분하여 반환
                    return ", ".join(selected_keywords) if selected_keywords else ""
                    
                except Exception as konlpy_error:
                    logger.warning(f"KoNLPy 키워드 추출 실패 (Java/JVM 문제), 기본 방식 사용: {konlpy_error}")
            
            # KoNLPy가 없거나 실패한 경우 개선된 기본 방식 사용
            keywords = []
            
            # 한글 명사 추출 (개선된 패턴 매칭)
            korean_nouns = re.findall(r'[가-힣]{2,}', comment_text)
            # 영어 단어 추출 (2글자 이상)
            english_words = re.findall(r'\b[a-zA-Z]{2,}\b', comment_text)
            
            # 한글 명사와 영어 단어 결합
            all_words = korean_nouns + english_words
            
            # 확장된 불용어 제거
            basic_stop_words = {
                '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만', '그런데',
                '그러나', '그래서', '그런', '이런', '저런', '어떤', '무슨', '어떻게', '왜',
                '언제', '어디서', '누가', '무엇을', '어떤', '이것', '저것', '그것', '우리',
                '저희', '그들', '당신', '너희', '그녀', '그분', '이분', '저분', '있', '하', '되',
                '보', '알', '생각', '말', '일', '때', '곳', '사람', '나', '너', '그', '이', '저'
            }
            filtered_words = [word for word in all_words if word not in basic_stop_words]
            
            # 빈도수 계산
            word_freq = {}
            for word in filtered_words:
                if len(word) >= 2:  # 2글자 이상만
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # 빈도수 순으로 정렬하여 상위 키워드 선택
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            # 최대 5개까지 선택
            selected_keywords = [word for word, freq in sorted_words[:max_keywords]]
            
            # 콤마로 구분하여 반환
            return ", ".join(selected_keywords) if selected_keywords else ""
            
        except Exception as e:
            logger.warning(f"댓글 키워드 추출 오류: {e}")
            return ""
    
    def _sort_and_select_comments(self, comment_data: List[Dict], max_comments: int) -> List[Dict]:
        """댓글 정렬 및 선택"""
        def sort_key(comment):
            time_text = comment.get('comment_time', '')
            if time_text:
                numbers = re.findall(r'\d+', time_text)
                if numbers:
                    time_value = int(numbers[0])
                    if '시간' in time_text:
                        return time_value
                    elif '일' in time_text:
                        return time_value * 24
                    elif '분' in time_text:
                        return time_value / 60
                    elif '주' in time_text:
                        return time_value * 168
                    elif '개월' in time_text or '달' in time_text:
                        return time_value * 720
                    elif '년' in time_text:
                        return time_value * 8760
            return 999999
        
        comment_data.sort(key=sort_key)
        comments = comment_data[:max_comments]
        
        # 인덱스 추가
        for i, comment in enumerate(comments):
            comment['comment_index'] = i + 1
        
        return comments
    
    def _scroll_comments_optimized(self):
        """최적화된 댓글 스크롤"""
        try:
            logger.info("최적화된 댓글 스크롤 시작...")
            
            # 댓글 섹션 찾기 (타임아웃 적용)
            comment_section = None
            try:
                comment_section = self._find_comment_section()
            except Exception as e:
                logger.warning(f"댓글 섹션 찾기 오류: {e}")
            
            if not comment_section:
                logger.warning("댓글 섹션을 찾을 수 없습니다. 페이지 하단으로 스크롤합니다.")
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)  # 짧은 대기 시간
                except Exception as e:
                    logger.warning(f"페이지 하단 스크롤 오류: {e}")
                
                # 다시 댓글 섹션 찾기
                try:
                    comment_section = self._find_comment_section()
                except Exception as e:
                    logger.warning(f"재시도 댓글 섹션 찾기 오류: {e}")
            
            # 댓글 섹션으로 스크롤
            if comment_section:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", comment_section)
                    time.sleep(1)  # 짧은 대기 시간
                except Exception as e:
                    logger.warning(f"댓글 섹션 스크롤 실패: {e}")
            
            # 간단한 스크롤만 시도 (복잡한 방법 제거)
            try:
                self._scroll_method_simple()
            except Exception as e:
                logger.warning(f"간단한 스크롤 실패: {e}")
            
            logger.info("댓글 스크롤 완료")
            
        except Exception as e:
            logger.error(f"댓글 스크롤 오류: {e}")
    
    def _scroll_method_simple(self):
        """간단한 스크롤 방법"""
        try:
            # 최소한의 스크롤만 수행
            for i in range(3):  # 3번만 스크롤
                try:
                    self.driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(0.5)  # 짧은 대기 시간
                    
                    # 댓글 확인
                    comments = self.driver.find_elements(By.CSS_SELECTOR, "ytd-comment-renderer")
                    if len(comments) > 0:
                        logger.info(f"댓글 {len(comments)}개 발견")
                        return True
                except Exception as e:
                    logger.warning(f"스크롤 반복 {i+1} 오류: {e}")
                    continue
                    
            return False
        except Exception as e:
            logger.warning(f"간단한 스크롤 방법 오류: {e}")
            return False
    
    def _scroll_method_1(self):
        """기본 스크롤 방법"""
        try:
            for i in range(5):
                self.driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(1)
                
                comments = self.driver.find_elements(By.CSS_SELECTOR, "ytd-comment-renderer")
                if len(comments) > 0:
                    logger.info(f"댓글 {len(comments)}개 발견")
                    return True
                
                # 추가 댓글 로드 버튼 클릭 시도
                try:
                    more_button = self.driver.find_element(By.CSS_SELECTOR, "#more-replies")
                    if more_button and more_button.is_displayed():
                        more_button.click()
                        time.sleep(1)
                except:
                    pass
                    
            return False
        except Exception as e:
            logger.warning(f"기본 스크롤 방법 오류: {e}")
            return False
    
    def _scroll_method_2(self):
        """동적 로딩 대기 방법"""
        try:
            comments_section = self.driver.find_element(By.CSS_SELECTOR, "ytd-comments")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", comments_section)
            time.sleep(2)
            
            for i in range(10):
                self.driver.execute_script("window.scrollBy(0, 200);")
                time.sleep(0.8)
                
                comments = self.driver.find_elements(By.CSS_SELECTOR, "ytd-comment-renderer")
                if len(comments) > 0:
                    logger.info(f"동적 로딩으로 댓글 {len(comments)}개 발견")
                    return True
                    
                # "더 보기" 버튼 클릭 시도
                try:
                    more_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label*='더 보기'], [aria-label*='Show more']")
                    for button in more_buttons:
                        if button.is_displayed():
                            button.click()
                            time.sleep(0.5)
                except:
                    pass
                    
            return False
        except Exception as e:
            logger.warning(f"동적 로딩 방법 오류: {e}")
            return False
    
    def _scroll_method_3(self):
        """JavaScript 직접 실행 방법"""
        try:
            result = self.driver.execute_script("""
                var commentsSection = document.querySelector('ytd-comments');
                if (commentsSection) {
                    commentsSection.scrollIntoView({behavior: 'smooth', block: 'start'});
                    
                    var event = new Event('scroll');
                    window.dispatchEvent(event);
                    
                    var moreButtons = document.querySelectorAll('[aria-label*="더 보기"], [aria-label*="Show more"]');
                    for (var i = 0; i < moreButtons.length; i++) {
                        if (moreButtons[i].offsetParent !== null) {
                            moreButtons[i].click();
                        }
                    }
                    
                    var comments = document.querySelectorAll('ytd-comment-renderer');
                    return comments.length;
                }
                return 0;
            """)
            
            time.sleep(2)
            
            comments = self.driver.find_elements(By.CSS_SELECTOR, "ytd-comment-renderer")
            if len(comments) > 0:
                logger.info(f"JavaScript 실행으로 댓글 {len(comments)}개 발견")
                return True
            return False
        except Exception as e:
            logger.warning(f"JavaScript 실행 방법 오류: {e}")
            return False
    
    async def save_to_excel_async(self, videos: List[Dict], comments: List[Dict], filename: str = "youtube_data.xlsx") -> Optional[str]:
        """비동기 엑셀 저장"""
        self.monitor.start_timer('save_excel')
        
        # 스레드 풀에서 실행
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._save_to_excel_sync,
            videos,
            comments,
            filename
        )
        
        self.monitor.end_timer('save_excel')
        return result
    
    def save_to_excel(self, videos: List[Dict], comments: List[Dict], filename: str = "youtube_data.xlsx") -> Optional[str]:
        """동기 엑셀 저장 (기존 호환성 유지)"""
        return asyncio.run(self.save_to_excel_async(videos, comments, filename))
    
    def _save_to_excel_sync(self, videos: List[Dict], comments: List[Dict], filename: str) -> Optional[str]:
        """동기 엑셀 저장 구현 - 강화된 버전"""
        try:
            # 저장 시작 알림
            self.send_notification("유튜브 크롤러", f"데이터 저장 시작 - {filename}")
            
            # 인코딩 설정 가져오기
            encoding = self.config.get('excel_encoding', 'utf-8-sig')
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 영상 정보 저장 - 발행일 정보 추가
                videos_df = pd.DataFrame(videos)
                
                # 발행일 정보가 이미 포함되어 있으므로 추가 처리 불필요
                # formatted_upload_date 필드가 이미 YYYY.MM.DD 형식으로 포함됨
                
                videos_df.to_excel(writer, sheet_name='Videos', index=False)
                
                # 댓글 정보 저장
                if comments:
                    comments_df = pd.DataFrame(comments)
                    comments_df.to_excel(writer, sheet_name='Comments', index=False)
                
                # 키워드 분석 결과 저장 (활성화된 경우)
                if self.config.get('enable_keyword_analysis', True) and comments:
                    try:
                        analyzer = KeywordAnalyzer()
                        comment_texts = [comment.get('comment_text', '') for comment in comments if comment.get('comment_text')]
                        
                        if comment_texts:
                            keyword_analysis = analyzer.analyze_keywords(comment_texts)
                            
                            # 키워드 분석 결과를 데이터프레임으로 변환
                            if keyword_analysis.get('top_keywords'):
                                keywords_df = pd.DataFrame([
                                    {'keyword': k, 'frequency': v} 
                                    for k, v in keyword_analysis['top_keywords'].items()
                                ])
                                keywords_df.to_excel(writer, sheet_name='Keyword_Analysis', index=False)
                            
                            # 감정 분석 결과 저장
                            sentiment_df = pd.DataFrame([{
                                'sentiment_score': keyword_analysis.get('sentiment_score', 0),
                                'sentiment_label': keyword_analysis.get('sentiment_label', 'N/A'),
                                'total_words': keyword_analysis.get('total_words', 0),
                                'unique_words': keyword_analysis.get('unique_words', 0)
                            }])
                            sentiment_df.to_excel(writer, sheet_name='Sentiment_Analysis', index=False)
                            
                    except Exception as e:
                        logger.warning(f"키워드 분석 저장 오류: {e}")
                
                # 성능 메트릭 저장
                metrics = self.get_performance_metrics()
                if metrics:
                    metrics_df = pd.DataFrame([metrics])
                    metrics_df.to_excel(writer, sheet_name='Performance_Metrics', index=False)
                    
            logger.info(f"데이터가 {filename}에 저장되었습니다. (인코딩: {encoding})")
            
            # 저장 완료 알림
            self.send_notification("유튜브 크롤러", f"데이터 저장 완료! {len(videos)}개 영상, {len(comments)}개 댓글")
            return filename
            
        except Exception as e:
            logger.error(f"엑셀 저장 오류: {e}")
            self.send_notification("유튜브 크롤러", f"데이터 저장 오류: {e}")
            return None
    
    async def get_comments_for_videos_async(self, videos: List[Dict], max_comments_per_video: int = 50) -> List[Dict]:
        """여러 영상의 댓글을 비동기로 수집 (최적화됨)"""
        self.monitor.start_timer('batch_comments')
        
        # 배치 크기 제한으로 안정성 향상
        batch_size = min(len(videos), 2)  # 최대 2개 영상씩 처리 (안정성 향상)
        all_comments = []
        
        for i in range(0, len(videos), batch_size):
            batch = videos[i:i+batch_size]
            logger.info(f"배치 {i//batch_size + 1} 처리 중... ({len(batch)}개 영상)")
            
            # 배치별 비동기 댓글 수집 태스크 생성
            tasks = []
            for video in batch:
                video_id = video.get('video_id')
                if video_id:
                    task = self.get_video_comments_async(video_id, max_comments_per_video)
                    tasks.append(task)
            
            if tasks:
                try:
                    # 배치별로 댓글 수집 완료 대기 (타임아웃 적용)
                    results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=45  # 45초 타임아웃 (안정성 향상)
                    )
                    
                    # 결과 병합
                    for j, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(f"영상 '{batch[j].get('title', 'Unknown')}' 댓글 수집 실패: {result}")
                            continue
                        all_comments.extend(result)
                        
                except asyncio.TimeoutError:
                    logger.warning(f"배치 {i//batch_size + 1} 타임아웃 발생")
                except Exception as e:
                    logger.error(f"배치 {i//batch_size + 1} 처리 오류: {e}")
            
            # 배치 간 메모리 최적화
            if i + batch_size < len(videos):
                self.optimize_memory()
                await asyncio.sleep(1)  # 배치 간 대기
        
        self.monitor.end_timer('batch_comments')
        self.monitor.log_memory_usage()
        
        logger.info(f"배치 댓글 수집 완료: {len(all_comments)}개 댓글")
        return all_comments
    
    def get_comments_for_videos(self, videos: List[Dict], max_comments_per_video: int = 50) -> List[Dict]:
        """여러 영상의 댓글을 동기로 수집 (기존 호환성 유지)"""
        return asyncio.run(self.get_comments_for_videos_async(videos, max_comments_per_video))
    
    def get_performance_metrics(self) -> Dict:
        """성능 메트릭 반환"""
        metrics = self.monitor.get_metrics()
        memory_usage = self.monitor.log_memory_usage()
        
        return {
            'metrics': metrics,
            'memory_usage_mb': memory_usage,
            'cache_enabled': self.cache is not None,
            'max_workers': self.config.get('max_workers'),
            'config': self.config.config
        }
    
    def clear_cache(self):
        """캐시 삭제"""
        if self.cache:
            self.cache.clear()
            logger.info("캐시가 삭제되었습니다.")
    
    def update_config(self, new_config: Dict):
        """설정 업데이트"""
        self.config.update(new_config)
        logger.info(f"설정이 업데이트되었습니다: {new_config}")
    
    def optimize_memory(self):
        """메모리 최적화"""
        try:
            # 가비지 컬렉션 실행
            gc.collect()
            
            # 메모리 사용량 확인
            memory_usage = self.monitor.log_memory_usage()
            max_memory = self.config.get('max_memory_mb')
            
            if memory_usage > max_memory:
                logger.warning(f"메모리 사용량이 높습니다: {memory_usage:.2f} MB (제한: {max_memory} MB)")
                
                # 캐시 삭제로 메모리 확보
                if self.cache:
                    self.cache.clear()
                    logger.info("메모리 최적화를 위해 캐시를 삭제했습니다.")
            
            logger.info("메모리 최적화 완료")
            
        except Exception as e:
            logger.error(f"메모리 최적화 오류: {e}")
    
    def close(self):
        """드라이버 종료 및 리소스 정리"""
        try:
            # 성능 메트릭 로깅
            metrics = self.get_performance_metrics()
            logger.info(f"종료 시 성능 메트릭: {metrics}")
            
            # 스레드 풀 종료
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
                logger.info("스레드 풀이 종료되었습니다.")
            
            # 드라이버 종료
            if self.driver:
                try:
                    self.driver.close()
                    self.driver.quit()
                    logger.info("ChromeDriver 안전하게 종료됨")
                except Exception as e:
                    logger.error(f"드라이버 종료 중 오류: {e}")
                    try:
                        self.driver.quit()
                    except:
                        pass
                finally:
                    self.driver = None
            
            # 메모리 최적화
            self.optimize_memory()
            
            logger.info("YouTubeCrawler가 안전하게 종료되었습니다.")
            
        except Exception as e:
            logger.error(f"종료 중 오류: {e}")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close() 