import re
from .nullables import NullablePercentExtractor

# 지원하는 데이터 타입(필드명) 목록 (한국어 전용, 영문, 언어 중립)
SUPPORTED_TYPES = {
    # 한국어 전용
    "korean_full_name", "korean_first_name", "korean_last_name", "korean_phone",
    "korean_address", "korean_street_address", "korean_city", "korean_state", "korean_country", "korean_postal_code",
    "korean_company_name", "korean_job_title", "korean_department_corporate", "korean_department_retail",
    "korean_product_name", "korean_product_category", "korean_catch_phrase", "korean_product_description",
    "korean_language", "korean_color",
    # 영문
    "full_name", "first_name", "last_name", "phone", "address", "street_address", "city", "state", "country", "postal_code",
    "company_name", "job_title", "department_corporate", "department_retail", "product_name", "product_category",
    "catch_phrase", "product_description", "language", "color",
    # 언어 중립
    "username", "password", "email_address", "domain_name", "url", "mac_address", "ip_v4_address", "ip_v6_address",
    "user_agent", "avatar", "app_name", "app_version", "device_model", "device_brand", "device_os",
    "credit_card_number", "credit_card_type", "product_price", "currency", "iban", "swift_bic",
    "paragraphs", "datetime", "time", "latitude", "longitude", "number_between_1_100"
}

# 조건이 붙을 수 있는 타입 목록
CONSTRAINT_TYPES = {
    "password", "phone", "avatar", "state", "country", "datetime", "time", "url",
    "credit_card_number", "credit_card_type", "paragraphs", "number_between_1_100",
    "korean_full_name", "korean_last_name", "email_address"
}

# state, country, credit_card_number, credit_card_type 지원 값 정의 (예시)
SUPPORTED_STATES = {
    "California", "New York", "Seoul", "Île-de-France", "Tokyo", "Beijing", "Ontario",
    "Bavaria (Bayern)", "São Paulo", "Maharashtra", "Istanbul", "England", "Madrid",
    "New South Wales", "Moscow"
}

SUPPORTED_COUNTRIES = {
    "United States", "미국",
    "China", "중국",
    "Germany", "독일",
    "United Kingdom", "영국",
    "France", "프랑스",
    "Japan", "일본",
    "India", "인도",
    "Russia", "러시아",
    "South Korea", "대한민국",
    "Brazil", "브라질",
    "Canada", "캐나다",
    "Italy", "이탈리아",
    "Australia", "호주",
    "Spain", "스페인",
    "Turkey", "튀르키예"
}

SUPPORTED_CARD_TYPES = {
    "Visa", "Mastercard", "American Express", "Amex", "JCB", "China UnionPay", "Maestro", "Diners Club International"
}

