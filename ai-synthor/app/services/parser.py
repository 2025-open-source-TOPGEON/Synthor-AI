# app/services/parser.py
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
            CreditCardTypeExtractor(), ParagraphsExtractor(), NumberBetweenExtractor(),
            KoreanFullNameExtractor(), KoreanLastNameExtractor(), EmailAddressConstraint()
        ]:
            reg.register(ext)
        return reg

    def parse_field_constraint(self, text: str) -> Dict:
        field = self.detector.detect_first(text)
        if not field:
            return {"type": None, "constraints": {}, "nullablePercent": None}

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
