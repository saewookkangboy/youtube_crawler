# 🌐 웹 서비스 사용 가이드

## 🚀 웹 서비스 시작하기

### 방법 1: 자동 스크립트 사용 (권장)
```bash
cd /Users/chunghyo/youtube_crawler
./start_web.sh
```

### 방법 2: 수동 실행
```bash
cd /Users/chunghyo/youtube_crawler
source venv/bin/activate
streamlit run app.py
```

### 방법 3: 설정 파일 사용
```bash
cd /Users/chunghyo/youtube_crawler
source venv/bin/activate
streamlit run app.py --config streamlit_config.toml
```

## 📍 접속 방법

웹 서비스가 시작되면 다음 주소로 접속하세요:

**🌐 http://localhost:8501**

## 🎯 주요 기능

### 1. 키워드 검색
- 3~5개의 키워드를 줄바꿈으로 구분하여 입력
- 예시:
  ```
  파이썬 튜토리얼
  머신러닝 기초
  데이터 분석
  ```

### 2. 수집 설정
- **키워드당 영상 수**: 5~50개 (슬라이더로 조정)
- **댓글 수집**: 체크박스로 선택
- **영상당 댓글 수**: 10~100개 (댓글 수집 시)

### 3. 날짜 필터링
- **날짜 범위 설정**: 체크박스로 활성화
- **시작 날짜**: 달력에서 선택 (기본값: 30일 전)
- **종료 날짜**: 달력에서 선택 (기본값: 오늘)

### 4. 파일 저장
- **파일명**: 자유롭게 입력 (기본값: youtube_data.xlsx)
- **자동 확장자**: .xlsx 자동 추가

## 📊 결과 확인

### 1. 실시간 진행 상황
- 진행률 바로 크롤링 상태 확인
- 단계별 상태 메시지 표시

### 2. 데이터 미리보기
- **영상 목록**: 수집된 영상 정보 테이블
- **댓글 목록**: 수집된 댓글 정보 테이블
- **분석 차트**: 키워드별, 채널별 통계

### 3. 파일 다운로드
- **엑셀 파일**: 전체 데이터 다운로드
- **CSV 파일**: 개별 시트 다운로드

## 🔧 문제 해결

### 포트 충돌
```bash
# 포트 사용 확인
lsof -i :8501

# 기존 프로세스 종료
pkill -f streamlit

# 다른 포트 사용
streamlit run app.py --server.port 8502
```

### 가상환경 문제
```bash
# 가상환경 재생성
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 패키지 오류
```bash
# 패키지 재설치
pip install --upgrade -r requirements.txt
```

## 📱 브라우저 호환성

- **Chrome**: 권장 (최신 버전)
- **Safari**: 지원
- **Firefox**: 지원
- **Edge**: 지원

## 🔒 보안 설정

- **로컬 접속만 허용**: localhost에서만 접속 가능
- **CORS 비활성화**: 개발 환경용
- **XSRF 보호 비활성화**: 로컬 사용

## 📈 성능 최적화

### 권장 사항
- **영상 수**: 키워드당 10~20개 (안정적)
- **댓글 수**: 영상당 20~50개 (시간 단축)
- **날짜 범위**: 1~3개월 (정확도 향상)

### 주의사항
- 대량 데이터 수집 시 시간이 오래 걸릴 수 있습니다
- 네트워크 상태에 따라 속도가 달라질 수 있습니다
- 유튜브 정책을 준수하여 적절한 간격으로 요청합니다

## 🆘 도움말

### 메뉴 항목
- **Get Help**: GitHub 저장소 링크
- **Report a bug**: 버그 리포트
- **About**: 서비스 정보

### 로그 확인
```bash
# Streamlit 로그 확인
tail -f ~/.streamlit/logs/streamlit.log
```

## 🎉 성공적인 사용을 위한 팁

1. **키워드 선택**: 구체적이고 명확한 키워드 사용
2. **날짜 범위**: 너무 넓지 않게 설정
3. **영상 수**: 처음에는 적은 수로 테스트
4. **네트워크**: 안정적인 인터넷 연결 확인
5. **브라우저**: Chrome 브라우저 권장 