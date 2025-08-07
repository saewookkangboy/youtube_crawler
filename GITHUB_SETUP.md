# GitHub 설정 및 커밋 가이드

## 🔧 문제 해결 완료

### ✅ 해결된 문제들:
1. **Streamlit plotly 의존성 오류** - `requirements.txt`에 `plotly>=5.17.0` 추가
2. **프로젝트 구조 개선** - `.gitignore` 파일 업데이트
3. **자동화 스크립트** - `commit_and_push.sh` 생성

### 📦 설치된 패키지:
- `plotly>=5.17.0` - 데이터 시각화
- `streamlit>=1.28.0` - 웹 인터페이스
- `selenium>=4.15.0` - 웹 크롤링
- 기타 모든 필요한 의존성 패키지들

## 🚀 GitHub 인증 설정

### 방법 1: Personal Access Token 사용 (권장)

1. **GitHub에서 Personal Access Token 생성:**
   - GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - "Generate new token" 클릭
   - 권한 설정: `repo`, `workflow` 체크
   - 토큰 생성 후 복사 (한 번만 표시됨)

2. **Git 설정 업데이트:**
   ```bash
   git config --global user.name "saewookkangboy"
   git config --global user.email "chunghyo@kakao.com"
   ```

3. **원격 저장소 URL 업데이트 (토큰 포함):**
   ```bash
   # YOUR_TOKEN을 실제 토큰으로 교체하세요
   git remote set-url origin https://YOUR_TOKEN@github.com/saewookkangboy/youtube_crawler.git
   ```

### 방법 2: SSH 키 사용

1. **SSH 키 생성:**
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```

2. **SSH 키를 GitHub에 추가:**
   - `~/.ssh/id_ed25519.pub` 파일 내용을 GitHub Settings → SSH and GPG keys에 추가

3. **원격 저장소 URL을 SSH로 변경:**
   ```bash
   git remote set-url origin git@github.com:saewookkangboy/youtube_crawler.git
   ```

## 📝 커밋 및 푸시 방법

### 자동화 스크립트 사용 (권장):
```bash
./commit_and_push.sh
```

### 수동 커밋:
```bash
# 변경사항 스테이징
git add .

# 커밋
git commit -m "🔧 Fix: Streamlit plotly dependency and improve project structure"

# 푸시
git push origin main
```

## 🎯 Streamlit 앱 실행

### 로컬에서 실행:
```bash
# 가상환경 활성화
source venv/bin/activate

# Streamlit 앱 실행
streamlit run app.py --server.port 8501
```

### Streamlit Cloud에서 배포:
1. GitHub 저장소를 Streamlit Cloud에 연결
2. 메인 파일: `app.py`
3. Python 버전: 3.9+
4. 패키지 파일: `requirements.txt`

## 📊 현재 상태

### ✅ 완료된 작업:
- [x] plotly 의존성 추가
- [x] .gitignore 파일 업데이트
- [x] 자동화 스크립트 생성
- [x] 로컬 테스트 완료
- [x] 가상환경 설정

### 🔄 진행 중인 작업:
- [ ] GitHub 인증 설정
- [ ] 원격 저장소 푸시

### 📋 다음 단계:
1. GitHub 인증 설정 완료
2. 변경사항 원격 저장소에 푸시
3. Streamlit Cloud 배포 (선택사항)

## 🛠️ 문제 해결

### Streamlit 오류가 계속 발생하는 경우:
```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Git 인증 오류:
```bash
# 현재 원격 저장소 확인
git remote -v

# HTTPS에서 SSH로 변경 (SSH 키 설정 후)
git remote set-url origin git@github.com:saewookkangboy/youtube_crawler.git
```

## 📞 지원

문제가 지속되는 경우:
1. GitHub 토큰이 올바르게 설정되었는지 확인
2. 저장소 권한이 있는지 확인
3. 네트워크 연결 상태 확인
