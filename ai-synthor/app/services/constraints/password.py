import re
from .base import ConstraintExtractor

class PasswordExtractor(ConstraintExtractor):
    type_name = "password"

    def extract(self, text: str) -> dict:
        c = {}

        def pick(m):
            return int(next(filter(None, m.groups()))) if m else None

        #최소 길이 (숫자 명시형만, ≥N)
        m_min = re.search(
            r'(?:최소|적어도)\s*(\d+)\s*(?:자|글자|자리)|'            # 최소 10자
            r'(\d+)\s*(?:자|글자|자리)\s*(?:이상)|'                  # 10자 이상
            r'최소\s*길이[:\s]*(\d+)|길이\s*최소[:\s]*(\d+)|'        # 최소 길이 10 / 길이 최소 10
            r'min(?:imum)?(?:\s*length)?[:\s]*(\d+)|'               # minimum length: 10
            r'length\s*(?:at\s*least|>=)\s*(\d+)|'                  # length at least 10 / length >= 10
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*(?:chars?|characters?|letters?)|'
            r'min[:\s]*(\d+)\s*(?:chars?|characters?)',             # min 10 chars
            text, re.I
        )

        #대문자 개수 (숫자 명시형만, ≥N)
        m_up  = re.search(
            r'대문자\s*(\d+)\s*(?:개|자)|'                          # 대문자 2개
            r'(?:대문자|영문\s*대문자)\s*(\d+)\s*개\s*이상|'         # 대문자 2개 이상
            r'대문자\s*최소[:\s]*(\d+)|'                            # 대문자 최소 2
            r'upper(?:case)?[:\s]*:?[\s]*(\d+)|'                    # uppercase: 2
            r'uppercase\s*>=\s*(\d+)|'                              # uppercase >= 2
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*uppercase(?:\s*letters?)?|'
            r'capitals?[:\s]*:?[\s]*(\d+)|'                         # capital: 2
            r'at\s*least\s*(\d+)\s*capitals?',                      # at least 1 capital
            text, re.I
        )

        #소문자 개수 (숫자 명시형만, ≥N)
        m_low = re.search(
            r'소문자\s*(\d+)\s*(?:개|자)|'
            r'(?:소문자|영문\s*소문자)\s*(\d+)\s*개\s*이상|'
            r'소문자\s*최소[:\s]*(\d+)|'
            r'lower(?:case)?[:\s]*:?[\s]*(\d+)|'
            r'lowercase\s*>=\s*(\d+)|'
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*lowercase(?:\s*letters?)?',
            text, re.I
        )

        #숫자/디지트 개수 (숫자 명시형만, ≥N)
        m_num = re.search(
            r'(?:숫자|수자)\s*(\d+)\s*(?:개|자)|'
            r'(?:숫자|수자)\s*(\d+)\s*개\s*이상|'
            r'숫자\s*최소[:\s]*(\d+)|'
            r'numbers?[:\s]*:?[\s]*(\d+)|'
            r'digits?[:\s]*:?[\s]*(\d+)|'
            r'numerals?[:\s]*:?[\s]*(\d+)|'                         #numeral: 2
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*(?:digits?|numbers?|numerals?)',
            text, re.I
        )

        #특수문자/기호 개수 (숫자 명시형만, ≥N)
        m_sym = re.search(
            r'(?:특수문자|특문|기호|특수\s*기호)\s*(\d+)\s*(?:개|자)|'
            r'(?:특수문자|특문|기호|특수\s*기호)\s*(\d+)\s*개\s*이상|'
            r'(?:특수문자|특문|기호)\s*최소[:\s]*(\d+)|'
            r'special\s*(?:chars?|characters?)[:\s]*:?[\s]*(\d+)|'  #special characters: 2
            r'symbols?[:\s]*:?[\s]*(\d+)|'
            r'punctuation[:\s]*:?[\s]*(\d+)|'
            r'non[- ]?alphanumeric[:\s]*:?[\s]*(\d+)|'
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*(?:symbols?|punctuation|special\s*(?:chars?|characters?))',
            text, re.I
        )

        categories = {
            "minimum_length": m_min,
            "upper": m_up, 
            "lower": m_low,
            "numbers": m_num,
            "symbols": m_sym
        }
        
        for category, match in categories.items():
            if match:
                val = pick(match)
                if val is not None:
                    c[category] = val
        
        return c
