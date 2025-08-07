#!/bin/bash

# YouTube Crawler - GitHub Token Push Script
echo "🚀 YouTube Crawler - GitHub 토큰 푸시 스크립트"
echo "================================================"

# 현재 상태 확인
echo "📊 현재 Git 상태 확인 중..."
git status

# Personal Access Token 입력 받기
echo ""
echo "🔑 GitHub Personal Access Token을 입력하세요:"
echo "   (토큰이 없다면 GITHUB_TOKEN_SETUP.md 파일을 참고하세요)"
read -s GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 토큰이 입력되지 않았습니다."
    exit 1
fi

echo ""
echo "✅ 토큰이 입력되었습니다."

# 원격 저장소 URL 업데이트
echo "🔧 원격 저장소 URL을 업데이트 중..."
git remote set-url origin https://${GITHUB_TOKEN}@github.com/saewookkangboy/youtube_crawler.git

# 변경된 파일들 스테이징
echo "📝 변경된 파일들을 스테이징 중..."
git add .

# 커밋 메시지 생성
COMMIT_DATE=$(date '+%Y-%m-%d %H:%M:%S')
COMMIT_MESSAGE="🔧 Update: GitHub token setup and documentation - $COMMIT_DATE"

echo "💾 커밋 중: $COMMIT_MESSAGE"
git commit -m "$COMMIT_MESSAGE"

# 원격 저장소로 푸시
echo "📤 원격 저장소로 푸시 중..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ GitHub 푸시 성공!"
    echo "📋 커밋 메시지: $COMMIT_MESSAGE"
    echo ""
    echo "🎉 모든 변경사항이 GitHub에 업로드되었습니다!"
    echo "📖 GitHub 저장소: https://github.com/saewookkangboy/youtube_crawler"
else
    echo ""
    echo "❌ GitHub 푸시 실패!"
    echo "🔧 다음을 확인해주세요:"
    echo "   1. 토큰이 올바른지 확인"
    echo "   2. 토큰 권한이 'repo'로 설정되었는지 확인"
    echo "   3. 저장소 접근 권한이 있는지 확인"
    echo ""
    echo "📖 자세한 설정 방법: GITHUB_TOKEN_SETUP.md"
fi

# 보안을 위해 토큰 변수 삭제
unset GITHUB_TOKEN
