import re
from datetime import datetime
from .base import ConstraintExtractor

class DatetimeExtractor(ConstraintExtractor):
    type_name = "datetime"

    def extract(self, text: str) -> dict:
        c = {}
        t = text.strip()

        # 숫자 날짜 표기 전반 캡처
        date_pattern = (
            r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}'      # 2023-01-05 / 2023.1.5 / 2023/1/5
            r'|\d{1,2}[-/.]\d{1,2}[-/.]\d{4}'      # 1-5-2023 / 01/05/2023
            r'|\d{2}\.\d{2}\.\d{2})'               # 23.01.05 (보조)
        )

        # "날짜 ~ 날짜" 범위 패턴 먼저 확인
        range_pattern = re.search(
            r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\s*[~-]\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\s*(?:사이|범위|between)',
            t, re.I
        )
        
        from_value = None
        to_value = None
        
        if range_pattern:
            from_value = range_pattern.group(1)
            to_value = range_pattern.group(2)
        else:
            # 기본 from/to 인식
            m_from = re.search(
                r'from\s*' + date_pattern + r'|'
                r'since\s*' + date_pattern + r'|'
                r'(?:start\s*date|start|시작(?:일| 날짜)?)\s*[:=]?\s*' + date_pattern + r'|'
                + date_pattern + r'\s*부터',
                t, re.I
            )
            m_to = re.search(
                r'to\s*' + date_pattern + r'|'
                r'until\s*' + date_pattern + r'|'
                r'(?:end\s*date|end|종료(?:일| 날짜)?)\s*[:=]?\s*' + date_pattern + r'|'
                r'(?:부터|이후|뒤)?\s*' + date_pattern + r'\s*까지',
                t, re.I
            )
            
            if m_from:
                from_value = next(filter(None, m_from.groups()))
            if m_to:
                to_value = next(filter(None, m_to.groups()))

        c = {}
        if from_value:
            c["from"] = from_value
        if to_value:
            c["to"] = to_value

        # 자연스러운 범위 표현: between/range/기간, ~ 구분
        if "from" not in c or "to" not in c:
            m_between = re.search(
                r'(?:between|기간|range)\s*[:=]?\s*' + date_pattern + r'\s*(?:and|~|to|-)\s*' + date_pattern,
                t, re.I
            )
            if m_between:
                gs = [g for g in m_between.groups() if g]
                if len(gs) >= 2:
                    c["from"], c["to"] = gs[0], gs[1]

        # 허용 포맷 6종
        fmt_map = {
            "m/d/yyyy": [
                r'\bm\s*/\s*d\s*/\s*yyyy\b', r'\bm/d/yyyy\b',
                # 한국어/혼용
                r'(?:형식|포맷|표기|방식|날짜\s*형식|기본|기본값|표준)\s*(?:으로|로|을|를|은|는)?\s*m\s*/\s*d\s*/\s*yyyy',
                r'm\s*/\s*d\s*/\s*yyyy\s*(?:형식|포맷|표기|방식|로|으로|사용|부탁|맞춰(?:줘|요)?|설정|세팅|지정)',
                # 영어
                r'(?:format|date\s*format)\s*(?:to|is|should\s*be|=|:)?\s*m\s*/\s*d\s*/\s*yyyy',
                r'(?:use|please\s*use|set\s*to|set|prefer|default)\s*m\s*/\s*d\s*/\s*yyyy',
                r'\bmdy\b',
            ],
            "mm/dd/yyyy": [
                r'\bmm\s*/\s*dd\s*/\s*yyyy\b', r'\bmm/dd/yyyy\b',
                r'(?:형식|포맷|표기|방식|날짜\s*형식|기본|기본값|표준)\s*(?:으로|로|을|를|은|는)?\s*mm\s*/\s*dd\s*/\s*yyyy',
                r'mm\s*/\s*dd\s*/\s*yyyy\s*(?:형식|포맷|표기|방식|로|으로|사용|부탁|맞춰(?:줘|요)?|설정|세팅|지정)',
                r'(?:format|date\s*format)\s*(?:to|is|should\s*be|=|:)?\s*mm\s*/\s*dd\s*/\s*yyyy',
                r'(?:use|please\s*use|set\s*to|set|prefer|default)\s*mm\s*/\s*dd\s*/\s*yyyy',
            ],
            "yyyy-mm-dd": [
                r'\byyyy\s*-\s*mm\s*-\s*dd\b', r'\byyyy-mm-dd\b',
                # 한국어/혼용
                r'(?:형식|포맷|표기|방식|날짜\s*형식|기본|기본값|표준)\s*(?:으로|로|을|를|은|는)?\s*yyyy\s*-\s*mm\s*-\s*dd',
                r'yyyy\s*-\s*mm\s*-\s*dd\s*(?:형식|포맷|표기|방식|로|으로|사용|부탁|맞춰(?:줘|요)?|설정|세팅|지정)',
                # 영어
                r'(?:format|date\s*format)\s*(?:to|is|should\s*be|=|:)?\s*yyyy\s*-\s*mm\s*-\s*dd',
                r'(?:use|please\s*use|set\s*to|set|prefer|default)\s*yyyy\s*-\s*mm\s*-\s*dd',
                r'\byear\s*-\s*month\s*-\s*day\b(?:\s*(?:format|형식|포맷|표기|방식))?',
                # 한국어 서술(년월일 → yyyy-mm-dd로만 취급)
                r'(?:년\s*[-./]?\s*월\s*[-./]?\s*일)\s*(?:형식|포맷|표기|방식|으로|로|처럼|같은\s*형식(?:으로)?)',
                r'yyyy\s*년\s*[-./]?\s*월\s*[-./]?\s*일',
                r'YYYY\s*년\s*[-./]?\s*MM\s*월\s*[-./]?\s*DD\s*일',
                r'\biso(?:\s*8601)?\b|\biso\s*format\b|\bymd\b',
            ],
            "yyyy-mm": [
                r'\byyyy\s*-\s*mm\b', r'\byyyy-mm\b',
                r'(?:형식|포맷|표기|방식|날짜\s*형식|기본|기본값|표준)\s*(?:으로|로|을|를|은|는)?\s*yyyy\s*-\s*mm',
                r'yyyy\s*-\s*mm\s*(?:형식|포맷|표기|방식|로|으로|사용|부탁|맞춰(?:줘|요)?|설정|세팅|지정)',
                r'(?:format|date\s*format)\s*(?:to|is|should\s*be|=|:)?\s*yyyy\s*-\s*mm',
                r'(?:use|please\s*use|set\s*to|set|prefer|default)\s*yyyy\s*-\s*mm',
            ],
            "d/m/yyyy": [
                r'\bd\s*/\s*m\s*/\s*yyyy\b', r'\bd/m/yyyy\b',
                r'(?:형식|포맷|표기|방식|날짜\s*형식|기본|기본값|표준)\s*(?:으로|로|을|를|은|는)?\s*d\s*/\s*m\s*/\s*yyyy',
                r'd\s*/\s*m\s*/\s*yyyy\s*(?:형식|포맷|표기|방식|로|으로|사용|부탁|맞춰(?:줘|요)?|설정|세팅|지정)',
                r'(?:format|date\s*format)\s*(?:to|is|should\s*be|=|:)?\s*d\s*/\s*m\s*/\s*yyyy',
                r'(?:use|please\s*use|set\s*to|set|prefer|default)\s*d\s*/\s*m\s*/\s*yyyy',
                r'\bdmy\b|(?:일\/월\/년)\s*(?:형식|포맷|표기|방식)',
            ],
            "dd/mm/yyyy": [
                r'\bdd\s*/\s*mm\s*/\s*yyyy\b', r'\bdd/mm/yyyy\b',
                r'(?:형식|포맷|표기|방식|날짜\s*형식|기본|기본값|표준)\s*(?:으로|로|을|를|은|는)?\s*dd\s*/\s*mm\s*/\s*yyyy',
                r'dd\s*/\s*mm\s*/\s*yyyy\s*(?:형식|포맷|표기|방식|로|으로|사용|부탁|맞춰(?:줘|요)?|설정|세팅|지정)',
                r'(?:format|date\s*format)\s*(?:to|is|should\s*be|=|:)?\s*dd\s*/\s*mm\s*/\s*yyyy',
                r'(?:use|please\s*use|set\s*to|set|prefer|default)\s*dd\s*/\s*mm\s*/\s*yyyy',
                r'(?:day\s*\/\s*month\s*\/\s*year)|\bDMY\b',
            ],
        }

        earliest = None
        for fmt, patterns in fmt_map.items():
            for pat in patterns:
                for m in re.finditer(pat, t, flags=re.IGNORECASE):
                    pos = m.start()
                    if earliest is None or pos < earliest[0]:
                        earliest = (pos, fmt)

        if earliest is None:
            context = re.search(r'(형식|포맷|표기|방식|format|date\s*format|같은\s*형식|처럼|와\s*같이|와\s*같은)', t, re.I)
            if context:
                # yyyy sep mm sep dd
                m_ymd = re.search(r'\b(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})\b', t)
                # mm/dd/yyyy or dd/mm/yyyy or m/d/yyyy or d/m/yyyy
                m_mdy = re.search(r'\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})\b', t)
                # yyyy-mm
                m_y_m = re.search(r'\b(\d{4})[\/\-\.](\d{1,2})\b', t)

                if m_ymd:
                    earliest = (m_ymd.start(), "yyyy-mm-dd")
                elif m_mdy:
                    a = int(m_mdy.group(1)); b = int(m_mdy.group(2))
                    a_raw = m_mdy.group(1); b_raw = m_mdy.group(2)
                    if a > 12 and b <= 12:
                        earliest = (m_mdy.start(), "d/m/yyyy")
                    elif a <= 12 and b > 12:
                        earliest = (m_mdy.start(), "m/d/yyyy")
                    else:
                        earliest = (m_mdy.start(), "mm/dd/yyyy" if len(a_raw) == 2 and len(b_raw) == 2 else "m/d/yyyy")
                elif m_y_m:
                    earliest = (m_y_m.start(), "yyyy-mm")

        result = {}
        if "from" in c:
            result["from"] = c["from"]
        if "to" in c:
            result["to"] = c["to"]

        # format: 발견되면 그 값, 없으면 기본 m/d/yyyy
        result["format"] = earliest[1] if earliest else "m/d/yyyy"

        # from/to가 전혀 없으면 현재 연도 기본 범위 설정
        if "from" not in result and "to" not in result:
            current_year = datetime.now().year
            result = {
                "from": f"{current_year}-01-01",
                "to":   f"{current_year}-12-31",
                "format": result["format"],
            }

        return result
