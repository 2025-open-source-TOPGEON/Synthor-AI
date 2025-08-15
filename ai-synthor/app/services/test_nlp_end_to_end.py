from .constraint_parser import Parser

test_cases = [
    # Date range patterns
    "2023-01-05 ~ 2023-12-32 사이",
    "2023.1.5 ~ 2023.12.31 범위",
    "2023/1/5 ~ 2023/12/31 between",
    "from 2023-01-05 to 2023-12-31",
    "since 2023.1.5 until 2023.12.31",
    "start date: 2023-01-05",
    "end date: 2023-12-31",
    "시작일: 2023-01-05",
    "종료일: 2023-12-31",
    "2023-01-05부터 2023-12-31까지",
    "between 2023-01-05 and 2023-12-31",
    "기간: 2023-01-05 ~ 2023-12-31",
    "range: 2023-01-05 to 2023-12-31",
    
    # Format specifications - m/d/yyyy
    "m/d/yyyy 형식으로",
    "m/d/yyyy 포맷 사용",
    "m/d/yyyy 방식으로 부탁",
    "format: m/d/yyyy",
    "date format: m/d/yyyy",
    "use m/d/yyyy",
    "please use m/d/yyyy",
    "set to m/d/yyyy",
    "prefer m/d/yyyy",
    "default m/d/yyyy",
    "mdy",
    
    # Format specifications - mm/dd/yyyy
    "mm/dd/yyyy 형식으로",
    "mm/dd/yyyy 포맷 사용",
    "format: mm/dd/yyyy",
    "use mm/dd/yyyy",
    "set mm/dd/yyyy",
    
    # Format specifications - yyyy-mm-dd
    "yyyy-mm-dd 형식으로",
    "yyyy-mm-dd 포맷 사용",
    "format: yyyy-mm-dd",
    "use yyyy-mm-dd",
    "ISO format",
    "ISO 8601",
    "ymd",
    "년-월-일 형식",
    "YYYY년-MM월-DD일",
    
    # Format specifications - yyyy-mm
    "yyyy-mm 형식으로",
    "yyyy-mm 포맷 사용",
    "format: yyyy-mm",
    "use yyyy-mm",
    
    # Format specifications - d/m/yyyy
    "d/m/yyyy 형식으로",
    "d/m/yyyy 포맷 사용",
    "format: d/m/yyyy",
    "use d/m/yyyy",
    "dmy",
    "일/월/년 형식",
    
    # Format specifications - dd/mm/yyyy
    "dd/mm/yyyy 형식으로",
    "dd/mm/yyyy 포맷 사용",
    "format: dd/mm/yyyy",
    "use dd/mm/yyyy",
    "day/month/year",
    "DMY",
    
    # Mixed patterns with actual dates
    "2023-01-05 형식으로",
    "2023.1.5 포맷 사용",
    "2023/01/05 방식으로",
    "1-5-2023 형식",
    "01/05/2023 포맷",
    "23.01.05 방식",
    
    # Context-based format detection
    "같은 형식으로 2023-01-05",
    "처럼 2023.1.5",
    "와 같은 2023/01/05",
    "format to 2023-01-05",
    "date format is 2023-01-05",
    
    # Edge cases
    "2023-01-05",  # Single date without format specification
    "2023-01",     # Year-month only
    "2023.1",      # Year-month with dot
    "2023/1",      # Year-month with slash
    
    # Korean mixed patterns
    "2023년 1월 5일 형식",
    "2023년-1월-5일 방식",
    "2023년/1월/5일 포맷",
    
    # Complex combinations
    "from 2023-01-05 to 2023-12-31 in yyyy-mm-dd format",
    "2023-01-05부터 2023-12-31까지 m/d/yyyy 형식으로",
    "between 2023.1.5 and 2023.12.31 using ISO format",
    "기간: 2023-01-05 ~ 2023-12-31, format: yyyy-mm-dd",
    
    # Ambiguous date patterns for format detection
    "12/25/2023 형식으로",  # Should detect as m/d/yyyy
    "25/12/2023 형식으로",  # Should detect as d/m/yyyy
    "2023/12/31 형식으로",  # Should detect as yyyy-mm-dd
    
    # Date validation and correction tests - Range patterns with invalid dates
    "2023-01-05 ~ 2023-12-32 사이",  # 12월 32일 → 12월 31일로 보정
    "from 2023-04-31 to 2023-06-32",  # 4월 31일 → 4월 30일, 6월 32일 → 6월 30일로 보정
    "between 2023-01-00 and 2023-13-15",  # 1월 0일 → 1월 1일, 13월 → 12월로 보정
    "2023.2.30 ~ 2023.4.31 범위",  # 2월 30일 → 2월 28일, 4월 31일 → 4월 30일로 보정
    "2023/2/30부터 2023/4/31까지",  # 2월 30일 → 2월 28일, 4월 31일 → 4월 30일로 보정
    
    # Date validation and correction tests - Single date patterns with invalid dates
    "2024-02-30",  # 윤년 2월 30일 → 2월 29일로 보정
    "2023-02-30",  # 평년 2월 30일 → 2월 28일로 보정
    "2023.2.30",  # 평년 2월 30일 → 2월 28일로 보정 (점 구분자)
    "2023/2/30",  # 평년 2월 30일 → 2월 28일로 보정 (슬래시 구분자)
    "2023-04-31",  # 4월 31일 → 4월 30일로 보정
    "2023-06-32",  # 6월 32일 → 6월 30일로 보정
    "2023-01-00",  # 1월 0일 → 1월 1일로 보정
    "2023-13-15",  # 13월 → 12월로 보정
    
    # Date validation and correction tests - Leap year cases
    "2024-02-29",  # 윤년 2월 29일 (유효한 날짜)
    "2023-02-29",  # 평년 2월 29일 → 2월 28일로 보정
    "2024.2.29",  # 윤년 2월 29일 (유효한 날짜, 점 구분자)
    "2023.2.29",  # 평년 2월 29일 → 2월 28일로 보정 (점 구분자)
    
    # Date validation and correction tests - Different separators
    "2023.4.31",  # 4월 31일 → 4월 30일로 보정 (점 구분자)
    "2023/4/31",  # 4월 31일 → 4월 30일로 보정 (슬래시 구분자)
    "2023.6.32",  # 6월 32일 → 6월 30일로 보정 (점 구분자)
    "2023/6/32",  # 6월 32일 → 6월 30일로 보정 (슬래시 구분자)
    
    # Date validation and correction tests - Two-digit year
    "23.2.30",  # 2자리 연도 2월 30일 → 2월 28일로 보정
    "24.2.30",  # 2자리 연도 윤년 2월 30일 → 2월 29일로 보정
    "23/2/30",  # 2자리 연도 2월 30일 → 2월 28일로 보정 (슬래시 구분자)
    "24/2/30",  # 2자리 연도 윤년 2월 30일 → 2월 29일로 보정 (슬래시 구분자)
    
    # Date validation and correction tests - Edge cases
    "2023-00-15",  # 0월 → 1월로 보정
    "2023-12-00",  # 0일 → 1일로 보정
    "2023-13-00",  # 13월 0일 → 12월 1일로 보정
    "2023.0.15",  # 0월 → 1월로 보정 (점 구분자)
    "2023.12.0",  # 0일 → 1일로 보정 (점 구분자)
    
    # ── 범위 표현 (한국어)
    "기간: 2023-01-05 ~ 2023-12-31, 형식은 yyyy-mm-dd",
    "조회기간 2023.1.5 ~ 2023.12.31 (포맷: d/m/yyyy)",
    "유효기간 2023/01/05 ~ 2023/12/31, 포맷은 mm/dd/yyyy",
    "2023-01-05부터 2023-12-31까지, 형식 yyyy-mm-dd 적용",
    "2023.01 ~ 2023.12 (yyyy-mm 형식)",
    "2023/1 ~ 2023/12 범위, format yyyy-mm",
    "시작 2023-01-05 종료 2023-12-31, 포맷 m/d/yyyy",
    "기간(포함): 2023-01-05 ~ 2023-12-31, 형식 dd/mm/yyyy",
    "from 2023-01-05 to 2023-12-31 (형식: yyyy-mm-dd)",
    
    # ── 단일 경계 (한국어)
    "시작일은 2023-01-05, 포맷 yyyy-mm-dd",
    "종료일은 2023-12-31, 형식 dd/mm/yyyy",
    "기준일 이후: 2023-01-05 (yyyy-mm-dd)",
    
    # ── 포맷 지정만 (한국어)
    "포맷은 m/d/yyyy 로 고정",
    "날짜 형식: yyyy-mm",
    "포맷 dd/mm/yyyy 사용",
    "형식은 yyyy-mm-dd 로 설정",
    
    # ── 공백/구두점/대시 변형 (한국어)
    "기간 : 2023-01-05~2023-12-31 , 형식: yyyy-mm-dd",
    "2023-01-05 – 2023-12-31 (en dash), 형식 yyyy-mm-dd",
    "2023-01-05 — 2023-12-31 (em dash), 포맷 mm/dd/yyyy",
    
    # ── 한글 '년/월/일' 표기
    "2023년 1월 5일 ~ 2023년 12월 31일, 형식 yyyy-mm-dd",
    "보고서 기간(yyyy-mm): 2023년 1월 ~ 2023년 12월",
    
    # ── Null 허용 (한국어)
    "nullable 50%, 기간 2023-01-05 ~ 2023-12-31, 형식 yyyy-mm-dd",
    "빈값 25% 허용, 포맷은 d/m/yyyy",
    
    # ── 범위 표현 (영어)
    "Between 2023-01-05 and 2023-12-31, format yyyy-mm-dd",
    "from 2023.1.5 through 2023.12.31, format d/m/yyyy",
    "Range: 2023/01/05 to 2023/12/31, use mm/dd/yyyy",
    "2023-01 ~ 2023-12 (format: yyyy-mm)",
    "Start 2023-01-05, End 2023-12-31 (format m/d/yyyy)",
    ">= 2023-01-05 and <= 2023-12-31, format dd/mm/yyyy",
    
    # ── 단일 경계 (영어)
    "start date: 2023-01-05 (format yyyy-mm-dd)",
    "end date: 2023-12-31, format dd/mm/yyyy",
    "on or after 2023-01-05 and on or before 2023-12-31, format yyyy-mm-dd",
    
    # ── 포맷 지정만 (영어)
    "Format should be m/d/yyyy",
    "Apply mm/dd/yyyy format",
    "Use ISO 8601 (yyyy-mm-dd)",
    "DATE FORMAT = dd/mm/yyyy",
    "Format: YYYY-MM",  # 대문자 토큰
    
    # ── 공백/구두점/대시 변형 (영어)
    "from   2023-01-05   to   2023-12-31,   format yyyy-mm-dd",
    "2023-01-05–2023-12-31 (en dash), format mm/dd/yyyy",
    "2023-01-05 — 2023-12-31, format d/m/yyyy",
    
    # ── 샘플로 포맷 유추 (영어)
    "e.g., 1-5-2023 format (m/d/yyyy)",
    "example: 01/05/2023 (mm/dd/yyyy)",
    "sample: 25/12/2023 (d/m/yyyy)",
    "sample: 2023-07-09 (yyyy-mm-dd)",
    
    # ── Null 허용 (영어)
    "nullable 40%, format yyyy-mm-dd",
    "Allow up to 30% nulls, format m/d/yyyy",
    
    # ── 범위 + 포맷 혼합 (한국어+영어)
    "기간 2023-01-05~2023-12-31, use yyyy-mm-dd",
    "조회기간 2023.1.5 ~ 2023.12.31, format d/m/yyyy",
    "2023/01/05 ~ 2023/12/31, 포맷 mm/dd/yyyy please",
    "from 2023-01-05 to 2023-12-31, 포맷은 dd/mm/yyyy",
    "2023-01 ~ 2023-12, format yyyy-mm only",
    
    # ── 단일 경계 (한국어+영어)
    "시작일 2023-01-05, format yyyy-mm-dd",
    "종료일 2023-12-31, use m/d/yyyy",
    "start=2023-01-05; end=2023-12-31 (형식: yyyy-mm-dd)",
    
    # ── 포맷 지정만 (한국어+영어)
    "format m/d/yyyy please",
    "기본 포맷 dd/mm/yyyy",
    "포맷만 설정: mm/dd/yyyy",
    "DATE fmt -> yyyy-mm",
    "set format = d/m/yyyy",
    
    # ── 공백/구두점/대시 변형 (한국어+영어)
    "기간 : 2023-01-05 ~ 2023-12-31 , format yyyy-mm-dd",
    "2023-01-05–2023-12-31, 포맷 mm/dd/yyyy",
    "2023-01-05 — 2023-12-31, use d/m/yyyy",
    
    # ── 샘플로 포맷 유추 (한국어+영어)
    "예: 1-5-2023 같은 형식 (m/d/yyyy)",
    "샘플 01/05/2023 → mm/dd/yyyy",
    "예시는 25/12/2023 (d/m/yyyy)",
    "sample 2023-07-09 → yyyy-mm-dd",
    
    # ── Null 허용 (한국어+영어)
    "nullable 50%, 기간 2023-01-05~2023-12-31, format yyyy-mm-dd",
    "빈 값 20% 허용, use m/d/yyyy",
]

parser = Parser()

for i, text in enumerate(test_cases, 1):
    print(f"## 입력: {text}")
    try:
        result = parser.parse_field_constraint(text)
        print(f"{result}")
    except Exception as e:
        print(f"Error: {e}")
    print()