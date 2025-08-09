FROM python:3.11-slim

WORKDIR /app

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY app/ ./app/

# 포트 노출 (Render에서는 동적 포트 사용)
EXPOSE 8000

# 애플리케이션 실행 (Render의 PORT 환경변수 사용)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

