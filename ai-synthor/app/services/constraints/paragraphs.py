import re
from .base import ConstraintExtractor

class ParagraphsExtractor(ConstraintExtractor):
    type_name = "paragraphs"

    def extract(self, text: str) -> dict:
        c = {}
        # "at least 2" 패턴
        m_min = re.search(r'최소\s*(\d+)문단|at least (\d+)', text, re.I)
        # "no more than 4" 패턴  
        m_max = re.search(r'최대\s*(\d+)문단|no more than (\d+)', text, re.I)
        
        if m_min:
            c["at least"] = int(next(filter(None, m_min.groups())))
        if m_max:
            c["but no more than"] = int(next(filter(None, m_max.groups())))
        return c
