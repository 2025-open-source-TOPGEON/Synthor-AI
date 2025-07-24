from pydantic import BaseModel

#요청 스키마 정의
class TextRequest(BaseModel):
    text: str

#응답 스키마 정의
class ParsedResult(BaseModel):
    text: str
    note: str

class JsonResponse(BaseModel):
    language: str
    parsed: ParsedResult