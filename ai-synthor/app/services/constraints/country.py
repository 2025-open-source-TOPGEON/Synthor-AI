import re
from .base import ConstraintExtractor
from ..constants_types import SUPPORTED_COUNTRIES
from ..mappings import KOR_TO_ENG_VALUE

class CountryExtractor(ConstraintExtractor):
    type_name = "country"

    def extract(self, text: str) -> dict:
        m = re.search(r'([가-힣A-Za-z \-\(\)]+)만|only ([A-Za-z \-\(\)]+)', text)
        if not m:
            return {}
        raw = (m.group(1) or m.group(2)).strip()
        val = KOR_TO_ENG_VALUE.get(raw, raw)
        if val not in SUPPORTED_COUNTRIES:
            raise ValueError(f"지원하지 않는 country 값입니다: {raw}")
        return {"options": val}
