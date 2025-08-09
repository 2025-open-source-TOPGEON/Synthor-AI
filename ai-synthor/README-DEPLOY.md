# AI Synthor 배포 가이드

## 🚀 빠른 시작

### 방법 1: 자동 배포 스크립트 (권장)
```bash
cd ai-synthor
chmod +x deploy.sh
./deploy.sh
```

### 방법 2: Docker Compose 수동 배포
```bash
cd ai-synthor
docker-compose up -d --build
```

### 방법 3: 단순 Docker 배포
```bash
cd ai-synthor
docker build -t ai-synthor .
docker run -d -p 8000:8000 --name ai-synthor ai-synthor
```

## 🌐 접속 정보

- **애플리케이션**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **Redoc 문서**: http://localhost:8000/redoc

## 🔧 관리 명령어

### 서비스 상태 확인
```bash
docker-compose ps
docker-compose logs -f ai-synthor
```

### 서비스 중지
```bash
docker-compose down
```

### 서비스 재시작
```bash
docker-compose restart
```

### 로그 확인
```bash
docker-compose logs -f
```

## ☁️ 클라우드 배포

### AWS EC2 배포
1. EC2 인스턴스 생성 (Ubuntu 22.04 권장)
2. Docker 및 Docker Compose 설치
3. 프로젝트 클론 후 위 명령어 실행

### Google Cloud Run 배포
```bash
# Google Cloud SDK 설치 후
gcloud builds submit --tag gcr.io/[PROJECT-ID]/ai-synthor
gcloud run deploy ai-synthor --image gcr.io/[PROJECT-ID]/ai-synthor --platform managed --port 8000
```

### Azure Container Instances 배포
```bash
# Azure CLI 설치 후
az container create --resource-group myResourceGroup --name ai-synthor --image ai-synthor --ports 8000
```

## 🔒 보안 설정

### 환경 변수 설정
`.env` 파일 생성:
```env
ENV=production
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,localhost
```

### HTTPS 설정 (Nginx + Let's Encrypt)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 모니터링

### 헬스체크
```bash
curl http://localhost:8000/
```

### 리소스 사용량 확인
```bash
docker stats ai-synthor
```

## 🐛 트러블슈팅

### 일반적인 문제들

1. **포트 충돌**: 8000번 포트가 사용 중인 경우
   ```bash
   docker-compose down
   sudo lsof -i :8000
   ```

2. **메모리 부족**: Docker 메모리 제한 증가
   ```yaml
   # docker-compose.yml에 추가
   mem_limit: 512m
   ```

3. **로그 확인**: 오류 발생 시
   ```bash
   docker-compose logs ai-synthor
   ```



