from fastapi import FastAPI
from app.api.endpoints.generation import router as generation_router

app = FastAPI(
    title="Synthor-AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 최종 경로: POST /api/fields/ai-suggest
app.include_router(generation_router, prefix="/api")
