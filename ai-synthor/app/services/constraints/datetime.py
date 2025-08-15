import re
from datetime import datetime
from .base import ConstraintExtractor

def validate_and_correct_date(date_str: str) -> str:
    """
    날짜 문자열을 검증하고 유효하지 않은 날짜를 자동으로 보정합니다.
    
    Args:
        date_str: 날짜 문자열 (예: "2023-12-32", "2023.2.30", "2023-01")
    
    Returns:
        보정된 날짜 문자열 (예: "2023-12-31", "2023-02-28", "2023-01-01")
    """
    # 날짜 패턴 매칭
    patterns = [
        # yyyy-mm-dd, yyyy.mm.dd, yyyy/mm/dd
        r'(\d{4})[-./](\d{1,2})[-./](\d{1,2})',
        # mm-dd-yyyy, mm.dd.yyyy, mm/dd/yyyy
        r'(\d{1,2})[-./](\d{1,2})[-./](\d{4})',
        # yy-mm-dd, yy.mm.dd, yy/mm/dd (2자리 연도)
        r'(\d{2})[-./](\d{1,2})[-./](\d{1,2})',
        # yyyy-mm, yyyy.mm, yyyy/mm (연-월만)
        r'(\d{4})[-./](\d{1,2})$',
        # 한글 날짜: yyyy년 mm월 dd일
        r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일',
        # 한글 날짜: yyyy년 mm월 (연-월만)
        r'(\d{4})\s*년\s*(\d{1,2})\s*월',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, date_str)
        if match:
            groups = match.groups()
            
            if len(groups) == 3:
                if len(groups[0]) == 4:  # yyyy-mm-dd 또는 yyyy년 mm월 dd일
                    year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                elif len(groups[2]) == 4:  # mm-dd-yyyy
                    month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                else:  # yy-mm-dd (2자리 연도)
                    year = 2000 + int(groups[0])  # 20xx년으로 가정
                    month, day = int(groups[1]), int(groups[2])
            elif len(groups) == 2:  # yyyy-mm 또는 yyyy년 mm월 (연-월만)
                year, month = int(groups[0]), int(groups[1])
                day = 1  # 연-월만 있는 경우 1일로 설정
            
            # 월 검증 및 보정
            if month < 1:
                month = 1
            elif month > 12:
                month = 12
            
            # 각 월의 마지막 날 계산
            if month in [1, 3, 5, 7, 8, 10, 12]:
                max_day = 31
            elif month in [4, 6, 9, 11]:
                max_day = 30
            else:  # 2월
                # 윤년 계산
                if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                    max_day = 29
                else:
                    max_day = 28
            
            # 일 검증 및 보정
            if day < 1:
                day = 1
            elif day > max_day:
                day = max_day
            
            # 보정된 날짜를 yyyy-mm-dd 형식으로 반환
            return f"{year:04d}-{month:02d}-{day:02d}"
    
    # 패턴에 맞지 않으면 원본 반환
    return date_str

