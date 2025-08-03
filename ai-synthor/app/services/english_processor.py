EN_TO_TYPE_FIELD = {
    # 개인정보
    "full name": "full_name", "fullname": "full_name", "name": "full_name",
    "first name": "first_name", "given name": "first_name",
    "last name": "last_name", "surname": "last_name",
    "phone": "phone", "phone number": "phone",
    # 주소
    "address": "address", "full address": "address",
    "street address": "street_address", "road address": "street_address",
    "city": "city",
    "state": "state", "province": "state", "region": "state",
    "country": "country", "nation": "country",
    "postal code": "postal_code", "zip code": "postal_code",
    # 회사 및 상업
    "company name": "company_name", "company": "company_name",
    "job title": "job_title", "position": "job_title",
    "department": "department_corporate", "corporate department": "department_corporate",
    "retail department": "department_retail",
    "product name": "product_name",
    "product category": "product_category",
    "catch phrase": "catch_phrase", "slogan": "catch_phrase",
    "product description": "product_description",
    # 기타
    "language": "language",
    "color": "color",
    # 언어 중립적 데이터 타입
    "username": "username", "user name": "username",
    "password": "password",
    "email": "email_address", "email address": "email_address",
    "domain name": "domain_name",
    "url": "url", "link": "url", "website": "url",
    "mac address": "mac_address",
    "ipv4 address": "ip_v4_address",
    "ipv6 address": "ip_v6_address",
    "user agent": "user_agent",
    "avatar": "avatar", "profile image": "avatar",
    # 앱 및 기기
    "app name": "app_name",
    "app version": "app_version",
    "device model": "device_model",
    "device brand": "device_brand",
    "device os": "device_os", "os": "device_os",
    # 금융
    "credit card number": "credit_card_number",
    "credit card type": "credit_card_type",
    "product price": "product_price",
    "currency": "currency",
    "iban": "iban",
    "swift bic": "swift_bic",
    # 기타
    "paragraph": "paragraphs", "paragraphs": "paragraphs",
    "datetime": "datetime", "date": "datetime",
    "time": "time",
    "latitude": "latitude",
    "longitude": "longitude",
    "number": "number_between_1_100", "number between 1 and 100": "number_between_1_100",
}

import re

def get_field_type_from_eng(keyword):
    if keyword in EN_TO_TYPE_FIELD:
        return EN_TO_TYPE_FIELD[keyword]
    keyword_no_space = keyword.replace(" ", "")
    if keyword_no_space in EN_TO_TYPE_FIELD:
        return EN_TO_TYPE_FIELD[keyword_no_space]
    return None

