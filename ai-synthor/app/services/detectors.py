from typing import List, Tuple, Optional
from .mappings import KOR_TO_ENG_FIELD, EN_TO_TYPE_FIELD

class FieldDetector:
    """입력 텍스트에서 가장 먼저 등장하는 타입명을 탐지"""
    def detect_first(self, text: str) -> Optional[str]:
        candidates: List[Tuple[str, int, str]] = []  # (타입, 위치, 키워드)

        # 한글 키워드
        for kor, eng in KOR_TO_ENG_FIELD.items():
            idx = text.find(kor)
            if idx != -1:
                candidates.append((eng, idx, kor))

        # 영문 키워드 (소문자 비교)
        low = text.lower()
        for eng_key, eng_value in EN_TO_TYPE_FIELD.items():
            idx = low.find(eng_key.lower())
            if idx != -1:
                candidates.append((eng_value, idx, eng_key))

            # 공백 구문 보강
            if " " in eng_key:
                words = eng_key.split()
                parts = text.split()
                for i in range(len(parts)):
                    if i + len(words) <= len(parts):
                        phrase = " ".join(parts[i:i+len(words)]).lower()
                        if phrase == eng_key.lower():
                            pidx = low.find(phrase)
                            if pidx != -1:
                                candidates.append((eng_value, pidx, eng_key))

        if not candidates:
            return None

        # 위치가 같으면 더 긴 키워드 우선, 그 다음 위치 순
        candidates.sort(key=lambda x: (x[1], -len(x[2])))
        return candidates[0][0]
