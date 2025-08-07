# GitHub Personal Access Token 설정 가이드

## 🔑 GitHub 인증 문제 해결

현재 2개의 커밋이 로컬에 있지만 GitHub에 푸시할 수 없는 상태입니다.
다음 단계를 따라 Personal Access Token을 설정하세요.

## 📋 단계별 설정 방법

### 1단계: GitHub Personal Access Token 생성

1. **GitHub.com에 로그인**
2. **우측 상단 프로필 클릭 → Settings**
3. **좌측 메뉴에서 "Developer settings" 클릭**
4. **"Personal access tokens" → "Tokens (classic)" 클릭**
5. **"Generate new token" → "Generate new token (classic)" 클릭**

### 2단계: 토큰 설정

**토큰 설정:**
- **Note**: `youtube_crawler_access`
- **Expiration**: `90 days` (권장)
- **Scopes**: 다음 항목들 체크
  - ✅ `repo` (전체 저장소 접근)
  - ✅ `workflow` (GitHub Actions)

### 3단계: 토큰 복사 및 저장

1. **"Generate token" 클릭**
2. **생성된 토큰을 안전한 곳에 복사** (한 번만 표시됨!)
3. **예시**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 4단계: Git 원격 저장소 URL 업데이트

터미널에서 다음 명령어를 실행하세요:

```bash
# YOUR_TOKEN을 실제 토큰으로 교체
git remote set-url origin https://YOUR_TOKEN@github.com/saewookkangboy/youtube_crawler.git
```

**예시:**
```bash
git remote set-url origin https://ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/saewookkangboy/youtube_crawler.git
```

### 5단계: 푸시 실행

```bash
git push origin main
```

## 🔍 현재 상태 확인

### 로컬 커밋 상태:
- ✅ `📚 Add: GitHub setup guide and project documentation`
- ✅ `🔧 Fix: Streamlit plotly dependency and improve project structure`

### 대기 중인 작업:
- ⏳ GitHub 원격 저장소 푸시

## 🛠️ 대안 방법: SSH 키 설정

Personal Access Token 대신 SSH 키를 사용할 수도 있습니다:

### SSH 키 생성:
```bash
ssh-keygen -t ed25519 -C "chunghyo@kakao.com"
```

### SSH 키를 GitHub에 추가:
1. `~/.ssh/id_ed25519.pub` 파일 내용 복사
2. GitHub Settings → SSH and GPG keys → New SSH key
3. 키 내용 붙여넣기

### 원격 저장소 URL 변경:
```bash
git remote set-url origin git@github.com:saewookkangboy/youtube_crawler.git
```

## 📞 문제 해결

### 토큰이 작동하지 않는 경우:
1. 토큰이 올바르게 복사되었는지 확인
2. 토큰 권한이 `repo`로 설정되었는지 확인
3. 토큰이 만료되지 않았는지 확인

### SSH 키가 작동하지 않는 경우:
1. SSH 키가 GitHub에 올바르게 추가되었는지 확인
2. `ssh -T git@github.com` 명령어로 연결 테스트

## 🎯 성공 후 확인

푸시가 성공하면 다음을 확인하세요:
1. GitHub 저장소에서 커밋이 표시되는지 확인
2. `GITHUB_SETUP.md` 파일이 저장소에 추가되었는지 확인
3. `requirements.txt`에 plotly 의존성이 추가되었는지 확인

## 📝 참고사항

- Personal Access Token은 민감한 정보이므로 안전하게 보관하세요
- 토큰은 90일 후 만료되므로 주기적으로 갱신이 필요합니다
- 프로덕션 환경에서는 더 안전한 인증 방법을 사용하세요