# 한글 → 영문/한국어 타입 매핑 (예시, 필요시 계속 확장)
KOR_TO_ENG_FIELD = {
    # korean_full_name
    "전체 이름": "korean_full_name",
    "이름 전체": "korean_full_name",
    "성명": "korean_full_name",
    "풀네임": "korean_full_name",
    "전성 이름": "korean_full_name",
    "이름": "korean_full_name",
    "이름 전체": "korean_full_name",
    "이름 전부": "korean_full_name",
    "이름 풀": "korean_full_name",
    "이름(전체)": "korean_full_name",
    "이름(풀)": "korean_full_name",
    "이름 전체명": "korean_full_name",
    "이름 풀네임": "korean_full_name",
    # korean_last_name
    "성": "korean_last_name",
    "성씨": "korean_last_name",
    "이 성": "korean_last_name",
    "김 성": "korean_last_name",
    "박 성": "korean_last_name",
    "최 성": "korean_last_name",
    "성(이)": "korean_last_name",
    "성(김)": "korean_last_name",
    "성(박)": "korean_last_name",
    "성(최)": "korean_last_name",
    # korean_full_name에 성씨 패턴 추가
    "이씨": "korean_full_name",
    "김씨": "korean_full_name",
    "박씨": "korean_full_name",
    "최씨": "korean_full_name",
    # korean_first_name
    "이름(이)": "korean_first_name",
    "이름(김)": "korean_first_name",
    "이름(박)": "korean_first_name",
    "이름(최)": "korean_first_name",
    "이름만": "korean_first_name",
    "이름(한글)": "korean_first_name",
    "이름(영문)": "korean_first_name",
    # korean_address
    "주소": "korean_address",
    "전체 주소": "korean_address",
    "집 주소": "korean_address",
    "거주지": "korean_address",
    "거주 주소": "korean_address",
    "거주지 주소": "korean_address",
    "거주지 전체": "korean_address",
    # korean_street_address
    "도로명 주소": "korean_street_address",
    "도로 주소": "korean_street_address",
    "도로명": "korean_street_address",
    "도로 전체": "korean_street_address",
    "도로명 전체": "korean_street_address",
    "도로명주소": "korean_street_address",
    # korean_city
    "도시": "korean_city",
    "도시 이름": "korean_city",
    "사는 도시": "korean_city",
    "거주 도시": "korean_city",
    "시": "korean_city",
    "시 이름": "korean_city",
    "도시 이름(한글)": "korean_city",
    # korean_state
    "시도": "korean_state",
    "도": "korean_state",
    "시/도": "korean_state",
    "시 도": "korean_state",
    "도 이름": "korean_state",
    "시 이름": "korean_state",
    # korean_country
    "국가": "korean_country",
    "나라": "korean_country",
    "거주 국가": "korean_country",
    "사는 나라": "korean_country",
    # korean_postal_code
    "우편번호": "korean_postal_code",
    "우편 코드": "korean_postal_code",
    "우편 번호": "korean_postal_code",
    "우편코드": "korean_postal_code",
    # korean_phone
    "전화번호": "korean_phone",
    "휴대폰 번호": "korean_phone",
    "핸드폰 번호": "korean_phone",
    "연락처": "korean_phone",
    "휴대폰": "korean_phone",
    "핸드폰": "korean_phone",
    "전화": "korean_phone",
    # korean_company_name
    "회사명": "korean_company_name",
    "회사 이름": "korean_company_name",
    "근무처": "korean_company_name",
    "근무 회사": "korean_company_name",
    # korean_job_title
    "직책": "korean_job_title",
    "직위": "korean_job_title",
    "포지션": "korean_job_title",
    "직무": "korean_job_title",
    # korean_department_corporate
    "부서": "korean_department_corporate",
    "소속": "korean_department_corporate",
    "소속 부서": "korean_department_corporate",
    "소속팀": "korean_department_corporate",
    # korean_product_name
    "제품명": "korean_product_name",
    "상품명": "korean_product_name",
    "제품 이름": "korean_product_name",
    "상품 이름": "korean_product_name",
    # korean_product_category
    "제품 카테고리": "korean_product_category",
    "상품 카테고리": "korean_product_category",
    "제품 종류": "korean_product_category",
    "상품 종류": "korean_product_category",
    # korean_catch_phrase
    "캐치프레이즈": "korean_catch_phrase",
    "슬로건": "korean_catch_phrase",
    "표어": "korean_catch_phrase",
    # korean_product_description
    "제품 설명": "korean_product_description",
    "상품 설명": "korean_product_description",
    "제품 소개": "korean_product_description",
    "상품 소개": "korean_product_description",
    # korean_language
    "언어": "korean_language",
    "사용 언어": "korean_language",
    "쓰는 언어": "korean_language",
    # korean_color
    "색상": "korean_color",
    "컬러": "korean_color",
    "색": "korean_color",
    # username
    "사용자명": "username",
    "유저명": "username",
    "계정명": "username",
    "계정 이름": "username",
    "유저 이름": "username",
    # password
    "비밀번호": "password",
    "패스워드": "password",
    "비번": "password",
    # email_address
    "이메일": "email_address",
    "이메일 주소": "email_address",
    "메일": "email_address",
    "메일 주소": "email_address",
    # domain_name
    "도메인": "domain_name",
    "도메인 이름": "domain_name",
    # url
    "URL": "url",
    "주소(URL)": "url",
    "링크": "url",
    "웹주소": "url",
    # mac_address
    "MAC 주소": "mac_address",
    # ip_v4_address
    "IPv4 주소": "ip_v4_address",
    # ip_v6_address
    "IPv6 주소": "ip_v6_address",
    # user_agent
    "유저 에이전트": "user_agent",
    # avatar
    "아바타": "avatar",
    "프로필 사진": "avatar",
    "프로필 이미지": "avatar",
    "프로필 그림": "avatar",
    "프로필 아이콘": "avatar",
    "프로필 그림 파일": "avatar",
    "프로필 캐릭터": "avatar",
    "프로필 사진 파일": "avatar",
    "프로필 얼굴": "avatar",
    "캐릭터 이미지": "avatar",
    "캐릭터 그림": "avatar",
    "캐릭터 아이콘": "avatar",
    "사용자 아이콘": "avatar",
    "사용자 이미지": "avatar",
    "사용자 사진": "avatar",
    "계정 아이콘": "avatar",
    "계정 이미지": "avatar",
    "계정 사진": "avatar",
    "계정 프로필": "avatar",
    "아바타 이미지": "avatar",
    "아바타 사진": "avatar",
    "아바타 이미지 파일": "avatar",
    "프로필 avatar": "avatar",
    "캐릭터 avatar": "avatar",
    "유저 avatar": "avatar",
    "계정 avatar": "avatar",
    # app_name
    "앱 이름": "app_name",
    "어플 이름": "app_name",
    # app_version
    "버전": "app_version",
    "앱 버전": "app_version",
    # device_model
    "기기 모델": "device_model",
    # device_brand
    "기기 브랜드": "device_brand",
    # device_os
    "OS": "device_os",
    "운영체제": "device_os",
    # credit_card_number
    "카드번호": "credit_card_number",
    "신용카드 번호": "credit_card_number",
    # credit_card_type
    "카드 종류": "credit_card_type",
    "카드 타입": "credit_card_type",
    "VISA MASTER 종류": "credit_card_type",
    # currency
    "통화": "currency",
    "화폐 단위": "currency",
    # iban
    "IBAN": "iban",
    "IBAN 코드": "iban",
    # swift_bic
    "SWIFT": "swift_bic",
    "SWIFT 코드": "swift_bic",
    # paragraphs
    "문단": "paragraphs",
    "단락": "paragraphs",
    "설명 글": "paragraphs",
    # datetime
    "날짜": "datetime",
    "일시": "datetime",
    # time
    "시간": "time",
    # latitude
    "위도": "latitude",
    # longitude
    "경도": "longitude",
    # number_between_1_100
    "숫자": "number_between_1_100",
    "1과 100 사이 숫자": "number_between_1_100",
    "1~100 숫자": "number_between_1_100",
}

