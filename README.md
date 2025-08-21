# Synthor-AI

**자연어로 데이터 필드 제약조건을 자동 생성하는 AI 서비스**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 개요

Synthor-AI는 자연어 설명을 통해 데이터베이스 필드의 제약조건을 자동으로 생성하는 AI 서비스입니다. 개발자가 "비밀번호는 최소 10자 이상이고 숫자와 특수문자가 포함되어야 해"와 같은 자연어 설명을 입력하면, AI가 이를 분석하여 적절한 필드 타입과 제약조건을 자동으로 생성합니다.

### 주요 기능

- **개별 필드 제약조건 생성**: 자연어로 필드 설명을 입력하면 제약조건 자동 생성
- **전체 필드 세트 자동 생성**: 시스템 목적을 설명하면 필요한 모든 필드 자동 생성
- **다국어 지원**: 한국어와 영어 자연어 처리 지원
- **다양한 데이터 타입**: 비밀번호, 이메일, 전화번호, 날짜/시간, 신용카드 등 20+ 타입 지원
- **RESTful API**: FastAPI 기반의 현대적인 API 제공
- **Docker 지원**: 컨테이너화된 배포 환경

## 빠른 시작

### Docker로 실행 (권장)

```bash
# 저장소 클론
git clone https://github.com/your-username/synthor-ai.git
cd synthor-ai/ai-synthor

# Docker Compose로 실행
docker-compose up -d

# 또는 자동 배포 스크립트 사용
chmod +x deploy.sh
./deploy.sh
```

### 로컬 개발 환경

```bash
# Python 3.11+ 설치 필요
cd ai-synthor

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 접속 정보

- **애플리케이션**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **API 문서 (ReDoc)**: http://localhost:8000/redoc
- **헬스체크**: http://localhost:8000/healthz

## API 사용법

### 1. 개별 필드 제약조건 생성

```bash
curl -X POST "http://localhost:8000/api/fields/ai-suggest" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "비밀번호는 최소 10자 이상이고 숫자와 특수문자가 포함되어야 해"
  }'
```

**응답 예시:**
```json
{
  "type": "password",
  "constraints": {
    "min_length": 10,
    "require_digits": true,
    "require_special_chars": true
  },
  "nullablePercent": 0
}
```

### 2. 전체 필드 세트 자동 생성

```bash
curl -X POST "http://localhost:8000/api/fields/auto-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "쇼핑몰에서 사용자 등록을 위한 정보"
  }'
```

**응답 예시:**
```json
{
  "count": 8,
  "fields": [
    {
      "name": "full_name",
      "type": "full_name",
      "constraints": {},
      "nullablePercent": 0
    },
    {
      "name": "email",
      "type": "email_address",
      "constraints": {},
      "nullablePercent": 0
    },
    {
      "name": "password",
      "type": "password",
      "constraints": {
        "min_length": 8,
        "require_digits": true,
        "require_special_chars": true
      },
      "nullablePercent": 0
    }
  ]
}
```

## 프로젝트 구조

```
ai-synthor/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── generation.py      # API 엔드포인트
│   ├── services/
│   │   ├── constraints/           # 제약조건 추출기들
│   │   │   ├── base.py           # 기본 추출기 인터페이스
│   │   │   ├── password.py       # 비밀번호 제약조건
│   │   │   ├── email.py          # 이메일 제약조건
│   │   │   ├── phone.py          # 전화번호 제약조건
│   │   │   └── ...               # 기타 제약조건들
│   │   ├── constraint_parser.py  # 메인 파서
│   │   ├── system_prompt_processor.py  # 전체 필드 생성
│   │   ├── korean_processor.py   # 한국어 처리
│   │   └── english_processor.py  # 영어 처리
│   ├── schemas/
│   │   └── nlp.py               # Pydantic 스키마
│   └── main.py                  # FastAPI 앱
├── Dockerfile                   # Docker 설정
├── docker-compose.yml          # Docker Compose 설정
├── requirements.txt            # Python 의존성
└── deploy.sh                   # 자동 배포 스크립트
```

## 지원하는 데이터 타입

### 기본 타입
- **비밀번호** (`password`): 길이, 문자 조합 제약조건
- **이메일** (`email_address`): 이메일 형식 검증
- **전화번호** (`phone`): 국가별 전화번호 형식
- **날짜/시간** (`datetime`): 날짜 범위, 형식 지정
- **시간** (`time`): 시간 형식 및 범위
- **URL** (`url`): URL 형식 검증
- **신용카드** (`credit_card_number`, `credit_card_type`): 카드 번호 및 타입
- **문단** (`paragraphs`): 문단 수 및 길이 제약조건

### 개인정보 타입
- **이름** (`full_name`, `first_name`, `last_name`)
- **주소** (`address`, `street_address`, `city`, `state`, `country`, `postal_code`)
- **회사 정보** (`company_name`, `job_title`, `department_corporate`, `department_retail`)

### 한국어 특화 타입
- **한국어 이름** (`korean_full_name`, `korean_first_name`, `korean_last_name`)
- **한국어 주소** (`korean_address`, `korean_street_address`, `korean_city`, `korean_state`, `korean_country`)
- **한국어 회사 정보** (`korean_company_name`, `korean_job_title`)

### 기타 타입
- **아바타** (`avatar`): 프로필 이미지
- **숫자 범위** (`number_between`): 최소/최대값 제약조건
- **제품 정보** (`product_name`, `product_category`, `product_description`, `product_price`)
- **기술 정보** (`mac_address`, `ip_v4_address`, `ip_v6_address`, `user_agent`)

## 다국어 지원

### 한국어 예시
```json
{
  "prompt": "사용자 이름은 한국어로 2-4글자여야 하고, 이메일은 필수입니다"
}
```

### 영어 예시
```json
{
  "prompt": "User name should be 2-4 characters in Korean, and email is required"
}
```

## Docker 배포

### 단일 컨테이너
```bash
docker build -t synthor-ai .
docker run -d -p 8000:8000 --name synthor-ai synthor-ai
```

### Docker Compose (권장)
```bash
docker-compose up -d --build
```

### 클라우드 배포
- **AWS EC2**: `docker-compose up -d`
- **Google Cloud Run**: `gcloud run deploy`
- **Azure Container Instances**: `az container create`
- **Render**: `render.yaml` 설정 파일 제공

## 보안

- CORS 설정으로 웹 브라우저 접근 허용
- 입력 검증을 위한 Pydantic 스키마 사용
- 환경 변수를 통한 설정 관리
- 헬스체크 엔드포인트 제공

## 테스트

```bash
# API 테스트
curl -X GET "http://localhost:8000/healthz"

# Swagger UI를 통한 인터랙티브 테스트
# http://localhost:8000/docs 접속
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/your-username/synthor-ai/issues)
- **문서**: [API 문서](http://localhost:8000/docs)
- **이메일**: your-email@example.com

## 감사의 말

이 프로젝트는 다음과 같은 오픈소스 프로젝트들을 기반으로 합니다:

- [FastAPI](https://fastapi.tiangolo.com/) - 현대적인 웹 API 프레임워크
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 데이터 검증 라이브러리
- [Uvicorn](https://www.uvicorn.org/) - ASGI 서버
