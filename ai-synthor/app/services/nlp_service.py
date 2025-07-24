from app.utils.language_detect import detect_supported_language

# 임시 더미 함수 (한국어 전용 처리기)
def process_korean(text: str) -> dict:
    """
    한국어 입력에 대한 처리 함수.
    실제 구현에서는 전처리, 파싱, JSON 변환 등을 수행할 수 있다.
    """
    return {
        "language": "ko",
        "parsed": {
            "text": text,
            "note": "한국어 처리 결과 예시입니다."
        }
    }

# 임시 더미 함수 (영어 전용 처리기)
def process_english(text: str) -> dict:
    """
    영어 입력에 대한 처리 함수.
    실제 구현에서는 전처리, 파싱, JSON 변환 등을 수행할 수 있다.
    """
    return {
        "language": "en",
        "parsed": {
            "text": text,
            "note": "English processing result example."
        }
    }

# 전체 파이프라인: 입력 → 언어 감지 → 언어별 처리 → 결과 JSON 반환
def convert_text_to_json(text: str) -> dict:
    """
    주어진 자연어 문장을 언어 감지 후, 해당 언어에 맞는 처리기로 전달하고
    처리 결과를 JSON 형태로 반환한다.
    지원 언어: 'ko', 'en'
    기타 언어: 'unsupported' 응답 반환
    """
    lang = detect_supported_language(text)  # 언어 감지 ('ko', 'en', 'unsupported')

    if lang == "ko":
        return process_korean(text)
    elif lang == "en":
        return process_english(text)
    else:
        # 지원하지 않는 언어에 대한 응답
        return {
            "language": "unsupported",
            "error": "지원하지 않는 언어입니다. Korean(ko) 또는 English(en)만 입력해주세요."
        }
