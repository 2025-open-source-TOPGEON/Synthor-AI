# app/api/endpoints/generation.py
from typing import Any, Dict, Optional, List
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from app.services.constraint_parser import Parser  # constraint_parser의 Parser 클래스

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

# 새로운 auto-generate 요청 모델
class AutoGenerateRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="전체 목적 프롬프트",
        example="쇼핑몰에서 사용자 등록을 위한 정보",
    )

# 새로운 auto-generate 응답 모델
class FieldDefinition(BaseModel):
    name: str
    type: str
    constraints: Dict[str, Any] = {}
    nullablePercent: int = 0

class AutoGenerateResponse(BaseModel):
    count: int
    fields: List[FieldDefinition]

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

@router.post(
    "/fields/auto-generate",
    summary="전체 목적 프롬프트 → 필드 세트 자동 생성",
    description="사용자 입력 전체 목적 프롬프트를 받아 완전한 필드 세트를 반환합니다.",
    tags=["fields"],
    response_model=AutoGenerateResponse,
)
def auto_generate_fields(
    req: AutoGenerateRequest = Body(...),
):
    try:
        from app.services.system_prompt_processor import SystemPromptProcessor
        
        processor = SystemPromptProcessor()
        result = processor.process_system_prompt(req.prompt)
        return result
    except Exception as e:
        # 내부 예외 메시지는 숨기고 500만 전달
        raise HTTPException(status_code=500, detail="Failed to generate fields")
