#!/bin/bash

# 유튜브 크롤러 웹 서비스 시작 스크립트

echo "🎥 유튜브 크롤러 웹 서비스 시작"
echo "=================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "📦 가상환경을 활성화합니다..."
    source venv/bin/activate
else
    echo "❌ 가상환경을 찾을 수 없습니다. 먼저 설치를 완료해주세요."
    exit 1
fi

# 필요한 패키지 확인
echo "🔧 패키지 상태를 확인합니다..."
pip show streamlit > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "📦 필요한 패키지를 설치합니다..."
    pip install -r requirements.txt
fi

# 포트 사용 가능 여부 확인
PORT=8501
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  포트 $PORT가 이미 사용 중입니다."
    echo "다른 포트를 사용하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "사용할 포트 번호를 입력하세요 (기본값: 8502):"
        read -r new_port
        PORT=${new_port:-8502}
    else
        echo "기존 프로세스를 종료하고 포트 $PORT를 사용합니다."
        pkill -f "streamlit.*app.py"
        sleep 2
    fi
fi

# 웹 서비스 시작
echo "🌐 웹 서비스를 시작합니다..."
echo "📍 접속 주소: http://localhost:$PORT"
echo "🔄 서비스를 중지하려면 Ctrl+C를 누르세요."
echo ""

# Streamlit 실행
streamlit run app.py --server.port $PORT --server.address localhost --server.headless true 