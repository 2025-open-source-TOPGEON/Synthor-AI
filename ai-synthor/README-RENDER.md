# 🚀 Render로 AI Synthor 배포하기

## 📋 배포 준비사항

### 1. GitHub 저장소 준비
```bash
# Git 초기화 (아직 안했다면)
git init
git add .
git commit -m "Initial commit"

# GitHub에 푸시
git remote add origin https://github.com/your-username/ai-synthor.git
git push -u origin main
```

### 2. Render 계정 생성
- https://render.com 에서 무료 계정 생성
- GitHub 계정과 연결

## 🔧 배포 방법

### 방법 1: Render Dashboard 사용 (권장)

1. **New Web Service 클릭**
2. **Connect GitHub 선택**
3. **저장소 선택**: `ai-synthor`
4. **설정 입력**:
   - **Name**: `ai-synthor`
   - **Environment**: `Docker`
   - **Region**: `Oregon (US West)` 또는 가까운 지역
   - **Branch**: `main`
   - **Dockerfile Path**: `./Dockerfile`

5. **환경 변수 설정**:
   ```
   PORT = 8000
   ENV = production
   ```

6. **Deploy Web Service 클릭**

### 방법 2: render.yaml 사용

1. `render.yaml` 파일에서 GitHub URL 수정:
   ```yaml
   repo: https://github.com/your-username/ai-synthor.git
   ```

2. 저장소에 푸시 후 Render에서 "New Blueprint" 선택

## 🌐 배포 후 확인

배포 완료 후 다음 URL들로 접속:
- **앱**: `https://your-app-name.onrender.com`
- **API 문서**: `https://your-app-name.onrender.com/docs`
- **Redoc**: `https://your-app-name.onrender.com/redoc`

## 🔍 배포 상태 확인

### Render Dashboard에서:
1. **Logs** 탭에서 실시간 로그 확인
2. **Metrics** 탭에서 성능 모니터링
3. **Settings**에서 환경 변수 및 설정 변경

### 로컬에서 테스트:
```bash
# 배포된 앱 테스트
curl https://your-app-name.onrender.com/

# API 엔드포인트 테스트
curl https://your-app-name.onrender.com/api/generation/
```

## ⚙️ 고급 설정

### 커스텀 도메인 설정
1. Render Dashboard > Settings > Custom Domains
2. 도메인 입력 및 DNS 설정

### 자동 배포 설정
- `main` 브랜치에 푸시할 때마다 자동 배포
- Pull Request 미리보기 (Pro 플랜)

### 환경 변수 관리
```bash
# Render Dashboard에서 추가 가능한 환경 변수들
DATABASE_URL=your-database-url
SECRET_KEY=your-secret-key
DEBUG=False
```

## 🚨 주의사항

### 무료 플랜 제한사항:
- **Sleep 모드**: 15분 비활성 후 자동 절전
- **빌드 시간**: 월 500분 제한
- **대역폭**: 월 100GB 제한

### 성능 최적화:
- Docker 이미지 크기 최소화
- 불필요한 의존성 제거
- 캐싱 활용

## 🐛 트러블슈팅

### 일반적인 문제들

1. **빌드 실패**:
   ```bash
   # Dockerfile 문법 확인
   docker build -t test .
   ```

2. **포트 오류**:
   - Render는 자동으로 PORT 환경변수 설정
   - Dockerfile에서 `${PORT:-8000}` 사용 확인

3. **의존성 오류**:
   ```bash
   # requirements.txt 확인
   pip install -r requirements.txt
   ```

4. **로그 확인**:
   - Render Dashboard > Logs에서 실시간 로그 모니터링

### 배포 재시작
```bash
# Render Dashboard에서
Manual Deploy > Deploy Latest Commit
```
