# Streamlit Cloud 배포 가이드

## 🚀 Streamlit Cloud 배포 완료!

### ✅ 배포 준비 완료된 항목들:

1. **의존성 패키지 최적화** - `requirements.txt` 정리
2. **Streamlit 설정** - `.streamlit/config.toml` 생성
3. **GitHub 커밋** - 모든 변경사항 업로드 완료
4. **plotly 의존성** - 데이터 시각화 패키지 추가

## 📋 Streamlit Cloud 배포 단계

### 1단계: Streamlit Cloud 접속
1. **https://share.streamlit.io** 접속
2. **GitHub 계정으로 로그인**

### 2단계: 새 앱 생성
1. **"New app" 버튼 클릭**
2. **저장소 선택**: `saewookkangboy/youtube_crawler`
3. **브랜치 선택**: `main`

### 3단계: 앱 설정
```
Repository: saewookkangboy/youtube_crawler
Branch: main
Main file path: app.py
```

### 4단계: 고급 설정 (선택사항)
```
Python version: 3.9
Requirements file: requirements.txt
```

### 5단계: 배포 실행
1. **"Deploy!" 버튼 클릭**
2. **배포 완료까지 대기** (약 2-3분)

## 🔧 배포 후 확인사항

### ✅ 정상 작동 확인:
- [ ] 앱이 정상적으로 로드되는지 확인
- [ ] plotly 차트가 표시되는지 확인
- [ ] YouTube 크롤링 기능이 작동하는지 확인

### ⚠️ 문제 발생 시 해결방법:

#### 1. plotly 오류가 발생하는 경우:
```bash
# requirements.txt에 plotly가 포함되어 있는지 확인
grep plotly requirements.txt
```

#### 2. ChromeDriver 오류가 발생하는 경우:
```bash
# packages.txt에 chromium이 포함되어 있는지 확인
cat packages.txt
```

#### 3. 메모리 부족 오류:
- Streamlit Cloud 설정에서 메모리 할당량 증가
- 불필요한 패키지 제거

## 📊 현재 프로젝트 상태

### ✅ 완료된 작업:
- [x] GitHub 커밋 및 푸시 완료
- [x] plotly 의존성 추가
- [x] requirements.txt 최적화
- [x] Streamlit 설정 파일 생성
- [x] 로컬 테스트 완료

### 🎯 배포 URL:
배포 완료 후 다음 URL에서 앱에 접근할 수 있습니다:
```
https://youtube-crawler-{username}.streamlit.app
```

## 🛠️ 로컬 테스트

배포 전 로컬에서 테스트:
```bash
# 가상환경 활성화
source venv/bin/activate

# Streamlit 앱 실행
streamlit run app.py --server.port 8501
```

## 📝 배포 후 관리

### 업데이트 방법:
1. **로컬에서 코드 수정**
2. **GitHub에 커밋 및 푸시**
3. **Streamlit Cloud에서 자동 재배포**

### 모니터링:
- Streamlit Cloud 대시보드에서 앱 상태 확인
- 로그 확인으로 오류 디버깅

## 🎉 성공 메시지

배포가 성공하면 다음과 같은 메시지가 표시됩니다:
```
✅ Your app is now live at: https://youtube-crawler-{username}.streamlit.app
```

## 📞 문제 해결

### 일반적인 문제들:
1. **의존성 충돌**: requirements.txt에서 버전 충돌 해결
2. **메모리 부족**: 불필요한 패키지 제거
3. **ChromeDriver 오류**: packages.txt 확인

### 지원:
- Streamlit Cloud 문서: https://docs.streamlit.io/streamlit-community-cloud
- GitHub Issues: 프로젝트 저장소에서 이슈 등록