def parse_english_text_to_json(text: str) -> dict:
    count_match = re.search(r'(?:generate|create|make)?\s*(\d+)\s*(users?|rows?|entries?|samples?|개|명|개체|개만|개씩)?', text, re.IGNORECASE)
    count = int(count_match.group(1)) if count_match else 1

    fields = []
    used_fields = set()

    for eng_kw in EN_TO_TYPE_FIELD.keys():
        if eng_kw in text.lower():
            type_name = get_field_type_from_eng(eng_kw)
            if type_name and type_name not in used_fields:
                used_fields.add(type_name)
                constraints = None
                # 12개 타입 robust constraints
                if type_name == "password":
                    minlen = re.search(r'minimum length:?\s*(\d+)', text, re.IGNORECASE)
                    upper = re.search(r'upper:?\s*(\d+)', text, re.IGNORECASE)
                    lower = re.search(r'lower:?\s*(\d+)', text, re.IGNORECASE)
                    numbers = re.search(r'numbers?:?\s*(\d+)', text, re.IGNORECASE)
                    symbols = re.search(r'symbols?:?\s*(\d+)', text, re.IGNORECASE)
                    cdict = {}
                    if minlen: cdict["min_length"] = int(minlen.group(1))
                    if upper: cdict["upper"] = int(upper.group(1))
                    if lower: cdict["lower"] = int(lower.group(1))
                    if numbers: cdict["numbers"] = int(numbers.group(1))
                    if symbols: cdict["symbols"] = int(symbols.group(1))
                    if cdict: constraints = cdict
                if type_name == "phone":
                    phone_format = None
                    for fmt in ["###-####-####", "(###) ###-####", "### ### ####", "+# ### ### ####", "+# (###) ###-####", "+#-###-###-####", "#-(###) ###-####", "##########"]:
                        if fmt.replace("#", "") in text:
                            phone_format = fmt
                    if phone_format:
                        constraints = {"format": phone_format}
                if type_name == "avatar":
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
                if type_name == "state":
                    state_value = re.search(r'state:?\s*([A-Za-z \-\(\)]+)', text)
                    if state_value:
                        val = state_value.group(1).strip()
                        constraints = {"value": val}
                if type_name == "country":
                    country_value = re.search(r'country:?\s*([A-Za-z \-\(\)]+)', text)
                    if country_value:
                        val = country_value.group(1).strip()
                        constraints = {"value": val}
                if type_name == "datetime":
                    dt_from = re.search(r'from (\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
                    dt_to = re.search(r'to (\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
                    dt_format = re.search(r'(yyyy-mm-dd|m/d/yyyy|d/m/yyyy)', text, re.IGNORECASE)
                    cdict = {}
                    if dt_from: cdict["from"] = dt_from.group(1)
                    if dt_to: cdict["to"] = dt_to.group(1)
                    if dt_format: cdict["format"] = dt_format.group(1)
                    if cdict: constraints = cdict
                if type_name == "time":
                    time_from = re.search(r'from (\d{1,2})(am|pm)?', text, re.IGNORECASE)
                    time_to = re.search(r'to (\d{1,2})(am|pm)?', text, re.IGNORECASE)
                    time_format = re.search(r'(12 ?hour|24 ?hour)', text, re.IGNORECASE)
                    cdict = {}
                    if time_from:
                        cdict["from"] = f"{time_from.group(1)}{time_from.group(2) or ''}"
                    if time_to:
                        cdict["to"] = f"{time_to.group(1)}{time_to.group(2) or ''}"
                    if time_format:
                        cdict["format"] = time_format.group(1)
                    if cdict: constraints = cdict
                if type_name == "url":
                    url_protocol = "protocol" in text.lower()
                    url_host = "host" in text.lower()
                    url_path = "path" in text.lower()
                    url_query = "query" in text.lower()
                    cdict = {}
                    if url_protocol: cdict["protocol"] = True
                    if url_host: cdict["host"] = True
                    if url_path: cdict["path"] = True
                    if url_query: cdict["query"] = True
                    if cdict: constraints = cdict
                if type_name == "credit_card_number":
                    card_type = None
                    for t in ["Visa", "Mastercard", "American Express", "Amex", "JCB", "China UnionPay", "Maestro", "Diners Club International"]:
                        if t.lower() in text.lower():
                            card_type = t
                    if card_type:
                        constraints = {"type": card_type}
                if type_name == "credit_card_type":
                    cct_value = None
                    for t in ["Visa", "Mastercard", "American Express", "Amex", "JCB", "China UnionPay", "Maestro", "Diners Club International"]:
                        if t.lower() in text.lower():
                            cct_value = t
                    if cct_value:
                        constraints = {"value": cct_value}
                if type_name == "paragraphs":
                    para_min = re.search(r'at least (\d+) paragraphs?', text, re.IGNORECASE)
                    para_max = re.search(r'no more than (\d+) paragraphs?', text, re.IGNORECASE)
                    cdict = {}
                    if para_min: cdict["min"] = int(para_min.group(1))
                    if para_max: cdict["max"] = int(para_max.group(1))
                    if cdict: constraints = cdict
                if type_name == "number_between_1_100":
                    under = re.search(r'under (\d+)', text, re.IGNORECASE)
                    over = re.search(r'over (\d+)', text, re.IGNORECASE)
                    at_least = re.search(r'at least (\d+)', text, re.IGNORECASE)
                    decimals = re.search(r'decimals?\s*(\d+)', text, re.IGNORECASE)
                    cdict = {}
                    if under: cdict["max"] = int(under.group(1))
                    if over: cdict["min"] = int(over.group(1))
                    if at_least: cdict["min"] = int(at_least.group(1))
                    if decimals: cdict["decimals"] = int(decimals.group(1))
                    if cdict: constraints = cdict
                field_obj = {"name": type_name, "type": "string" if type_name != "number_between_1_100" else "number"}
                if constraints:
                    field_obj["constraints"] = constraints
                fields.append(field_obj)

    if not fields:
        return {"error": "No valid fields found in input."}

    return {
        "count": count,
        "fields": fields
    }

if __name__ == "__main__":
    test_cases = [
        "Generate 10 users with Gmail emails under 40 years old",
        "Create 5 samples, full name, email address only gmail, age over 20",
        "10 users, phone number, at least 2 paragraphs, no more than 5 paragraphs",
        "Generate 3 avatars, company, city, country",
        "fullname 2개, email address, under 30",
        "paragraphs at least 2, no more than 4",
        "phone, gmail only, number over 10",
        "password minimum length 8 upper 1 lower 1 numbers 1 symbols 1",
        "avatar size 50x50 format png",
        "state: California, country: United States",
        "datetime from 2024-01-01 to 2024-12-31 format yyyy-mm-dd",
        "time from 9am to 6pm 24 hour",
        "url protocol host path query",
        "credit card number Visa",
        "credit card type Mastercard",
        "latitude, longitude, product price, swift bic, iban"
    ]
    for text in test_cases:
        print(f"Input: {text}")
        print(parse_english_text_to_json(text))
        print("-" * 40)