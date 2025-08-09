# app/api/generation.py
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

# ── Parser: 네 서비스 경로에 맞춰 import
#   예) app/services/parser.py 안에 class Parser 존재
from app.services.parser import Parser

router = APIRouter()
parser = Parser()

# ── 요청 스키마
class PromptRequest(BaseModel):
    """신규 권장: prompt 키로 자연어를 전달"""
    prompt: str

class UnifiedRequest(BaseModel):
    """
    하위호환용: prompt 또는 text 둘 중 하나를 허용.
    Swagger에서도 prompt 예시가 기본으로 노출됨.
    """
    prompt: Optional[str] = None
    text: Optional[str] = None

    def get_text(self) -> str:
        if self.prompt:
            return self.prompt
        if self.text:
            return self.text
        raise ValueError("Either 'prompt' or 'text' is required.")

# ── 응답 스키마: Parser가 반환하는 포맷 그대로
class FieldConstraint(BaseModel):
    type: Optional[str]
    constraints: Dict[str, Any]
    nullablePercent: Optional[int]

# ── 엔드포인트: /api/generation/generate-json
@router.post(
    "/generate-json",
    response_model=FieldConstraint,
    summary="Generate Json",
    description=(
        "자연어 제약 조건을 분석해 {type, constraints, nullablePercent} 형식으로 반환합니다.\n"
        "요청은 prompt 또는 text로 보낼 수 있으며, prompt를 권장합니다."
    ),
    tags=["generation"],
)
def generate_json(
    req: UnifiedRequest = Body(
        ...,
        examples={
            "ko": {
                "summary": "한국어 예시",
                "value": {
                    "prompt": "비밀번호는 최소 10자 이상이고 숫자와 특수문자가 포함되어야 해"
                },
            },
            "en": {
                "summary": "영어 예시",
                "value": {
                    "prompt": "Password must be at least 10 characters and include a number and a special character."
                },
            },
            "legacy_text": {
                "summary": "하위호환(text) 예시",
                "value": {
                    "text": "휴대폰 번호는 한국 형식으로 만들어 줘. 20%는 비워도 돼."
                },
            },
        },
    )
):
    """
    Parser.parse_field_constraint() 호출 → 그대로 반환
    """
    try:
        text = req.get_text()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result: Dict[str, Any] = parser.parse_field_constraint(text)
    except Exception as e:
        # 내부 파서 오류까지 노출하지 않도록 500/메시지 최소화
        raise HTTPException(status_code=500, detail="Failed to parse constraints")

    # Parser가 이미 {"type":..., "constraints":..., "nullablePercent":...} 포맷을 반환
    return result
