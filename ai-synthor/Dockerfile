FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# 로그 버퍼링 끄기(중요: 크래시 트레이스가 바로 보임)
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# (선택) 헬스체크용 curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Render는 동적 포트. 반드시 sh -c 로 $PORT 평가!
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level debug"]

# 선택: 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --retries=5 CMD curl -fsS http://localhost:${PORT:-8000}/healthz || exit 1