# 한글 → 영문 값 매핑 (state, country, 카드사 등)
KOR_TO_ENG_VALUE = {
    # state
    "서울": "Seoul",
    "도쿄": "Tokyo",
    "베이징": "Beijing",
    "뉴욕": "New York",
    "파리": "Île-de-France",
    "상파울루": "São Paulo",
    "마드리드": "Madrid",
    "모스크바": "Moscow",
    "이슬람불": "Istanbul",
    "바이에른": "Bavaria (Bayern)",
    "마하라슈트라": "Maharashtra",
    "온타리오": "Ontario",
    "뉴사우스웨일스": "New South Wales",
    "잉글랜드": "England",
    "캘리포니아": "California",
    # country
    "미국": "United States",
    "중국": "China",
    "독일": "Germany",
    "영국": "United Kingdom",
    "프랑스": "France",
    "일본": "Japan",
    "인도": "India",
    "러시아": "Russia",
    "대한민국": "South Korea",
    "한국": "South Korea",
    "브라질": "Brazil",
    "캐나다": "Canada",
    "이탈리아": "Italy",
    "호주": "Australia",
    "스페인": "Spain",
    "튀르키예": "Turkey",
    # 카드사
    "비자카드": "Visa",
    "마스터카드": "Mastercard",
    "아멕스카드": "American Express",
    "JCB카드": "JCB",
    "유니온페이": "China UnionPay",
    "마에스트로": "Maestro",
    "다이너스클럽": "Diners Club International",
    "아메리칸 익스프레스": "American Express",
    "아멕스": "Amex",
}

