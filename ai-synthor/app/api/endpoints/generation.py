# app/api/endpoints/generation.py
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from app.services.parser import Parser  # Parser 클래스

router = APIRouter()
parser = Parser()

# 요청: prompt만 받음 (Swagger 기본값을 example로 지정)
class PromptRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="자연어 제약 설명",
        example="비밀번호는 최소 10자 이상이고 숫자와 특수문자가 포함되어야 해",
    )

# 응답: Parser 포맷 그대로
class FieldConstraint(BaseModel):
    type: Optional[str]
    constraints: Dict[str, Any]
    nullablePercent: Optional[int]

@router.post(
    "/fields/ai-suggest",
    summary="개별 필드 프롬프트 → 제약 추론",
    description="prompt 한 줄을 받아 Parser.parse_field_constraint() 결과를 그대로 반환합니다.",
    tags=["fields"],
    response_model=FieldConstraint,
    response_model_exclude_none=False,  # None도 그대로 노출
)
def ai_suggest(
    req: PromptRequest = Body(...),
):
    try:
        # 가공 없이 원본 그대로 반환
        result: Dict[str, Any] = parser.parse_field_constraint(req.prompt)
        return result
    except Exception:
        # 내부 예외 메시지는 숨기고 500만 전달
        raise HTTPException(status_code=500, detail="Failed to parse constraints")
