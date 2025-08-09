#!/bin/bash
# Render 배포용 시작 스크립트

# 환경 변수 설정
export PORT=${PORT:-8000}

# 애플리케이션 시작
uvicorn app.main:app --host 0.0.0.0 --port $PORT



