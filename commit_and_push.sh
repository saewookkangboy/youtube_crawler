#!/bin/bash

# YouTube Crawler - Git Commit & Push Script
echo "🚀 YouTube Crawler - Git 커밋 및 푸시 시작"

# 현재 상태 확인
echo "📊 현재 Git 상태 확인 중..."
git status

# 변경된 파일들 스테이징
echo "📝 변경된 파일들을 스테이징 중..."
git add .

# 커밋 메시지 생성 (현재 날짜와 시간 포함)
COMMIT_DATE=$(date '+%Y-%m-%d %H:%M:%S')
COMMIT_MESSAGE="🔧 Fix: Streamlit plotly dependency and improve project structure - $COMMIT_DATE"

echo "💾 커밋 중: $COMMIT_MESSAGE"
git commit -m "$COMMIT_MESSAGE"

# 원격 저장소로 푸시
echo "📤 원격 저장소로 푸시 중..."
git push origin main

echo "✅ Git 커밋 및 푸시 완료!"
echo "📋 커밋 메시지: $COMMIT_MESSAGE"
