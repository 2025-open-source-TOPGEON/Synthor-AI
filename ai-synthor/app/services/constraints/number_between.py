import re
from .base import ConstraintExtractor

class NumberBetweenExtractor(ConstraintExtractor):
    type_name = "number_between_1_100"

    def extract(self, text: str) -> dict:
        c = {}
        m_min = re.search(r'(\d+)\s*이상|at least (\d+)', text, re.I)
        m_max = re.search(r'(\d+)\s*이하|under (\d+)', text, re.I)
        m_dec = re.search(r'소수점\s*(\d+)자리|decimals?\s*(\d+)', text, re.I)
        if m_min: c["min"] = int(next(filter(None, m_min.groups())))
        if m_max: c["max"] = int(next(filter(None, m_max.groups())))
        if m_dec: c["decimals"] = int(next(filter(None, m_dec.groups())))
        return c
