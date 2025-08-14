import re

class GlobalQualifiersExtractor:
    """성별/언어/나이/도메인 등 전역 보조 제약"""
    def extract(self, text: str) -> dict:
        c = {}
        low = text.lower()
        if "여자" in text or "female" in low: c["gender"] = "female"
        if "남자" in text or "male" in low:   c["gender"] = "male"
        if "영어" in text or "english" in low: c["lang"] = "en"
        if "한국어" in text or "korean" in low: c["lang"] = "ko"
        m = re.search(r"(\d+)세 미만|under (\d+)", text)
        if m:
            c["max"] = int(m.group(1) or m.group(2)) - 1  # 배타적 처리
        if "gmail" in low:
            c["domain"] = "gmail.com"
        return c
