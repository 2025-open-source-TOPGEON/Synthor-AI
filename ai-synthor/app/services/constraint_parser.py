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
            r'\b(?:format|date\s*format|m/d/yyyy|mm/dd/yyyy|d/m/yyyy|yyyy-mm-dd|yyyy-mm)\b',
            r'\b(?:e\.?g\.?|example|sample|예시는|샘플|예|샘)[:\s]',
            r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',
            r'\d{1,2}[-/.]\d{1,2}[-/.]\d{4}',
            r'\d{2}[-/.]\d{1,2}[-/.]\d{1,2}',
            # 나이/연령 컨텍스트가 아닐 때만 from/to/between을 날짜로 인식
            r'(?<!나이|연령)\b(?:from|to|through|between|range|기간|조회기간|시작일|종료일|start|end)\b(?!\s*\d+)',
            r'\b(?:use|포맷|형식|fmt)\b',  # nullable 제거
            r'\b(?:d/m/yyyy|m/d/yyyy|mm/dd/yyyy|yyyy-mm-dd|yyyy-mm)\b',
            r'\b(?:please|only|같은|형식|포맷만|설정)\b',
        ]
        
        is_datetime_text = any(re.search(pattern, text, re.I) for pattern in datetime_indicators)
        
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
            password_constraint_keywords = ["대문자", "소문자", "숫자", "특수문자", "특수기호", "symbol", "uppercase", "lowercase", "numbers", "letters", "character", "characters", "비밀번호", "password"]
            if any(keyword in text for keyword in password_constraint_keywords):
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

        # 2) 전역 보조 제약 merge (password/phone 등 제한 타입일 때만 반영하려면 여기서 merge)
        global_c = self.qualifiers.extract(text)
        constraints.update(global_c)

        # 3) nullablePercent
        nullable = self.nullables.extract(text)

                    # 4) 최종 JSON 조립 (원 코드와 완전 동일 포맷)
        if field in CONSTRAINT_TYPES:
            # number_between_1_100과 korean_* 타입들은 원래 이름 그대로 사용
            if field == "number_between_1_100" or field.startswith("korean_"):
                type_name = field
            else:
                # email_address, password, datetime은 그대로 유지, 나머지는 대문자로 시작하도록 변환
                if field == "email_address" or field == "password" or field == "datetime":
                    type_name = field
                else:
                    type_name = field.replace("_", " ").title().replace(" ", "")
            return {"type": type_name, "constraints": constraints, "nullablePercent": nullable}
        else:
            type_name = field.replace("_", " ").title().replace(" ", "")
            return {"type": type_name, "constraints": {}, "nullablePercent": nullable}
