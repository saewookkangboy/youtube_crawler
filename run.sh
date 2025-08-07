#!/bin/bash

# 유튜브 크롤러 실행 스크립트

echo "🎥 유튜브 크롤러 및 데이터 정리 서비스"
echo "=================================="

# Python 가상환경 확인
if [ -d "venv" ]; then
    echo "📦 가상환경을 활성화합니다..."
    source venv/bin/activate
fi

# 필요한 패키지 설치 확인
echo "🔧 필요한 패키지를 확인합니다..."
pip install -r requirements.txt

# 실행 방법 선택
echo ""
echo "실행 방법을 선택하세요:"
echo "1. 웹 인터페이스 (권장)"
echo "2. 명령줄 인터페이스"
echo "3. 종료"
echo ""
read -p "선택 (1-3): " choice

case $choice in
    1)
        echo "🌐 웹 인터페이스를 시작합니다..."
        echo "브라우저에서 http://localhost:8501 로 접속하세요."
        streamlit run app.py
        ;;
    2)
        echo "💻 명령줄 인터페이스를 시작합니다..."
        python main.py
        ;;
    3)
        echo "👋 종료합니다."
        exit 0
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac 