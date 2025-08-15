from typing import Dict
from .detectors import FieldDetector
from .nullables import NullablePercentExtractor
from .qualifiers import GlobalQualifiersExtractor
from .constants_types import CONSTRAINT_TYPES
from .constraints.registry import ConstraintRegistry
from .constraints.default import DefaultExtractor

# 개별 Extractor 등록
from .constraints.password import PasswordExtractor
from .constraints.phone import PhoneExtractor
from .constraints.avatar import AvatarExtractor
from .constraints.state import StateExtractor
from .constraints.country import CountryExtractor
from .constraints.datetime import DatetimeExtractor
from .constraints.time import TimeExtractor
from .constraints.url import UrlExtractor 
from .constraints.credit_card_number import CreditCardNumberExtractor
from .constraints.credit_card_type import CreditCardTypeExtractor
from .constraints.paragraphs import ParagraphsExtractor
from .constraints.number_between import NumberBetweenExtractor
from .constraints.korean_full_name import KoreanFullNameExtractor, KoreanLastNameExtractor
from .constraints.email import EmailExtractor

class Parser:
    def __init__(self):
        self.detector = FieldDetector()
        self.nullables = NullablePercentExtractor()
        self.qualifiers = GlobalQualifiersExtractor()
        self.registry = self._build_registry()
        self.default_extractor = DefaultExtractor()

    def _build_registry(self) -> ConstraintRegistry:
        reg = ConstraintRegistry()
        for ext in [
            PasswordExtractor(), PhoneExtractor(), AvatarExtractor(),
            StateExtractor(), CountryExtractor(), DatetimeExtractor(),
            TimeExtractor(), UrlExtractor(), CreditCardNumberExtractor(),
            CreditCardTypeExtractor(), ParagraphsExtractor(), 
            KoreanFullNameExtractor(), KoreanLastNameExtractor(), EmailExtractor(),
            NumberBetweenExtractor()  # 숫자범위는 마지막에 배치
        ]:
            reg.register(ext)
        return reg

    def parse_field_constraint(self, text: str) -> Dict:
        # 날짜/포맷 지시어가 있으면 datetime 타입으로 고정 (우선순위: DateFormat > Nullable% > NumberBetween)
        import re
        
        # 나이/연령 키워드가 있으면 number_between_1_100으로 우선 처리
        age_keywords = [r'\b(?:나이|연령|age)\b']
        is_age_text = any(re.search(pattern, text, re.I) for pattern in age_keywords)
        
        # integer 키워드가 나이/연령과 함께 있으면 숫자로 인식
        integer_age_pattern = r'\b(?:integer|정수)\s+(?:나이|연령|age)\b'
        is_integer_age = bool(re.search(integer_age_pattern, text, re.I))
        
        datetime_indicators = [
            r'\b(?:date\s*format|m/d/yyyy|mm/dd/yyyy|d/m/yyyy|yyyy-mm-dd|yyyy-mm)\b',
            r'\b(?:e\.?g\.?|example|sample|예시는|샘플|예|샘)[:\s]',
            r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',
            r'\d{1,2}[-/.]\d{1,2}[-/.]\d{4}',
            r'\d{2}[-/.]\d{1,2}[-/.]\d{1,2}',
            # 나이/연령 컨텍스트가 아닐 때만 from/between을 날짜로 인식 (to는 이메일에서도 사용되므로 제외)
            r'(?<!나이|연령)\b(?:from|through|between|range|기간|조회기간|시작일|종료일|start|end)\b(?!\s*\d+)',
            r'\b(?:fmt)\b',  # use 제거 (이메일에서도 사용됨)
            r'\b(?:d/m/yyyy|m/d/yyyy|mm/dd/yyyy|yyyy-mm-dd|yyyy-mm)\b',
            r'\b(?:같은|설정)\b',  # only 제거 (이메일에서도 사용됨)
        ]
        
        is_datetime_text = any(re.search(pattern, text, re.I) for pattern in datetime_indicators)
        
        # 이메일 도메인/패턴이 보이면 datetime 우선순위를 끈다
        email_first_patterns = [
            r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',    # @domain.com
            r'@[a-zA-Z0-9.-]+형',                 # @domain형
            r'@[a-zA-Z0-9.-]+(?:로|으로)\b',     # @domain로, @domain으로
            r'\b(?:naver\.com|gmail\.com|yahoo\.com|hotmail\.com|outlook\.com|daum\.net|nate\.com|hanmail\.net|icloud\.com|protonmail\.com)\b',
        ]
        if any(re.search(p, text, re.I) for p in email_first_patterns):
            is_datetime_text = False
        
        # 추가 날짜 감지: 날짜 패턴이 있으면 무조건 datetime
        date_patterns = [
            r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',  # 2023-07-09, 2023/07/09
            r'\d{1,2}[-/.]\d{1,2}[-/.]\d{4}',  # 25/12/2023, 12/25/2023
            r'\d{2}[-/.]\d{1,2}[-/.]\d{1,2}',  # 23/12/25
            r'\d{4}[-/.]\d{1,2}',  # 2023-01, 2023.1
        ]
        has_date_pattern = any(re.search(pattern, text) for pattern in date_patterns)
        
        # 날짜 패턴이 있으면 무조건 datetime으로 설정
        if has_date_pattern:
            is_datetime_text = True
        
        # 더 강력한 날짜 감지: 숫자-숫자-숫자 패턴이 있으면 무조건 datetime
        # 단, 나이/연령 키워드가 있으면 제외
        if not is_age_text and not is_integer_age and re.search(r'\d+[-/.]\d+[-/.]\d+', text):
            is_datetime_text = True
        
        field = self.detector.detect_first(text)
        if not field:
            if is_datetime_text:
                field = "datetime"
            else:
                return {"type": None, "constraints": {}, "nullablePercent": None}

        # 날짜 관련 텍스트면 datetime 타입으로 강제 (FieldDetector 결과 무시)
        # 단, 나이/연령 키워드가 있으면 number_between_1_100으로 유지
        if is_datetime_text and not is_age_text and not is_integer_age:
            field = "datetime"
            extractor = self.registry.get("datetime") or self.default_extractor
        else:
            extractor = self.registry.get(field) or self.default_extractor

        # 비밀번호 제약 조건 컨텍스트 후처리
        if field == "number_between_1_100":
            # 더 구체적인 비밀번호 키워드만 사용
            password_specific_keywords = ["비밀번호", "패스워드", "비번", "password", "대문자", "소문자", "특수문자", "특수기호", "symbol", "uppercase", "lowercase"]
            # "숫자는 1에서 100 사이" 같은 경우는 number_between_1_100으로 유지
            if re.search(r'숫자.*\d+.*\d+', text) and not any(keyword in text for keyword in ["비밀번호", "패스워드", "password"]):
                field = "number_between_1_100"
                extractor = self.registry.get("number_between_1_100") or self.default_extractor
            # 숫자 키워드는 비밀번호 컨텍스트에서만 사용
            elif any(keyword in text for keyword in password_specific_keywords) or ("숫자" in text and ("비밀번호" in text or "패스워드" in text or "password" in text)):
                field = "password"
                extractor = self.registry.get("password") or self.default_extractor

        extractor = self.registry.get(field) or self.default_extractor

        # 1) 타입별 constraints - korean_* 타입들을 해당 타입으로 변환
        if field == "korean_phone":
            phone_extractor = self.registry.get("phone")
            if phone_extractor:
                phone_constraints = phone_extractor.extract(text) or {}
                if phone_constraints:  # phone constraints가 있으면 korean_phone → phone으로 변경
                    field = "phone"
                    extractor = phone_extractor
        
        elif field == "korean_state":
            state_extractor = self.registry.get("state")
            if state_extractor:
                state_constraints = state_extractor.extract(text) or {}
                if state_constraints:  # state constraints가 있으면 korean_state → state로 변경
                    field = "state"
                    extractor = state_extractor
        
        elif field == "korean_country":
            country_extractor = self.registry.get("country")
            if country_extractor:
                country_constraints = country_extractor.extract(text) or {}
                if country_constraints:  # country constraints가 있으면 korean_country → country로 변경
                    field = "country"
                    extractor = country_extractor
        
        elif field == "korean_full_name":
            # korean_full_name은 그대로 유지
            korean_full_name_extractor = self.registry.get("korean_full_name")
            if korean_full_name_extractor:
                extractor = korean_full_name_extractor
        
        elif field == "email_address":
            email_extractor = self.registry.get("email_address")
            if email_extractor:
                email_constraints = email_extractor.extract(text) or {}
                if email_constraints:  # email constraints가 있으면 email_address → email_address로 유지
                    extractor = email_extractor
        

        
        try:
            constraints = extractor.extract(text) or {}
        except ValueError as e:
            return {"type": None, "constraints": {}, "nullablePercent": None}

        # datetime 필드명 매핑 (from/to 유지)
        # if field == "datetime" and constraints:
        #     if "from" in constraints:
        #         constraints["min_date"] = constraints.pop("from")
        #     if "to" in constraints:
        #         constraints["max_date"] = constraints.pop("to")

        # 2) 전역 보조 제약 merge (password/phone 등 제한 타입일 때만 반영하려면 여기서 merge)
        global_c = self.qualifiers.extract(text)
        constraints.update(global_c)

        # 3) nullablePercent
        nullable = self.nullables.extract(text)

                    # 4) 최종 JSON 조립 (원 코드와 완전 동일 포맷)
        if field in CONSTRAINT_TYPES:
            # 모든 타입을 소문자로 반환
            type_name = field
            return {"type": type_name, "constraints": constraints, "nullablePercent": nullable}
        else:
            type_name = field
            return {"type": type_name, "constraints": {}, "nullablePercent": nullable}