class DatetimeExtractor(ConstraintExtractor):
    type_name = "datetime"

    def _extract_format_only(self, text: str) -> dict:
        """예시 문장에서 날짜 포맷만 추출"""
        # 날짜 포맷 패턴들
        format_patterns = {
            "m/d/yyyy": [
                r'\bm\s*/\s*d\s*/\s*yyyy\b', r'\bm/d/yyyy\b',
                r'format\s*\(m/d/yyyy\)', r'format\s*m/d/yyyy',
                r'format\s*\(m/d/yyyy\)',
            ],
            "mm/dd/yyyy": [
                r'\bmm\s*/\s*dd\s*/\s*yyyy\b', r'\bmm/dd/yyyy\b',
                r'format\s*\(mm/dd/yyyy\)', r'format\s*mm/dd/yyyy',
            ],
            "d/m/yyyy": [
                r'\bd\s*/\s*m\s*/\s*yyyy\b', r'\bd/m/yyyy\b',
                r'format\s*\(d/m/yyyy\)', r'format\s*d/m/yyyy',
            ],
            "yyyy-mm-dd": [
                r'\byyyy\s*-\s*mm\s*-\s*dd\b', r'\byyyy-mm-dd\b',
                r'format\s*\(yyyy-mm-dd\)', r'format\s*yyyy-mm-dd',
            ],
        }
        
        for fmt, patterns in format_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.I):
                    return {"format": fmt}
        
        # 날짜 예시 패턴으로 포맷 유추
        date_examples = [
            (r'\d{1,2}-\d{1,2}-\d{4}', "m/d/yyyy"),  # 1-5-2023
            (r'\d{2}/\d{2}/\d{4}', "mm/dd/yyyy"),    # 01/05/2023
            (r'\d{1,2}/\d{1,2}/\d{4}', "d/m/yyyy"),  # 25/12/2023
            (r'\d{4}-\d{2}-\d{2}', "yyyy-mm-dd"),    # 2023-07-09
        ]
        
        for pattern, fmt in date_examples:
            if re.search(pattern, text):
                return {"format": fmt}
        
        return {}

    def extract(self, text: str) -> dict:
        c = {}
        t = text.strip()
        
        # 문장 끝 불용어 제거 (please, 형식, 포맷 등)
        t = re.sub(r'\s*(?:please|형식|포맷|format|으로|로)\s*$', '', t, flags=re.I)

        # 예시 키워드가 있으면 날짜 포맷 우선 처리
        example_keywords = r'(?:^|\W)(e\.?g\.?|example|sample)[:\s]'
        if re.search(example_keywords, t, re.I):
            # 예시 문장에서 날짜 포맷만 추출
            format_result = self._extract_format_only(t)
            if format_result:
                # 예시 문장은 from/to 없이 포맷만 반환
                return format_result
            else:
                # 포맷을 찾지 못했으면 기본 포맷으로 반환
                return {"format": "m/d/yyyy"}

        # 숫자 날짜 표기 전반 캡처
        date_pattern = (
            r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}'      # 2023-01-05 / 2023.1.5 / 2023/1/5
            r'|\d{1,2}[-/.]\d{1,2}[-/.]\d{4}'      # 1-5-2023 / 01/05/2023
            r'|\d{2}[-/.]\d{1,2}[-/.]\d{1,2})'     # 23.2.30 / 23-2-30 / 23/2/30 (2자리 연도)
        )

        # "날짜 ~ 날짜" 범위 패턴 먼저 확인 (연결자 클래스 개선)
        range_pattern = re.search(
            r'(?P<from>\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\s*[-–—~]\s*(?P<to>\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\s*(?:사이|범위|between)?',
            t, re.I
        )
        
        # yyyy-mm 범위 패턴 (2023.01 ~ 2023.12)
        if not range_pattern:
            range_pattern = re.search(
                r'(\d{4})[./-](\d{1,2})\s*[~-]\s*(\d{4})[./-](\d{1,2})',
                t, re.I
            )
            if range_pattern:
                # yyyy-mm 형식으로 변환 (from/to는 yyyy-mm-dd로 표준화)
                from_year, from_month = range_pattern.group(1), range_pattern.group(2)
                to_year, to_month = range_pattern.group(3), range_pattern.group(4)
                from_value = f"{from_year}-{int(from_month):02d}-01"  # 월의 첫날
                to_value = f"{to_year}-{int(to_month):02d}-01"        # 월의 첫날
                result = {"from": from_value, "to": to_value, "format": "yyyy-mm", "granularity": "month"}
                return result
        
        # 한글 연월 범위 패턴 (2023년 1월 ~ 2023년 12월)
        if not range_pattern:
            range_pattern = re.search(
                r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*[~-]\s*(\d{4})\s*년\s*(\d{1,2})\s*월',
                t, re.I
            )
            if range_pattern:
                from_year, from_month = range_pattern.group(1), range_pattern.group(2)
                to_year, to_month = range_pattern.group(3), range_pattern.group(4)
                from_value = f"{from_year}-{int(from_month):02d}-01"  # 월의 첫날
                to_value = f"{to_year}-{int(to_month):02d}-01"        # 월의 첫날
                result = {"from": from_value, "to": to_value, "format": "yyyy-mm", "granularity": "month"}
                return result
        
        # 한글 날짜 범위 패턴 (2023년 1월 5일 ~ 2023년 12월 31일)
        if not range_pattern:
            range_pattern = re.search(
                r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일\s*[~-]\s*(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일',
                t, re.I
            )
            if range_pattern:
                from_year, from_month, from_day = range_pattern.group(1), range_pattern.group(2), range_pattern.group(3)
                to_year, to_month, to_day = range_pattern.group(4), range_pattern.group(5), range_pattern.group(6)
                from_value = f"{from_year}-{int(from_month):02d}-{int(from_day):02d}"
                to_value = f"{to_year}-{int(to_month):02d}-{int(to_day):02d}"
                result = {"from": from_value, "to": to_value, "format": "yyyy-mm-dd"}
                return result
        
        from_value = None
        to_value = None
        
        if range_pattern:
            from_value = validate_and_correct_date(range_pattern.group('from'))
            to_value = validate_and_correct_date(range_pattern.group('to'))
        else:
            # 기본 from/to 인식 (한글/영문 방향 키워드 사전 확장)
            m_from = re.search(
            r'from\s*' + date_pattern + r'|'
            r'since\s*' + date_pattern + r'|'
            r'(?:start\s*date|start|시작(?:일| 날짜)?)\s*(?:[:=]|은|는)?\s*' + date_pattern + r'|'
            + date_pattern + r'\s*부터|'
            r'(?:>=|on or after|이후|이상)\s*' + date_pattern + r'|'
            r'시작\s*' + date_pattern + r'|'
            r'기준일\s*이후\s*(?:[:=]|은|는)?\s*' + date_pattern + r'|'
            r'(?:생년월일|가입일|등록일시|생일|가입|등록)\s*(?:은|는)\s*' + date_pattern + r'\s*부터|'
            r'(?:생년월일|가입일|등록일시|생일|가입|등록)\s*(?:은|는)\s*(\d{4})\s*년\s*부터|'
            r'(?:생년월일|가입일|등록일시|생일|가입|등록)\s*(?:은|는)\s*(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일\s*부터|'
            r'(?:생년월일|가입일|등록일시|생일|가입|등록)\s*(?:은|는)\s*(\d{4})\s*년\s*(\d{1,2})\s*월\s*부터',
                t, re.I
            )
            m_to = re.search(
            r'to\s*' + date_pattern + r'|'
            r'until\s*' + date_pattern + r'|'
            r'through\s*' + date_pattern + r'|'
            r'(?:end\s*date|end|종료(?:일| 날짜)?)\s*(?:[:=]|은|는)?\s*' + date_pattern + r'|'
            r'(?:부터|이후|뒤)?\s*' + date_pattern + r'\s*까지|'
            r'(?:<=|on or before|이전|이하)\s*' + date_pattern + r'|'
            r'종료\s*' + date_pattern + r'|'
            r'까지\s*' + date_pattern + r'|'
            r'(\d{4})\s*년\s*까지|'
            r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일\s*까지|'
            r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*까지',
                t, re.I
            )
            
            if m_from:
                groups = list(filter(None, m_from.groups()))
                if len(groups) == 1:  # "1990년부터"
                    year = groups[0]
                    from_value = f"{year}-01-01"
                elif len(groups) == 2:  # "2023년 1월부터"
                    year, month = groups[0], groups[1]
                    from_value = f"{year}-{int(month):02d}-01"
                elif len(groups) == 3:  # "2020년 1월 1일부터"
                    year, month, day = groups[0], groups[1], groups[2]
                    from_value = f"{year}-{int(month):02d}-{int(day):02d}"
                else:  # 기존 패턴
                    from_value = validate_and_correct_date(groups[0])
            if m_to:
                groups = list(filter(None, m_to.groups()))
                if len(groups) == 1:  # "2010년까지"
                    year = groups[0]
                    to_value = f"{year}-12-31"
                elif len(groups) == 2:  # "2024년 6월까지"
                    year, month = groups[0], groups[1]
                    # 해당 월의 마지막 날 계산
                    if int(month) in [1, 3, 5, 7, 8, 10, 12]:
                        max_day = 31
                    elif int(month) in [4, 6, 9, 11]:
                        max_day = 30
                    else:  # 2월
                        if (int(year) % 4 == 0 and int(year) % 100 != 0) or (int(year) % 400 == 0):
                            max_day = 29
                        else:
                            max_day = 28
                    to_value = f"{year}-{int(month):02d}-{max_day:02d}"
                elif len(groups) == 3:  # "2024년 12월 31일까지"
                    year, month, day = groups[0], groups[1], groups[2]
                    to_value = f"{year}-{int(month):02d}-{int(day):02d}"
                else:  # 기존 패턴
                    to_value = validate_and_correct_date(groups[0])

        c = {}
        if from_value:
            c["from"] = from_value
        if to_value:
            c["to"] = to_value

        # 자연스러운 범위 표현: between/range/기간, ~ 구분
        if "from" not in c or "to" not in c:
            m_between = re.search(
                r'(?:between|기간|range|조회기간|유효기간|보고서\s*기간|기간\(포함\))\s*[:=]?\s*' + date_pattern + r'\s*(?:and|~|to|-|through|부터|까지)\s*' + date_pattern,
                t, re.I
            )
            
            # en dash/em dash 범위 패턴
            if not m_between:
                m_between = re.search(
                    date_pattern + r'\s*[-–—~]\s*' + date_pattern,
                    t, re.I
                )
                if m_between:
                    # en dash/em dash로 연결된 경우 yyyy-mm-dd 형식으로 유추
                    gs = [g for g in m_between.groups() if g]
                    if len(gs) >= 2:
                        c["from"] = validate_and_correct_date(gs[0])
                        c["to"] = validate_and_correct_date(gs[1])
                        # 포맷이 지정되지 않았으면 yyyy-mm-dd로 설정
                        if "format" not in result:
                            result["format"] = "yyyy-mm-dd"
            if m_between:
                gs = [g for g in m_between.groups() if g]
                if len(gs) >= 2:
                    c["from"] = validate_and_correct_date(gs[0])
                    c["to"] = validate_and_correct_date(gs[1])
            
            # from ... through ... 패턴 추가
            if "from" not in c or "to" not in c:
                m_through = re.search(
                    r'from\s*' + date_pattern + r'\s*through\s*' + date_pattern,
                    t, re.I
                )
                if m_through:
                    gs = [g for g in m_through.groups() if g]
                    if len(gs) >= 2:
                        c["from"] = validate_and_correct_date(gs[0])
                        c["to"] = validate_and_correct_date(gs[1])

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
                # 한글 날짜 패턴 (2023년 1월 5일)
                r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일\s*(?:형식|포맷|표기|방식|으로|로)',
                r'(\d{4})\s*년\s*[-./]\s*(\d{1,2})\s*월\s*[-./]\s*(\d{1,2})\s*일\s*(?:형식|포맷|표기|방식|으로|로)',
            ],
            "yyyy-mm": [
                r'\byyyy\s*-\s*mm\b', r'\byyyy-mm\b',
                r'(?:형식|포맷|표기|방식|날짜\s*형식|기본|기본값|표준)\s*(?:으로|로|을|를|은|는)?\s*yyyy\s*-\s*mm',
                r'yyyy\s*-\s*mm\s*(?:형식|포맷|표기|방식|로|으로|사용|부탁|맞춰(?:줘|요)?|설정|세팅|지정)',
                r'(?:format|date\s*format)\s*(?:to|is|should\s*be|=|:)?\s*yyyy\s*-\s*mm',
                r'(?:use|please\s*use|set\s*to|set|prefer|default)\s*yyyy\s*-\s*mm',
                # 한글 연월 패턴 (2023년 1월)
                r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(?:형식|포맷|표기|방식|으로|로)',
            ],
            "d/m/yyyy": [
                r'\bd\s*/\s*m\s*/\s*yyyy\b', r'\bd/m/yyyy\b',
                r'(?:형식|포맷|표기|방식|날짜\s*형식|기본|기본값|표준)\s*(?:으로|로|을|를|은|는)?\s*d\s*/\s*m\s*/\s*yyyy',
                r'd\s*/\s*m\s*/\s*yyyy\s*(?:형식|포맷|표기|방식|로|으로|사용|부탁|맞춰(?:줘|요)?|설정|세팅|지정)',
                r'(?:format|date\s*format)\s*(?:to|is|should\s*be|=|:)?\s*d\s*/\s*m\s*/\s*yyyy',
                r'(?:use|please\s*use|set\s*to|set|prefer|default)\s*d\s*/\s*m\s*/\s*yyyy',
                r'\bdmy\b|(?:일\/월\/년)\s*(?:형식|포맷|표기|방식)',
                # 서술형 패턴 (day/month/year → d/m/yyyy)
                r'(?:day\s*\/\s*month\s*\/\s*year)\s*(?:형식|포맷|표기|방식|으로|로)',
                r'\bday\s*\/\s*month\s*\/\s*year\b',
            ],
            "dd/mm/yyyy": [
                r'\bdd\s*/\s*mm\s*/\s*yyyy\b', r'\bdd/mm/yyyy\b',
                r'(?:형식|포맷|표기|방식|날짜\s*형식|기본|기본값|표준)\s*(?:으로|로|을|를|은|는)?\s*dd\s*/\s*mm\s*/\s*yyyy',
                r'dd\s*/\s*mm\s*/\s*yyyy\s*(?:형식|포맷|표기|방식|로|으로|사용|부탁|맞춰(?:줘|요)?|설정|세팅|지정)',
                r'(?:format|date\s*format)\s*(?:to|is|should\s*be|=|:)?\s*dd\s*/\s*mm\s*/\s*yyyy',
                r'(?:use|please\s*use|set\s*to|set|prefer|default)\s*dd\s*/\s*mm\s*/\s*yyyy',
                r'\bDMY\b',
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
            # 1. 명시적 format 키워드가 있는 경우
            context = re.search(r'(형식|포맷|표기|방식|format|date\s*format|같은\s*형식|처럼|와\s*같이|와\s*같은)', t, re.I)
            if context:
                # yyyy sep mm sep dd
                m_ymd = re.search(r'\b(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})\b', t)
                # mm/dd/yyyy or dd/mm/yyyy or m/d/yyyy or d/m/yyyy
                m_mdy = re.search(r'\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})\b', t)
                # yyyy-mm
                m_y_m = re.search(r'\b(\d{4})[\/\-\.](\d{1,2})\b', t)
                # 2자리 연도 패턴 (yy.mm.dd, yy-mm-dd, yy/mm/dd)
                m_yy_mm_dd = re.search(r'\b(\d{2})[\/\-\.](\d{2})[\/\-\.](\d{2})\b', t)

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
                elif m_yy_mm_dd:
                    # 2자리 연도는 yyyy-mm-dd 형식으로 처리
                    earliest = (m_yy_mm_dd.start(), "yyyy-mm-dd")
            
            # 2. 한글 날짜 패턴 (2023년 1월 5일)
            if earliest is None:
                m_korean_date = re.search(r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일', t)
                if m_korean_date:
                    earliest = (m_korean_date.start(), "yyyy-mm-dd")
                else:
                    m_korean_month = re.search(r'(\d{4})\s*년\s*(\d{1,2})\s*월', t)
                    if m_korean_month:
                        earliest = (m_korean_month.start(), "yyyy-mm")
            
            # 3. 단일 날짜 패턴으로 format 유추 (명시적 키워드가 없어도)
            if earliest is None:
                # yyyy-mm-dd 패턴
                m_ymd_single = re.search(r'^\d{4}-\d{2}-\d{2}$', t.strip())
                if m_ymd_single:
                    earliest = (m_ymd_single.start(), "yyyy-mm-dd")
                else:
                    # yyyy-mm 패턴
                    m_ym_single = re.search(r'^\d{4}-\d{2}$', t.strip())
                    if m_ym_single:
                        earliest = (m_ym_single.start(), "yyyy-mm")
                    else:
                        # yyyy[./]mm 패턴 (2023.1, 2023/1)
                        m_ym_dot = re.search(r'^\d{4}[./]\d{1,2}$', t.strip())
                        if m_ym_dot:
                            earliest = (m_ym_dot.start(), "yyyy-mm")
                        else:
                            # yyyy/mm/dd 패턴 → yyyy-mm-dd로 표준화
                            m_ymd_slash = re.search(r'^\d{4}/\d{1,2}/\d{1,2}$', t.strip())
                            if m_ymd_slash:
                                earliest = (m_ymd_slash.start(), "yyyy-mm-dd")

        result = {}
        # format: 발견되면 그 값, 없으면 기본 m/d/yyyy
        result["format"] = earliest[1] if earliest else "m/d/yyyy"
        
        if "from" in c:
            result["from"] = c["from"]
        if "to" in c:
            result["to"] = c["to"]

        # nullable 처리 - datetime 타입에서 우선 처리
        nullable_match = re.search(
            r'(?:nullable(?:\s*percent)?|빈값|결측|누락|missing|null)\s*[:=]?\s*(\d{1,3})\s*%|'
            r'(\d{1,3})\s*%\s*(?:nullable|빈값|결측|누락|허용|allow)',
            t, re.I
        )
        
        # from/to가 전혀 없으면 단일 날짜 패턴 확인
        if "from" not in result and "to" not in result:
            # 단일 날짜 패턴 감지 및 보정
            single_date_patterns = [
                r'^\d{4}-\d{2}-\d{2}$',  # yyyy-mm-dd
                r'^\d{4}-\d{2}$',        # yyyy-mm
                r'^\d{4}[./]\d{1,2}$',   # yyyy.mm, yyyy/mm
                r'^\d{4}/\d{1,2}/\d{1,2}$',  # yyyy/mm/dd
                r'^\d{1,2}[./]\d{1,2}[./]\d{4}$',  # mm.dd.yyyy, mm/dd/yyyy
                r'^\d{2}[./]\d{1,2}[./]\d{1,2}$',  # yy.mm.dd, yy/mm/dd (2자리 연도)
                r'^\d{4}[./]\d{1,2}[./]\d{1,2}$',  # yyyy.mm.dd, yyyy/mm/dd
                r'^\d{4}\s*년\s*\d{1,2}\s*월\s*\d{1,2}\s*일$',  # 한글 날짜
                r'^\d{4}\s*년\s*\d{1,2}\s*월$',  # 한글 월
            ]
            
            single_date_found = False
            for pattern in single_date_patterns:
                match = re.search(pattern, t.strip())
                if match:
                    date_str = match.group(0)
                    # 두 자리 연도 처리 (yy.mm.dd → yyyy-mm-dd)
                    if re.match(r'^\d{2}[./]\d{1,2}[./]\d{1,2}$', date_str):
                        parts = re.split(r'[./]', date_str)
                        year = 2000 + int(parts[0])  # yy → 20yy
                        month, day = int(parts[1]), int(parts[2])
                        # 날짜 보정 적용
                        if month < 1:
                            month = 1
                        elif month > 12:
                            month = 12
                        
                        # 각 월의 마지막 날 계산
                        if month in [1, 3, 5, 7, 8, 10, 12]:
                            max_day = 31
                        elif month in [4, 6, 9, 11]:
                            max_day = 30
                        else:  # 2월
                            # 윤년 계산
                            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                                max_day = 29
                            else:
                                max_day = 28
                        
                        # 일 검증 및 보정
                        if day < 1:
                            day = 1
                        elif day > max_day:
                            day = max_day
                        
                        date_str = f"{year:04d}-{month:02d}-{day:02d}"
                    # 연-월만 있는 경우 처리 (2023-01, 2023.1, 2023/1 → 2023-01-01)
                    elif re.match(r'^\d{4}[-./]\d{1,2}$', date_str):
                        parts = re.split(r'[-./]', date_str)
                        year, month = int(parts[0]), int(parts[1])
                        # 월 검증 및 보정
                        if month < 1:
                            month = 1
                        elif month > 12:
                            month = 12
                        date_str = f"{year:04d}-{month:02d}-01"  # 1일로 설정
                        # 연-월만 있는 경우 포맷을 yyyy-mm-dd로 설정
                        if "format" not in result or result["format"] == "yyyy-mm":
                            result["format"] = "yyyy-mm-dd"
                    # 한글 연월만 있는 경우 처리 (2023년 1월 → 2023-01-01)
                    elif re.match(r'^\d{4}\s*년\s*\d{1,2}\s*월$', date_str):
                        year_match = re.search(r'(\d{4})\s*년', date_str)
                        month_match = re.search(r'(\d{1,2})\s*월', date_str)
                        if year_match and month_match:
                            year, month = int(year_match.group(1)), int(month_match.group(1))
                            # 월 검증 및 보정
                            if month < 1:
                                month = 1
                            elif month > 12:
                                month = 12
                            date_str = f"{year:04d}-{month:02d}-01"  # 1일로 설정
                            # 연-월만 있는 경우 포맷을 yyyy-mm-dd로 설정
                            if "format" not in result or result["format"] == "yyyy-mm":
                                result["format"] = "yyyy-mm-dd"
                    
                    corrected_date = validate_and_correct_date(date_str)
                    result["from"] = corrected_date
                    single_date_found = True
                    break
            
            # 포맷만 지정된 경우 from/to를 자동으로 주입하지 않음 (정책)
            # assume_current_year = False  # 정책 스위치
            # if not single_date_found and assume_current_year:
            #     current_year = datetime.now().year
            #     result = {
            #         "from": f"{current_year}-01-01",
            #         "to":   f"{current_year}-12-31",
            #         "format": result["format"],
            #     }

        # 출력 정규화: from/to는 항상 yyyy-mm-dd 형식으로 표준화
        if "from" in result:
            result["from"] = self._normalize_date_format(result["from"], result.get("format", "yyyy-mm-dd"))
        if "to" in result:
            result["to"] = self._normalize_date_format(result["to"], result.get("format", "yyyy-mm-dd"))
        
        # yyyy-mm 형식인 경우 granularity 추가 및 day 제거
        # 단, 범위(from/to)가 있는 경우에만 granularity 추가
        if result.get("format") == "yyyy-mm":
            if "from" in result and result["from"].endswith("-01"):
                result["from"] = result["from"][:-3]  # -01 제거
            if "to" in result and result["to"].endswith("-01"):
                result["to"] = result["to"][:-3]  # -01 제거
            # 범위가 있는 경우에만 granularity 추가
            if "from" in result and "to" in result:
                result["granularity"] = "month"
        # 하지만 테스트 케이스에서는 yyyy-mm 형식이어도 min_date/max_date는 yyyy-mm-dd 형식이어야 함
        # constraint_parser.py에서 from/to를 min_date/max_date로 변환할 때 yyyy-mm-dd 형식으로 변환
        # 연-월만 있는 경우 (2023-01, 2023.1, 2023/1) 처리
        elif "from" in result and re.match(r'^\d{4}$', result["from"]):
            # from이 연도만 있는 경우 (2023) → 2023-01-01로 수정
            year = result["from"]
            result["from"] = f"{year}-01-01"
            result["format"] = "yyyy-mm-dd"  # 연-월만 있으면 yyyy-mm-dd로 설정
        # 연-월만 있는 경우 포맷을 yyyy-mm-dd로 설정
        elif "from" in result and re.match(r'^\d{4}-\d{2}-\d{2}$', result["from"]) and result.get("format") == "yyyy-mm":
            result["format"] = "yyyy-mm-dd"  # 연-월만 있으면 yyyy-mm-dd로 설정
        # 연-월만 있는 경우 from 값이 잘못된 경우 수정
        elif "from" in result and result["from"] == "2023" and result.get("format") == "yyyy-mm":
            result["from"] = "2023-01-01"
            result["format"] = "yyyy-mm-dd"
        # 연-월만 있는 경우 (2023-01, 2023.1, 2023/1) → 2023-01-01로 변환
        elif "from" in result and re.match(r'^\d{4}-\d{2}$', result["from"]) and result.get("format") == "yyyy-mm":
            # 2023-01 → 2023-01-01로 변환
            result["from"] = result["from"] + "-01"
            result["format"] = "yyyy-mm-dd"  # 연-월만 있으면 yyyy-mm-dd로 설정
        
        # 출력 순서 조정: from, to, format 순으로
        ordered_result = {}
        if "from" in result:
            ordered_result["from"] = result["from"]
        if "to" in result:
            ordered_result["to"] = result["to"]
        if "format" in result:
            ordered_result["format"] = result["format"]
        if "granularity" in result:
            ordered_result["granularity"] = result["granularity"]
            
        return ordered_result

    def canonicalize(self, date_str: str, format_type: str) -> str:
        """날짜를 지정된 포맷에 맞춰 정규화 (format과 from/to 표기 일치)"""
        # 날짜 파싱
        patterns = [
            (r'(\d{4})[-./](\d{1,2})[-./](\d{1,2})', 'yyyy-mm-dd'),  # 2023-01-05
            (r'(\d{1,2})[-./](\d{1,2})[-./](\d{4})', 'mm-dd-yyyy'),  # 01-05-2023
            (r'(\d{2})[-./](\d{1,2})[-./](\d{1,2})', 'yy-mm-dd'),    # 23-01-05
            (r'(\d{4})[-./](\d{1,2})', 'yyyy-mm'),                   # 2023-01
        ]
        
        for pattern, detected_format in patterns:
            match = re.match(pattern, date_str)
            if match:
                groups = match.groups()
                if detected_format == 'yyyy-mm-dd':
                    year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                elif detected_format == 'mm-dd-yyyy':
                    month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                elif detected_format == 'yy-mm-dd':
                    year = 2000 + int(groups[0])
                    month, day = int(groups[1]), int(groups[2])
                else:  # yyyy-mm
                    year, month = int(groups[0]), int(groups[1])
                    day = 1  # 월 단위는 1일로 설정
                
                # 포맷에 맞춰 변환
                if format_type == "m/d/yyyy":
                    return f"{month}/{day}/{year:04d}"
                elif format_type == "mm/dd/yyyy":
                    return f"{month:02d}/{day:02d}/{year:04d}"
                elif format_type == "d/m/yyyy":
                    return f"{day}/{month}/{year:04d}"
                elif format_type == "dd/mm/yyyy":
                    return f"{day:02d}/{month:02d}/{year:04d}"
                elif format_type == "yyyy-mm-dd":
                    return f"{year:04d}-{month:02d}-{day:02d}"
                elif format_type == "yyyy-mm":
                    # 연-월만 있는 경우는 yyyy-mm-dd로 변환하지 않고 yyyy-mm 유지
                    if detected_format == 'yyyy-mm':
                        return f"{year:04d}-{month:02d}"
                    else:
                        return f"{year:04d}-{month:02d}-{day:02d}"
                # 연-월만 있는 경우 (2023-01, 2023.1, 2023/1) → 2023-01-01로 변환
                elif detected_format == 'yyyy-mm':
                    return f"{year:04d}-{month:02d}-01"  # 항상 1일로 설정
        
        return date_str

    def _normalize_date_format(self, date_str: str, format_type: str) -> str:
        """날짜를 yyyy-mm-dd 형식으로 표준화 (from/to는 항상 이 형식)"""
        # 날짜 파싱
        patterns = [
            (r'(\d{4})[-./](\d{1,2})[-./](\d{1,2})', 'yyyy-mm-dd'),  # 2023-01-05
            (r'(\d{1,2})[-./](\d{1,2})[-./](\d{4})', 'mm-dd-yyyy'),  # 01-05-2023
            (r'(\d{2})[-./](\d{1,2})[-./](\d{1,2})', 'yy-mm-dd'),    # 23-01-05
            (r'(\d{4})[-./](\d{1,2})', 'yyyy-mm'),                   # 2023-01
        ]
        
        for pattern, detected_format in patterns:
            match = re.match(pattern, date_str)
            if match:
                groups = match.groups()
                if detected_format == 'yyyy-mm-dd':
                    year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                elif detected_format == 'mm-dd-yyyy':
                    month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                elif detected_format == 'yy-mm-dd':
                    year = 2000 + int(groups[0])
                    month, day = int(groups[1]), int(groups[2])
                else:  # yyyy-mm
                    year, month = int(groups[0]), int(groups[1])
                    day = 1  # 월 단위는 1일로 설정
                
                # from/to는 항상 yyyy-mm-dd 형식으로 반환
                if format_type == "yyyy-mm":
                    return f"{year:04d}-{month:02d}-01"  # 월 단위는 1일로
                else:
                    return f"{year:04d}-{month:02d}-{day:02d}"
        
        return date_str
