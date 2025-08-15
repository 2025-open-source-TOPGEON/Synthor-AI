# app/services/parser.py
import re
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
from .constraints.email_address import EmailAddressConstraint

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
            KoreanFullNameExtractor(), KoreanLastNameExtractor(), EmailAddressConstraint(),
            NumberBetweenExtractor()  # 숫자범위는 마지막에 배치
        ]:
            reg.register(ext)
        return reg

    def parse_field_constraint(self, text: str) -> Dict:
        # 나이/연령 관련 키워드가 있으면 datetime으로 인식하지 않음
        age_keywords = ['나이', '연령', '연령대', '나이대', '세', '살', 'age']
        has_age_keyword = any(keyword in text for keyword in age_keywords)
        
        # 이메일 도메인 패턴이 있으면 datetime으로 인식하지 않음
        email_domain_patterns = [
            r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # @domain.com
            r'@[a-zA-Z0-9.-]+형',  # @domain형
            r'\b(?:naver\.com|gmail\.com|yahoo\.com|hotmail\.com|outlook\.com|daum\.net|nate\.com|hanmail\.net|icloud\.com|protonmail\.com)\b',  # 일반 도메인
            r'\b(?:naver|gmail|yahoo|hotmail|outlook|daum|nate|hanmail|icloud|protonmail)\s+account\b',  # 도메인 account
            r'\b(?:naver|gmail|yahoo|hotmail|outlook|daum|nate|hanmail|icloud|protonmail)\s+mail\b',  # 도메인 mail
            r'\b(?:naver|gmail|yahoo|hotmail|outlook|daum|nate|hanmail|icloud|protonmail)\s+email\b',  # 도메인 email
        ]
        has_email_domain = any(re.search(pattern, text, re.I) for pattern in email_domain_patterns)
        
        # 한국어 이름 패턴이 있으면 datetime으로 인식하지 않음
        korean_name_patterns = [
            r'성이\s*[가-힣]{1,2}',  # 성이 김, 성이 이, 성이 박 등
            r'성씨가\s*[가-힣]{1,2}',  # 성씨가 김, 성씨가 이 등
            r'[가-힣]{1,2}씨',  # 김씨, 이씨, 박씨 등
            r'[가-힣]{1,2}\s*성',  # 김 성, 이 성 등
        ]
        has_korean_name = any(re.search(pattern, text) for pattern in korean_name_patterns)
        
        # 날짜/포맷 지시어가 있으면 datetime 타입으로 고정 (우선순위: DateFormat > Nullable% > NumberBetween)
        datetime_indicators = [
            r'\b(?:format|date\s*format|m/d/yyyy|mm/dd/yyyy|d/m/yyyy|yyyy-mm-dd|yyyy-mm)\b',
            r'\b(?:e\.?g\.?|example|sample|예시는|샘플|예|샘)[:\s]',
            r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',
            r'\d{1,2}[-/.]\d{1,2}[-/.]\d{4}',
            r'\d{2}[-/.]\d{1,2}[-/.]\d{1,2}',
            r'\b(?:from|to|through|between|range|기간|조회기간|시작일|종료일|start|end)\b',
            r'\b(?:nullable|빈값|결측|누락|use|포맷|형식|fmt)\b',
            r'\b(?:d/m/yyyy|m/d/yyyy|mm/dd/yyyy|yyyy-mm-dd|yyyy-mm)\b',
            r'\b(?:only|같은|형식|포맷만|설정)\b',
        ]
        
        is_datetime_text = any(re.search(pattern, text, re.I) for pattern in datetime_indicators)
        
        # 나이 관련 키워드가 있으면 datetime으로 인식하지 않음
        if has_age_keyword:
            is_datetime_text = False
            
        # 이메일 도메인 패턴이 있으면 datetime으로 인식하지 않음
        if has_email_domain:
            is_datetime_text = False
            
        # 한국어 이름 패턴이 있으면 datetime으로 인식하지 않음
        if has_korean_name:
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
        if re.search(r'\d+[-/.]\d+[-/.]\d+', text):
            is_datetime_text = True
        
        field = self.detector.detect_first(text)
        if not field:
            if is_datetime_text:
                field = "datetime"
            else:
                return {"type": None, "constraints": {}, "nullablePercent": None}

        # 날짜 관련 텍스트면 datetime 타입으로 강제 (FieldDetector 결과 무시)
        if is_datetime_text:
            field = "datetime"
            extractor = self.registry.get("datetime") or self.default_extractor
        else:
            extractor = self.registry.get(field) or self.default_extractor

        # 1) 타입별 constraints - korean_* 타입들을 해당 타입으로 변환
        if field == "korean_phone":
            phone_extractor = self.registry.get("phone")
            if phone_extractor:
                phone_constraints = phone_extractor.extract(text) or {}
                if phone_constraints:
                    field = "phone"
                    extractor = phone_extractor

        elif field == "korean_state":
            state_extractor = self.registry.get("state")
            if state_extractor:
                state_constraints = state_extractor.extract(text) or {}
                if state_constraints:
                    field = "state"
                    extractor = state_extractor

        elif field == "korean_country":
            country_extractor = self.registry.get("country")
            if country_extractor:
                country_constraints = country_extractor.extract(text) or {}
                if country_constraints:
                    field = "country"
                    extractor = country_extractor

        try:
            constraints = extractor.extract(text) or {}
        except ValueError:
            return {"type": None, "constraints": {}, "nullablePercent": None}

        # 2) 전역 보조 제약 merge
        global_c = self.qualifiers.extract(text)
        constraints.update(global_c)

        # 3) nullablePercent
        nullable = self.nullables.extract(text)

        # 4) 최종 JSON
        if field in CONSTRAINT_TYPES:
            return {"type": field, "constraints": constraints, "nullablePercent": nullable}
        else:
            return {"type": field, "constraints": {}, "nullablePercent": nullable}
