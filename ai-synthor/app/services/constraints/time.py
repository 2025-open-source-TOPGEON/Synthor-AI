import re
from .base import ConstraintExtractor

class TimeExtractor(ConstraintExtractor):
    type_name = "time"

    def extract(self, text: str) -> dict:
        c = {}
        m_from = re.search(r'(오전|오후)?\s*(\d{1,2})시부터|from (\d{1,2})(am|pm)?', text, re.I)
        m_to   = re.search(r'부터\s*(오전|오후)?\s*(\d{1,2})시까지|to (\d{1,2})(am|pm)?', text, re.I)
        m_fmt  = re.search(r'(12시간제|24시간제|12 ?hour|24 ?hour)', text, re.I)

        if m_from:
            if m_from.group(1):
                c["from"] = f"{m_from.group(1)}{m_from.group(2)}"
            elif m_from.group(3):
                c["from"] = f"{m_from.group(3)}{m_from.group(4) or ''}"

        if m_to:
            if m_to.group(1):
                c["to"] = f"{m_to.group(1)}{m_to.group(2)}"
            elif m_to.group(3):
                c["to"] = f"{m_to.group(3)}{m_to.group(4) or ''}"

        if m_fmt:
            c["format"] = m_fmt.group(1)
        return c
