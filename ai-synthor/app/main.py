from fastapi import FastAPI
from app.api.endpoints.generation import router as generation_router
# field_suggest.py 파일이 실제 존재하면 아래 라인 주석 해제
# from app.api.endpoints.field_suggest import router as field_suggest_router

app = FastAPI()

# 라우터 등록
app.include_router(generation_router, prefix="/api/generation", tags=["generation"])
# app.include_router(field_suggest_router, prefix="/api/fields", tags=["fields"])

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}
