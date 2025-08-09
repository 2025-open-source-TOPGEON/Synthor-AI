from fastapi import FastAPI
from app.api.endpoints import generation, field_suggest

app = FastAPI()

# 라우터 등록
app.include_router(generation.router, prefix="/api/generation", tags=["generation"])
app.include_router(field_suggest.router, prefix="/api/fields", tags=["fields"])

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}