from langdetect import detect

def detect_supported_language(text: str) -> str:
    """
    주어진 텍스트의 언어를 감지하고,
    'ko' 또는 'en'인 경우만 반환한다.
    그 외 언어는 'unsupported'를 반환한다.
    """
    try:
        lang = detect(text)
        if lang in ["ko", "en"]:
            return lang
        else:
            return "unsupported"
    except Exception:
        return "unsupported"