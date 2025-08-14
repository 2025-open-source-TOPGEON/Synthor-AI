# 타입/지원값 상수

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

# 제약이 붙는 타입
CONSTRAINT_TYPES = {
    "password", "phone", "avatar", "state", "country", "datetime", "time", "url",
    "credit_card_number", "credit_card_type", "paragraphs", "number_between_1_100", "korean_full_name", "korean_last_name", "email_address"
}

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