def parse_korean_text_to_json(text: str) -> dict:
    count_match = re.search(r'(\d+)\s*(명|개|건|줄|users|rows|entries|개체|개씩|개만)|at least (\d+)', text, re.IGNORECASE)
    if count_match:
        count = int(next(filter(None, count_match.groups())))
    else:
        count = 1

    # nullable 설정 파싱
    nullable_extractor = NullablePercentExtractor()
    nullable_percent = nullable_extractor.extract(text)

    fields = []
    unsupported_fields = []
    used_fields = set()

    # 1. 한글 키워드 매핑
    for kor, eng in KOR_TO_ENG_FIELD.items():
        if kor in text and eng not in used_fields:
            used_fields.add(eng)
            constraints = None
            # 조건이 붙을 수 있는 타입에만 조건 파싱 적용
            if eng in CONSTRAINT_TYPES:
                # number_between_1_100
                if eng == "number_between_1_100":
                    min_match = re.search(r'(\d+)\s*이상|at least (\d+)', text, re.IGNORECASE)
                    max_match = re.search(r'(\d+)\s*이하|under (\d+)', text, re.IGNORECASE)
                    decimals_match = re.search(r'소수점\s*(\d+)자리|decimals?\s*(\d+)', text, re.IGNORECASE)
                    cdict = {}
                    if min_match:
                        min_val = next(filter(None, min_match.groups()))
                        cdict["min"] = int(min_val)
                    if max_match:
                        max_val = next(filter(None, max_match.groups()))
                        # under 패턴인 경우 배타적 처리
                        if "under" in max_match.group(0).lower():
                            cdict["max"] = int(max_val) - 1
                        else:
                            cdict["max"] = int(max_val)
                    if decimals_match:
                        dec_val = next(filter(None, decimals_match.groups()))
                        cdict["decimals"] = int(dec_val)
                    if cdict:
                        constraints = cdict
                # password
                elif eng == "password":
                    # 최소 길이 패턴 (숫자 명시형)
                    minlen = re.search(r'(\d+)자 이상|minimum length:?\s*(\d+)', text, re.IGNORECASE)
                    
                    # 포함 패턴 (숫자 미명시형 - 기본값 1)
                    upper_include = re.search(r'대문자.*?(포함|되야해|되어야해|있어야\s*해)|(포함|되야해|되어야해|있어야\s*해).*?대문자', text, re.IGNORECASE)
                    lower_include = re.search(r'소문자.*?(포함|되야해|되어야해|있어야\s*해)|(포함|되야해|되어야해|있어야\s*해).*?소문자', text, re.IGNORECASE)
                    numbers_include = re.search(r'숫자.*?(포함|되야해|되어야해|있어야\s*해)|(포함|되야해|되어야해|있어야\s*해).*?숫자', text, re.IGNORECASE)
                    symbols_include = re.search(r'기호.*?(포함|되야해|되어야해|있어야\s*해)|특수문자.*?(포함|되야해|되어야해|있어야\s*해)', text, re.IGNORECASE)
                    
                    # 숫자 명시형 패턴
                    upper = re.search(r'대문자\s*(\d+)개|upper:?\s*(\d+)', text, re.IGNORECASE)
                    lower = re.search(r'소문자\s*(\d+)개|lower:?\s*(\d+)', text, re.IGNORECASE)
                    numbers = re.search(r'숫자\s*(\d+)개|numbers?:?\s*(\d+)', text, re.IGNORECASE)
                    symbols = re.search(r'특수문자\s*(\d+)개|기호\s*(\d+)개|symbols?:?\s*(\d+)', text, re.IGNORECASE)
                    
                    cdict = {}
                    if minlen:
                        minlen_val = next(filter(None, minlen.groups()))
                        cdict["minimum_length"] = int(minlen_val)
                    if upper:
                        upper_val = next(filter(None, upper.groups()))
                        cdict["upper"] = int(upper_val)
                    elif upper_include:
                        cdict["upper"] = 1
                    if lower:
                        lower_val = next(filter(None, lower.groups()))
                        cdict["lower"] = int(lower_val)
                    elif lower_include:
                        cdict["lower"] = 1
                    if numbers:
                        numbers_val = next(filter(None, numbers.groups()))
                        cdict["numbers"] = int(numbers_val)
                    elif numbers_include:
                        cdict["numbers"] = 1
                    if symbols:
                        symbols_val = next(filter(None, symbols.groups()))
                        cdict["symbols"] = int(symbols_val)
                    elif symbols_include:
                        cdict["symbols"] = 1
                    if cdict:
                        constraints = cdict
                # phone
                elif eng == "phone":
                    phone_format = None
                    for fmt in ["###-####-####", "(###) ###-####", "### ### ####", "+# ### ### ####", "+# (###) ###-####", "+#-###-###-####", "#-(###) ###-####", "##########"]:
                        if fmt.replace("#", "") in text:
                            phone_format = fmt
                    if phone_format:
                        constraints = {"format": phone_format}
                # avatar
                elif eng == "avatar":
                    avatar_size = re.search(r'(\d+)x(\d+)|size:?\s*(\d+)\s*[xX*]\s*(\d+)', text, re.IGNORECASE)
                    avatar_format = None
                    for fmt in ["png", "bmp", "jpg"]:
                        if fmt in text.lower():
                            avatar_format = fmt
                    cdict = {}
                    if avatar_size:
                        size_groups = avatar_size.groups()
                        w = next(filter(None, size_groups[0:3]))
                        h = next(filter(None, size_groups[1:4]))
                        cdict["size"] = f"{w}x{h}"
                    if avatar_format:
                        cdict["format"] = avatar_format
                    if cdict:
                        constraints = cdict
                # state
                elif eng == "state":
                    state_value = re.search(r'([가-힣A-Za-z \-\(\)]+)만|only ([A-Za-z \-\(\)]+)', text)
                    val = None
                    if state_value:
                        val = next(filter(None, state_value.groups())).strip()
                    if val:
                        val_eng = KOR_TO_ENG_VALUE.get(val, val)
                        if val_eng in SUPPORTED_STATES:
                            constraints = {"value": val_eng}
                        else:
                            return {"error": f"지원하지 않는 state 값입니다: {val}"}
                # country
                elif eng == "country":
                    country_value = re.search(r'([가-힣A-Za-z \-\(\)]+)만|only ([A-Za-z \-\(\)]+)', text)
                    val = None
                    if country_value:
                        val = next(filter(None, country_value.groups())).strip()
                    if val:
                        val_eng = KOR_TO_ENG_VALUE.get(val, val)
                        if val_eng in SUPPORTED_COUNTRIES:
                            constraints = {"value": val_eng}
                        else:
                            return {"error": f"지원하지 않는 country 값입니다: {val}"}
                # datetime
                elif eng == "datetime":
                    dt_from = re.search(r'(\d{4}-\d{2}-\d{2})부터|from (\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
                    dt_to = re.search(r'부터\s*(\d{4}-\d{2}-\d{2})까지|to (\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
                    dt_format = re.search(r'(yyyy-mm-dd|m/d/yyyy|d/m/yyyy)', text, re.IGNORECASE)
                    cdict = {}
                    if dt_from:
                        from_val = next(filter(None, dt_from.groups()))
                        cdict["from"] = from_val
                    if dt_to:
                        to_val = next(filter(None, dt_to.groups()))
                        cdict["to"] = to_val
                    if dt_format:
                        cdict["format"] = dt_format.group(1)
                    if cdict:
                        constraints = cdict
                # time
                elif eng == "time":
                    time_from = re.search(r'(오전|오후)?\s*(\d{1,2})시부터|from (\d{1,2})(am|pm)?', text, re.IGNORECASE)
                    time_to = re.search(r'부터\s*(오전|오후)?\s*(\d{1,2})시까지|to (\d{1,2})(am|pm)?', text, re.IGNORECASE)
                    time_format = re.search(r'(12시간제|24시간제|12 ?hour|24 ?hour)', text, re.IGNORECASE)
                    cdict = {}
                    if time_from:
                        if time_from.group(1):
                            cdict["from"] = f"{time_from.group(1)}{time_from.group(2)}"
                        elif time_from.group(3):
                            cdict["from"] = f"{time_from.group(2)}{time_from.group(3)}"
                    if time_to:
                        if time_to.group(1):
                            cdict["to"] = f"{time_to.group(1)}{time_to.group(2)}"
                        elif time_to.group(3):
                            cdict["to"] = f"{time_to.group(2)}{time_to.group(3)}"
                    if time_format:
                        cdict["format"] = time_format.group(1)
                    if cdict:
                        constraints = cdict
                # url
                elif eng == "url":
                    url_protocol = "protocol" in text.lower() or "프로토콜" in text
                    url_host = "host" in text.lower() or "호스트" in text
                    url_path = "path" in text.lower() or "경로" in text
                    url_query = "query" in text.lower() or "쿼리" in text
                    cdict = {}
                    if url_protocol:
                        cdict["protocol"] = True
                    if url_host:
                        cdict["host"] = True
                    if url_path:
                        cdict["path"] = True
                    if url_query:
                        cdict["query"] = True
                    if cdict:
                        constraints = cdict
                # credit_card_number
                elif eng == "credit_card_number":
                    card_type = None
                    for t in SUPPORTED_CARD_TYPES:
                        kor_t = [k for k, v in KOR_TO_ENG_VALUE.items() if v == t]
                        if t.lower() in text.lower() or any(k in text for k in kor_t):
                            card_type = t
                    if card_type:
                        constraints = {"type": card_type}
                    else:
                        return {"error": "지원하지 않는 카드사입니다."}
                # credit_card_type
                elif eng == "credit_card_type":
                    cct_value = None
                    for t in SUPPORTED_CARD_TYPES:
                        kor_t = [k for k, v in KOR_TO_ENG_VALUE.items() if v == t]
                        if t.lower() in text.lower() or any(k in text for k in kor_t):
                            cct_value = t
                    if cct_value:
                        constraints = {"value": cct_value}
                    else:
                        return {"error": "지원하지 않는 카드사입니다."}
                # paragraphs
                elif eng == "paragraphs":
                    para_min = re.search(r'최소\s*(\d+)문단|at least (\d+) paragraphs?', text, re.IGNORECASE)
                    para_max = re.search(r'최대\s*(\d+)문단|no more than (\d+) paragraphs?', text, re.IGNORECASE)
                    cdict = {}
                    if para_min:
                        min_val = next(filter(None, para_min.groups()))
                        cdict["min"] = int(min_val)
                    if para_max:
                        max_val = next(filter(None, para_max.groups()))
                        cdict["max"] = int(max_val)
                    if cdict:
                        constraints = cdict
                # email_address
                elif eng == "email_address":
                    # 네이버, 구글 등 한글 도메인명 매핑
                    korean_domain_mapping = {
                        "네이버": "naver.com",
                        "구글": "gmail.com",
                        "gmail": "gmail.com",  # 영문 gmail도 추가
                        "야후": "yahoo.com",
                        "핫메일": "hotmail.com",
                        "아웃룩": "outlook.com",
                        "다음": "daum.net",
                        "네이트": "nate.com",
                        "한메일": "hanmail.net",
                        "아이클라우드": "icloud.com",
                        "프로톤메일": "protonmail.com"
                    }
                    
                    # 지원하는 도메인 목록
                    supported_domains = {
                        "naver.com", "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
                        "daum.net", "nate.com", "hanmail.net", "icloud.com", "protonmail.com"
                    }
                    
                    cdict = {}
                    
                    # 여러 도메인 제약 조건 파싱 (예: "네이버나 구글 이메일") - 먼저 확인
                    domains = []
                    for kor_domain, eng_domain in korean_domain_mapping.items():
                        if kor_domain in text:
                            domains.append(eng_domain)
                    
                    if len(domains) > 1:
                        cdict["domains"] = domains
                    else:
                        # 단일 도메인 제약 조건 파싱
                        for kor_domain, eng_domain in korean_domain_mapping.items():
                            if f"{kor_domain}만" in text or f"{kor_domain} 이메일" in text:
                                cdict["domain"] = eng_domain
                                break
                        
                        # 영문 도메인 직접 매칭
                        if not cdict:
                            for domain in supported_domains:
                                if f"{domain}만" in text or f"{domain} 이메일" in text:
                                    cdict["domain"] = domain
                                    break
                    
                    if cdict:
                        constraints = cdict
                # korean_full_name
                elif eng == "korean_full_name":
                    # 성씨 제약 조건 파싱 (예: "김씨인 사람만", "이씨만", "박씨")
                    # 성씨 제약 조건 파싱 - 더 간단하고 명확한 접근
                    # 모든 "~씨" 패턴을 찾아서 성씨만 추출
                    lastname_match = re.search(r'([가-힣]+)씨', text)
                    if lastname_match:
                        lastname = lastname_match.group(1)
                        constraints = {"lastName": lastname}
            # 나머지 타입은 constraints 없이 제공
            if eng not in SUPPORTED_TYPES:
                unsupported_fields.append(eng)
            else:
                if eng == "number_between_1_100":
                    field_type = "number"
                elif eng.startswith("korean_") and "phone" in eng:
                    field_type = "string"
                else:
                    field_type = "string"
                field_obj = {"type": eng}
                if constraints is not None:
                    field_obj["constraints"] = constraints
                # nullable 설정 추가
                if nullable_percent > 0:
                    field_obj["nullablePercent"] = nullable_percent
                fields.append(field_obj)

    # 2. 영문 타입명 직접 매칭
    for eng in SUPPORTED_TYPES:
        # "로", "만" 등 조사 제거 후 타입명만 추출
        if (f"{eng}로" in text or f"{eng}만" in text or eng in text) and eng not in used_fields:
            used_fields.add(eng)
            constraints = None
            # 조건이 붙을 수 있는 타입에만 constraints 파싱 적용
            if eng in CONSTRAINT_TYPES:
                # number_between_1_100
                if eng == "number_between_1_100":
                    min_match = re.search(r'(\d+)\s*이상', text)
                    max_match = re.search(r'(\d+)\s*이하', text)
                    decimals_match = re.search(r'소수점\s*(\d+)자리', text)
                    cdict = {}
                    if min_match:
                        cdict["min"] = int(min_match.group(1))
                    if max_match:
                        cdict["max"] = int(max_match.group(1))
                    if decimals_match:
                        cdict["decimals"] = int(decimals_match.group(1))
                    if cdict:
                        constraints = cdict
                # password
                elif eng == "password":
                    minlen = re.search(r'(\d+)자 이상', text)
                    upper = re.search(r'대문자\s*(\d+)개', text)
                    lower = re.search(r'소문자\s*(\d+)개', text)
                    numbers = re.search(r'숫자\s*(\d+)개', text)
                    symbols = re.search(r'특수문자\s*(\d+)개', text)
                    cdict = {}
                    if minlen:
                        cdict["min_length"] = int(minlen.group(1))
                    if upper:
                        cdict["upper"] = int(upper.group(1))
                    if lower:
                        cdict["lower"] = int(lower.group(1))
                    if numbers:
                        cdict["numbers"] = int(numbers.group(1))
                    if symbols:
                        cdict["symbols"] = int(symbols.group(1))
                    if cdict:
                        constraints = cdict
                # phone
                elif eng == "phone":
                    phone_format = None
                    for fmt in ["###-####-####", "(###) ###-####", "### ### ####", "+# ### ### ####", "+# (###) ###-####", "+#-###-###-####", "#-(###) ###-####", "##########"]:
                        if fmt.replace("#", "") in text:
                            phone_format = fmt
                    if phone_format:
                        constraints = {"format": phone_format}
                # avatar
                elif eng == "avatar":
                    avatar_size = re.search(r'(\d+)x(\d+)', text)
                    avatar_format = None
                    for fmt in ["png", "bmp", "jpg"]:
                        if fmt in text:
                            avatar_format = fmt
                    cdict = {}
                    if avatar_size:
                        cdict["size"] = f"{avatar_size.group(1)}x{avatar_size.group(2)}"
                    if avatar_format:
                        cdict["format"] = avatar_format
                    if cdict:
                        constraints = cdict
                # state
                elif eng == "state":
                    state_value = re.search(r'([가-힣A-Za-z ]+)만', text)
                    if state_value:
                        val = state_value.group(1).strip()
                        val_eng = KOR_TO_ENG_VALUE.get(val, val)
                        if val_eng in SUPPORTED_STATES:
                            constraints = {"value": val_eng}
                        else:
                            return {"error": f"지원하지 않는 state 값입니다: {val}"}
                # country
                elif eng == "country":
                    country_value = re.search(r'([가-힣A-Za-z ]+)만', text)
                    if country_value:
                        val = country_value.group(1).strip()
                        val_eng = KOR_TO_ENG_VALUE.get(val, val)
                        if val_eng in SUPPORTED_COUNTRIES:
                            constraints = {"value": val_eng}
                        else:
                            return {"error": f"지원하지 않는 country 값입니다: {val}"}
                # datetime
                elif eng == "datetime":
                    dt_from = re.search(r'(\d{4}-\d{2}-\d{2})부터', text)
                    dt_to = re.search(r'부터\s*(\d{4}-\d{2}-\d{2})까지', text)
                    dt_format = re.search(r'(yyyy-mm-dd|m/d/yyyy|d/m/yyyy)', text)
                    cdict = {}
                    if dt_from:
                        cdict["from"] = dt_from.group(1)
                    if dt_to:
                        cdict["to"] = dt_to.group(1)
                    if dt_format:
                        cdict["format"] = dt_format.group(1)
                    if cdict:
                        constraints = cdict
                # time
                elif eng == "time":
                    time_from = re.search(r'(오전|오후)?\s*(\d{1,2})시부터', text)
                    time_to = re.search(r'부터\s*(오전|오후)?\s*(\d{1,2})시까지', text)
                    time_format = re.search(r'(12시간제|24시간제)', text)
                    cdict = {}
                    if time_from:
                        cdict["from"] = f"{time_from.group(1) or ''}{time_from.group(2)}"
                    if time_to:
                        cdict["to"] = f"{time_to.group(1) or ''}{time_to.group(2)}"
                    if time_format:
                        cdict["format"] = time_format.group(1)
                    if cdict:
                        constraints = cdict
                # url
                elif eng == "url":
                    url_protocol = "protocol" in text or "프로토콜" in text
                    url_host = "host" in text or "호스트" in text
                    url_path = "path" in text or "경로" in text
                    url_query = "query" in text or "쿼리" in text
                    cdict = {}
                    if url_protocol:
                        cdict["protocol"] = True
                    if url_host:
                        cdict["host"] = True
                    if url_path:
                        cdict["path"] = True
                    if url_query:
                        cdict["query"] = True
                    if cdict:
                        constraints = cdict
                # credit_card_number
                elif eng == "credit_card_number":
                    card_type = None
                    for t in SUPPORTED_CARD_TYPES:
                        kor_t = [k for k, v in KOR_TO_ENG_VALUE.items() if v == t]
                        if t.lower() in text.lower() or any(k in text for k in kor_t):
                            card_type = t
                    if card_type:
                        constraints = {"type": card_type}
                    else:
                        return {"error": "지원하지 않는 카드사입니다."}
                # credit_card_type
                elif eng == "credit_card_type":
                    cct_value = None
                    for t in SUPPORTED_CARD_TYPES:
                        kor_t = [k for k, v in KOR_TO_ENG_VALUE.items() if v == t]
                        if t.lower() in text.lower() or any(k in text for k in kor_t):
                            cct_value = t
                    if cct_value:
                        constraints = {"value": cct_value}
                    else:
                        return {"error": "지원하지 않는 카드사입니다."}
                # paragraphs
                elif eng == "paragraphs":
                    para_min = re.search(r'최소\s*(\d+)문단', text)
                    para_max = re.search(r'최대\s*(\d+)문단', text)
                    cdict = {}
                    if para_min:
                        cdict["min"] = int(para_min.group(1))
                    if para_max:
                        cdict["max"] = int(para_max.group(1))
                    if cdict:
                        constraints = cdict
                # email_address
                elif eng == "email_address":
                    # 네이버, 구글 등 한글 도메인명 매핑
                    korean_domain_mapping = {
                        "네이버": "naver.com",
                        "구글": "gmail.com",
                        "gmail": "gmail.com",  # 영문 gmail도 추가
                        "야후": "yahoo.com",
                        "핫메일": "hotmail.com",
                        "아웃룩": "outlook.com",
                        "다음": "daum.net",
                        "네이트": "nate.com",
                        "한메일": "hanmail.net",
                        "아이클라우드": "icloud.com",
                        "프로톤메일": "protonmail.com"
                    }
                    
                    # 지원하는 도메인 목록
                    supported_domains = {
                        "naver.com", "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
                        "daum.net", "nate.com", "hanmail.net", "icloud.com", "protonmail.com"
                    }
                    
                    cdict = {}
                    
                    # 여러 도메인 제약 조건 파싱 (예: "네이버나 구글 이메일") - 먼저 확인
                    domains = []
                    for kor_domain, eng_domain in korean_domain_mapping.items():
                        if kor_domain in text:
                            domains.append(eng_domain)
                    
                    if len(domains) > 1:
                        cdict["domains"] = domains
                    else:
                        # 단일 도메인 제약 조건 파싱
                        for kor_domain, eng_domain in korean_domain_mapping.items():
                            if f"{kor_domain}만" in text or f"{kor_domain} 이메일" in text:
                                cdict["domain"] = eng_domain
                                break
                        
                        # 영문 도메인 직접 매칭
                        if not cdict:
                            for domain in supported_domains:
                                if f"{domain}만" in text or f"{domain} 이메일" in text:
                                    cdict["domain"] = domain
                                    break
                    
                    if cdict:
                        constraints = cdict
                # korean_full_name
                elif eng == "korean_full_name":
                    # 성씨 제약 조건 파싱 (예: "김씨인 사람만", "이씨만", "박씨")
                    # 성씨 제약 조건 파싱 - 더 간단하고 명확한 접근
                    # 모든 "~씨" 패턴을 찾아서 성씨만 추출
                    lastname_match = re.search(r'([가-힣]+)씨', text)
                    if lastname_match:
                        lastname = lastname_match.group(1)
                        constraints = {"lastName": lastname}
            if eng not in SUPPORTED_TYPES:
                unsupported_fields.append(eng)
            else:
                if eng == "number_between_1_100":
                    field_type = "number"
                elif eng.startswith("korean_") and "phone" in eng:
                    field_type = "string"
                else:
                    field_type = "string"
                field_obj = {"type": eng}
                if constraints is not None:
                    field_obj["constraints"] = constraints
                # nullable 설정 추가
                if nullable_percent > 0:
                    field_obj["nullablePercent"] = nullable_percent
                fields.append(field_obj)

    if unsupported_fields:
        return {
            "error": f"지원하지 않는 데이터 타입입니다: {', '.join(unsupported_fields)}",
            "unsupported_fields": unsupported_fields
        }

    if not fields:
        return {
            "error": "추출된 데이터 필드가 없습니다. 입력을 확인해 주세요."
        }

    return {
        "count": count,
        "fields": fields
    }

# 혼합 입력 테스트 케이스 추가
if __name__ == "__main__":
    test_cases = [
        # 이메일 제약 조건 테스트
        "네이버만 이메일 3개",
        "gmail만 이메일 2개",
        "네이버나 구글 이메일 5개",
        "naver.com만 이메일 주소 1개",
        # 혼합 입력 예시
        "10 users, 이메일은 gmail만, 나이는 under 40",
        "Generate 5개 email_address, 이름은 한국어로",
        "최소 2문단, no more than 5 paragraphs",
        "50x50 png avatar, size: 100x100, format: jpg 2개",
        # 기존 테스트 케이스
        "언어 5개",
        "서울만 state로 5개",
        "파리만 state로 3개",
        "한국만 country로 2개",
        "브라질만 country로 2개",
        "비자카드만 credit_card_number로 2개",
        "아멕스카드만 credit_card_type로 2개",
        "없는나라 country로 1개",
        "없는카드 credit_card_type로 1개",
        "비밀번호 8자 이상, 대문자 1개, blank 0% 3개",
        "50x50 png avatar 2개",
        "10 이상 50 이하 소수점 2자리 number_between_1_100 4개"
    ]
    for text in test_cases:
        print(f"입력: {text}")
        print(parse_korean_text_to_json(text))
        print("-" * 40)