from typing import List, Tuple, Optional
from .mappings import KOR_TO_ENG_FIELD, EN_TO_TYPE_FIELD

class FieldDetector:
    """입력 텍스트에서 가장 먼저 등장하는 타입명을 탐지"""
    def detect_first(self, text: str) -> Optional[str]:
        candidates: List[Tuple[str, int, str]] = []  # (타입, 위치, 키워드)

        # 비밀번호 관련 키워드 우선 확인 (높은 우선순위)
        password_keywords = ["비밀번호", "패스워드", "비번", "password"]
        password_constraint_keywords = ["대문자", "소문자", "숫자", "특수문자", "특수기호", "symbol", "uppercase", "lowercase", "numbers", "letters", "character", "characters"]
        has_password_context = any(keyword in text for keyword in password_keywords) or any(keyword in text for keyword in password_constraint_keywords)

        # 비밀번호 제약 조건 키워드가 있으면 우선적으로 password 반환
        if has_password_context:
            return "password"

        # 한글 키워드
        for kor, eng in KOR_TO_ENG_FIELD.items():
            idx = text.find(kor)
            if idx != -1:
                # 비밀번호 컨텍스트에서 길이 관련 키워드는 제외
                if has_password_context and eng == "number_between_1_100" and any(length_word in kor for length_word in ["길이", "최소 길이", "최소길이"]):
                    continue
                candidates.append((eng, idx, kor))

        # 영문 키워드 (소문자 비교)
        low = text.lower()
        for eng_key, eng_value in EN_TO_TYPE_FIELD.items():
            idx = low.find(eng_key.lower())
            if idx != -1:
                # 비밀번호 컨텍스트에서 길이 관련 키워드는 제외
                if has_password_context and eng_value == "number_between_1_100" and any(length_word in eng_key.lower() for length_word in ["length", "minimum length", "minimum"]):
                    continue
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
                                # 비밀번호 컨텍스트에서 길이 관련 키워드는 제외
                                if has_password_context and eng_value == "number_between_1_100" and any(length_word in phrase for length_word in ["length", "minimum length", "minimum"]):
                                    continue
                                candidates.append((eng_value, pidx, eng_key))

        if not candidates:
            return None

        # 위치가 같으면 더 긴 키워드 우선, 그 다음 위치 순
        candidates.sort(key=lambda x: (x[1], -len(x[2])))
        return candidates[0][0]
