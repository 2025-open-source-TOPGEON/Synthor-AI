from .base import ConstraintExtractor
from ..constants_types import SUPPORTED_CARD_TYPES
from ..mappings import KOR_TO_ENG_VALUE

class CreditCardNumberExtractor(ConstraintExtractor):
    type_name = "credit_card_number"

    def extract(self, text: str) -> dict:
        low = text.lower()
        for t in SUPPORTED_CARD_TYPES:
            kor_eq = [k for k, v in KOR_TO_ENG_VALUE.items() if v == t]
            if t.lower() in low or any(k in text for k in kor_eq):
                return {"options": t}
        raise ValueError("지원하지 않는 카드사입니다.")
