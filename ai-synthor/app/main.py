from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.generation import router as generation_router

app = FastAPI(
    title="Synthor-AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS 미들웨어 추가 (개발 환경에서 캐시 문제 해결)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 최종 경로: POST /api/fields/ai-suggest
app.include_router(generation_router, prefix="/api")
