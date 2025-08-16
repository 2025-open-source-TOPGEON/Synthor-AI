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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 빠른 헬스 체크
@app.get("/healthz")
def healthz():
    return {"ok": True}

# 루트도 간단히 확인 가능하도록
@app.get("/")
def root():
    return {"service": "Synthor-AI", "status": "up"}

# 최종 경로: POST /api/fields/ai-suggest
app.include_router(generation_router, prefix="/api")
