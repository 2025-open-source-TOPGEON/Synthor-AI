#!/bin/bash

# AI Synthor 배포 스크립트

set -e

echo "🚀 AI Synthor 배포를 시작합니다..."

# 환경 변수 설정
export COMPOSE_PROJECT_NAME=ai-synthor

# 기존 컨테이너 정리
echo "📦 기존 컨테이너 정리 중..."
docker-compose down --remove-orphans

# 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose build --no-cache

# 서비스 시작
echo "▶️ 서비스 시작 중..."
docker-compose up -d

# 헬스체크 대기
echo "🏥 헬스체크 대기 중..."
timeout 60 bash -c 'until curl -s http://localhost:8000/ > /dev/null; do sleep 2; done'

if [ $? -eq 0 ]; then
    echo "✅ 배포가 성공적으로 완료되었습니다!"
    echo "🌐 애플리케이션이 http://localhost:8000 에서 실행 중입니다."
    echo "📖 API 문서: http://localhost:8000/docs"
else
    echo "❌ 배포 중 오류가 발생했습니다. 로그를 확인해주세요:"
    docker-compose logs
    exit 1
fi
