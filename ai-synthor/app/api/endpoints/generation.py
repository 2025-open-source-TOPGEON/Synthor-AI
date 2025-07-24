from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.nlp_service import convert_text_to_json

#FastAPI 라우터 파일 generation.py 생성
router = APIRouter()

#요청 스키마 정의 (Request Body에 들어올 text 필드 정의)
class TextRequest(BaseModel):
    text: str

#POST API 생성 및 자동 Swagger 등록
@router.post("/generate-json")
def generate_json(request: TextRequest):
    """
    자연어 문장을 받아 언어 감지 후, 해당 언어 처리기를 통해 JSON 구조로 반환
    """
    #convert_text_to_json() 호출하여 언어 별 처리 결과 반환
    result = convert_text_to_json(request.text)

    #언어 감지 실패 또는 미지원 언어인 경우 메시지 반환
    if result.get("language") == "unsupported":
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result