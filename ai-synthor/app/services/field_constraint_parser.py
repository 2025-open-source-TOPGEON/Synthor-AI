"""
Object-oriented field constraint parser.
"""
import re
from typing import Dict, Any, List, Tuple, Optional

from .field_constants import (
    SUPPORTED_TYPES, CONSTRAINT_TYPES, KOR_TO_ENG_FIELD, EN_TO_TYPE_FIELD
)
from .nullable_percent_parser import NullablePercentParser
from .constraint_parsers import ConstraintParserFactory


class FieldIdentifier:
    """Identifies field types from natural language text."""
    
    def __init__(self):
        self.korean_mappings = KOR_TO_ENG_FIELD
        self.english_mappings = EN_TO_TYPE_FIELD
    
    def find_field_candidates(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Find all field type candidates in text.
        
        Returns:
            List of (field_type, matched_text, position) tuples
        """
        candidates = []
        
        # 한국어 필드 검색
        for kor_text, eng_type in self.korean_mappings.items():
            idx = text.find(kor_text)
            if idx != -1:
                candidates.append((eng_type, kor_text, idx))
        
        # 영어 필드 검색
        for eng_key, eng_type in self.english_mappings.items():
            # 정확한 매칭
            idx = text.lower().find(eng_key.lower())
            if idx != -1:
                candidates.append((eng_type, eng_key, idx))
            
            # 공백이 있는 경우도 처리
            if " " in eng_key:
                words = eng_key.split()
                text_words = text.split()
                for i in range(len(text_words)):
                    if i + len(words) <= len(text_words):
                        phrase = " ".join(text_words[i:i+len(words)]).lower()
                        if phrase == eng_key.lower():
                            candidates.append((eng_type, eng_key, text.lower().find(phrase)))
        
        # 유효한 후보만 반환 (위치가 -1이 아닌 것)
        return [c for c in candidates if c[2] != -1]
    
    def get_first_field_type(self, text: str) -> Optional[str]:
        """Get the first field type found in text."""
        candidates = self.find_field_candidates(text)
        if not candidates:
            return None
        
        # 가장 먼저 등장하는 필드 반환
        candidates.sort(key=lambda x: x[2])
        return candidates[0][0]


class GeneralConstraintParser:
    """Parses general constraints that apply to multiple field types."""
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse general constraints from text."""
        constraints = {}
        
        # Gender constraints
        if "여자" in text or "female" in text:
            constraints["gender"] = "female"
        if "남자" in text or "male" in text:
            constraints["gender"] = "male"
        
        # Language constraints
        if "영어" in text or "english" in text:
            constraints["lang"] = "en"
        if "한국어" in text or "korean" in text:
            constraints["lang"] = "ko"
        
        # Age constraints
        age_match = re.search(r"(\d+)세 미만|under (\d+)", text)
        if age_match:
            constraints["max"] = int(age_match.group(1) or age_match.group(2))
        
        # Domain constraints
        if "gmail" in text.lower():
            constraints["domain"] = "gmail.com"
        
        return constraints


class FieldConstraintParser:
    """Main field constraint parser using object-oriented design."""
    
    def __init__(self):
        self.field_identifier = FieldIdentifier()
        self.nullable_parser = NullablePercentParser()
        self.general_parser = GeneralConstraintParser()
        self.constraint_factory = ConstraintParserFactory()
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse field constraints from natural language text.
        
        Args:
            text: Input text to parse
            
        Returns:
            Dictionary with type, constraints, and nullablePercent
        """
        # 1. 필드 타입 식별
        field_type = self.field_identifier.get_first_field_type(text)
        if not field_type:
            return self._create_null_response()
        
        # 2. nullable percentage 파싱
        nullable_percent = self.nullable_parser.parse(text)
        
        # 3. 일반 constraints 파싱
        constraints = self.general_parser.parse(text)
        
        # 4. 필드별 특수 constraints 파싱
        if field_type in CONSTRAINT_TYPES:
            try:
                specific_constraints = self._parse_specific_constraints(field_type, text)
                if specific_constraints:
                    constraints.update(specific_constraints)
            except ValueError:
                # 지원하지 않는 값이 있는 경우
                return self._create_null_response()
        
        # 5. 결과 반환
        return {
            "type": field_type,
            "constraints": constraints,
            "nullablePercent": nullable_percent
        }
    
    def _parse_specific_constraints(self, field_type: str, text: str) -> Optional[Dict[str, Any]]:
        """Parse field-specific constraints."""
        parser = self.constraint_factory.get_parser(field_type)
        if parser:
            return parser.parse(text)
        return None
    
    def _create_null_response(self) -> Dict[str, Any]:
        """Create null response for unsupported or error cases."""
        return {
            "type": None,
            "constraints": {},
            "nullablePercent": None
        }


# Backward compatibility function
def parse_field_constraint(text: str) -> Dict[str, Any]:
    """
    Parse field constraint from text (backward compatibility function).
    
    Args:
        text: Input text to parse
        
    Returns:
        Dictionary with type, constraints, and nullablePercent
    """
    parser = FieldConstraintParser()
    return parser.parse(text)


if __name__ == "__main__":
    # Test cases
    test_cases = [
        # 혼합 입력, 에러, edge case 등
        "이름은 영어로, 주소는 한국어로 3개",
        "여자 이름만",
        "40세 미만",
        "Gmail만",
        "주소는 한국어로, 이름은 영어로 3개",
        "email은 gmail만, 20세 미만",
        "없는타입",
        "이름, 없는조건",
        "비밀번호 8자 이상, 대문자 1개, 숫자 1개 2개",
        "paragraphs at least 2, no more than 4",
        "phone, gmail only, number over 10",
        "Generate 10 users with Gmail emails under 40 years old",
        "Create 5 samples, full name, email address only gmail, age over 20",
        "10 users, phone number, at least 2 paragraphs, no more than 5 paragraphs",
        "Generate 3 avatars, company, city, country",
        "fullname 2개, email address, under 30",
        "avatar size 50x50 format png",
        "state: California, country: United States",
        "datetime from 2024-01-01 to 2024-12-31 format yyyy-mm-dd",
        "time from 9am to 6pm 24 hour",
        "url protocol host path query",
        "credit card number Visa",
        "credit card type Mastercard",
        "latitude, longitude, product price, swift bic, iban",
        # nullablePercent 테스트 케이스들
        "카드번호 blank 10%",
        "이름 빈 값 15%",
        "전화번호 빈값 20%",
        "이메일 null 25%",
        "주소 nullable 30%",
        "credit card number blank 40%",
        "phone number null 50%",
        "password missing 60%",
        "avatar blank: 70%",
        "state nullable: 80%",
        "10개 중에 3개 빈값 이름",
        "3 out of 10 null phone number",
        "email address blank 0%",
        "비밀번호 8자 이상 blank 25%"
    ]
    
    parser = FieldConstraintParser()
    for text in test_cases:
        print(f"입력: {text}")
        print(parser.parse(text))
        print("-" * 40)
