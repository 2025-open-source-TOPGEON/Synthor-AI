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

# 한글 → 영문/한국어 타입 매핑 (예시, 필요시 계속 확장)
KOR_TO_ENG_FIELD = {
    # 개인정보
    "이름": "korean_full_name",
    "성명": "korean_full_name",
    "이메일": "email_address",
    "나이": "number_between_1_100",  # 실제로는 조건 파싱 필요
    "성별": "gender",  # 필요시 추가
    "아이디": "username",
    "비밀번호": "password",
    "전화번호": "korean_phone",
    # 주소
    "주소": "korean_address",
    "도로명주소": "korean_street_address",
    "도시": "korean_city",
    "도": "korean_state",
    "시": "korean_state",
    "국가": "korean_country",
    "우편번호": "korean_postal_code",
    # 회사 및 상업
    "회사": "korean_company_name",
    "직책": "korean_job_title",
    "부서": "korean_department_corporate",  # 또는 korean_department_retail
    "제품명": "korean_product_name",
    "제품 카테고리": "korean_product_category",
    "캐치프레이즈": "korean_catch_phrase",
    "제품 설명": "korean_product_description",
    # 기타
    "언어": "korean_language",
    "색상": "korean_color",
    # 언어 중립
    "도메인": "domain_name",
    "URL": "url",
    "MAC": "mac_address",
    "IPv4": "ip_v4_address",
    "IPv6": "ip_v6_address",
    "유저 에이전트": "user_agent",
    "아바타": "avatar",
    "앱 이름": "app_name",
    "앱 버전": "app_version",
    "기기 모델": "device_model",
    "기기 제조사": "device_brand",
    "운영체제": "device_os",
    "신용카드 번호": "credit_card_number",
    "신용카드 종류": "credit_card_type",
    "상품 가격": "product_price",
    "통화": "currency",
    "IBAN": "iban",
    "SWIFT": "swift_bic",
    "문단": "paragraphs",
    "날짜": "datetime",
    "시간": "time",
    "위도": "latitude",
    "경도": "longitude",
    # 필요시 계속 확장
}