from difflib import get_close_matches
import re

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
    "profile picture": "avatar", "profile pic": "avatar", "profile photo": "avatar",
    "profile icon": "avatar", "profile graphic": "avatar", "profile figure": "avatar",
    "profile character": "avatar", "user icon": "avatar", "user image": "avatar",
    "user photo": "avatar", "account icon": "avatar", "account image": "avatar",
    "account picture": "avatar", "character image": "avatar", "character icon": "avatar",
    "character graphic": "avatar", "profile thumbnail": "avatar", "profile portrait": "avatar",
    "avatar image": "avatar", "avatar picture": "avatar", "avatar photo": "avatar",
    "avatar icon": "avatar", "avatar image file": "avatar", "avatar jpg": "avatar",
    "avatar png": "avatar", "profile avatar": "avatar", "profile picture": "avatar",
    "profile photo": "avatar", "character avatar": "avatar", "character image": "avatar",
    "user avatar": "avatar", "user image": "avatar", "account avatar": "avatar",
    "account image": "avatar",
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

def get_field_type_from_eng(keyword):
    if keyword in EN_TO_TYPE_FIELD:
        return EN_TO_TYPE_FIELD[keyword]
    keyword_no_space = keyword.replace(" ", "")
    if keyword_no_space in EN_TO_TYPE_FIELD:
        return EN_TO_TYPE_FIELD[keyword_no_space]
    return None

def suggest_type(input_type, supported_types):
    matches = get_close_matches(input_type, supported_types, n=1, cutoff=0.6)
    if matches:
        return matches[0]
    return None

def extract_count(text):
    # 가장 앞에 등장하는 명확한 개수 패턴만 count로 사용
    count_patterns = [
        r'(\d+)\s*(users?|rows?|entries?|samples?|개|명|개만|개씩)',
        r'at least (\d+) paragraphs?',
        r'(\d+)\s*개',
    ]
    for pat in count_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return 1

def parse_english_text_to_json(text: str) -> dict:
    count = extract_count(text)
    fields = []
    used_fields = set()
    supported_types = list(EN_TO_TYPE_FIELD.values())
    last_field = None
    segments = [seg.strip() for seg in re.split(r'[,.]', text)]
    # number_between_1_100은 명시적으로 등장할 때만 필드로 추가
    explicit_number = any(
        key in text.lower() for key in ["number", "number between 1 and 100"]
    )
    for seg in segments:
        found = False
        for key in EN_TO_TYPE_FIELD.keys():
            # number_between_1_100은 명시적으로 등장할 때만 필드로 추가
            if EN_TO_TYPE_FIELD[key] == "number_between_1_100" and not explicit_number:
                continue
            if key in seg.lower() and EN_TO_TYPE_FIELD[key] not in used_fields:
                used_fields.add(EN_TO_TYPE_FIELD[key])
                field_obj = {"name": EN_TO_TYPE_FIELD[key], "type": "string" if EN_TO_TYPE_FIELD[key] != "number_between_1_100" else "number"}
                # password constraints
                if EN_TO_TYPE_FIELD[key] == "password":
                    cdict = {}
                    minlen = re.search(r'(\d+)\s*(자 이상|characters? minimum|minimum length)', seg, re.IGNORECASE)
                    upper = re.search(r'(\d+)\s*(대문자|upper)', seg, re.IGNORECASE)
                    lower = re.search(r'(\d+)\s*(소문자|lower)', seg, re.IGNORECASE)
                    numbers = re.search(r'(\d+)\s*(숫자|numbers?)', seg, re.IGNORECASE)
                    symbols = re.search(r'(\d+)\s*(기호|symbols?)', seg, re.IGNORECASE)
                    if minlen: cdict["min_length"] = int(minlen.group(1))
                    if upper: cdict["upper"] = int(upper.group(1))
                    if lower: cdict["lower"] = int(lower.group(1))
                    if numbers: cdict["numbers"] = int(numbers.group(1))
                    if symbols: cdict["symbols"] = int(symbols.group(1))
                    if cdict: field_obj["constraints"] = cdict
                # avatar
                if EN_TO_TYPE_FIELD[key] == "avatar":
                    avatar_size = re.search(r'(\d+)x(\d+)|size:?\s*(\d+)\s*[xX*]\s*(\d+)', seg, re.IGNORECASE)
                    avatar_format = None
                    
                    # format 처리 개선 - 자연어 표현 포함
                    fmt_patterns = {
                        "png": r'\bpng\b|png\s*format|format\s*[:=]?\s*png|png\s*type|save\s*as\s*png|png\s*로',
                        "bmp": r'\bbmp\b|bmp\s*format|format\s*[:=]?\s*bmp|bmp\s*type|save\s*as\s*bmp|bmp\s*로',
                        "jpg": r'\bjpg\b|\bjpeg\b|jpe?g\s*format|format\s*[:=]?\s*(?:jpg|jpeg)|jpe?g\s*type|save\s*as\s*jpe?g|jpe?g\s*로',
                    }
                    
                    found_formats = []
                    for norm_fmt, pattern in fmt_patterns.items():
                        if re.search(pattern, seg, re.IGNORECASE):
                            if norm_fmt not in found_formats:
                                found_formats.append(norm_fmt)
                    
                    if found_formats:
                        if len(found_formats) == 1:
                            avatar_format = found_formats[0]
                        else:
                            # 순서를 맞추기 위해 정렬 (jpg, png, bmp 순서)
                            format_order = {"jpg": 0, "png": 1, "bmp": 2}
                            sorted_formats = sorted(found_formats, key=lambda x: format_order.get(x, 3))
                            avatar_format = sorted_formats[0]  # 첫 번째 것을 선택
                    
                    cdict = {}
                    if avatar_size:
                        size_groups = avatar_size.groups()
                        w = next(filter(None, size_groups[0:3]))
                        h = next(filter(None, size_groups[1:4]))
                        cdict["size"] = f"{w}x{h}"
                    if avatar_format:
                        cdict["format"] = avatar_format
                    if cdict:
                        field_obj["constraints"] = cdict
                # paragraphs
                if EN_TO_TYPE_FIELD[key] == "paragraphs":
                    cdict = {}
                    para_min = re.search(r'at least (\d+)', seg, re.IGNORECASE)
                    para_max = re.search(r'no more than (\d+)', seg, re.IGNORECASE)
                    if para_min: cdict["min"] = int(para_min.group(1))
                    if para_max: cdict["max"] = int(para_max.group(1))
                    if cdict: field_obj["constraints"] = cdict
                # number_between_1_100
                if EN_TO_TYPE_FIELD[key] == "number_between_1_100":
                    cdict = {}
                    under = re.search(r'under (\d+)', seg, re.IGNORECASE)
                    over = re.search(r'over (\d+)', seg, re.IGNORECASE)
                    at_least = re.search(r'at least (\d+)', seg, re.IGNORECASE)
                    decimals = re.search(r'decimals?\s*(\d+)', seg, re.IGNORECASE)
                    if under: cdict["max"] = int(under.group(1)) - 1  # 배타적 처리
                    if over: cdict["min"] = int(over.group(1))
                    if at_least: cdict["min"] = int(at_least.group(1))
                    if decimals: cdict["decimals"] = int(decimals.group(1))
                    if cdict: field_obj["constraints"] = cdict
                fields.append(field_obj)
                last_field = field_obj
                found = True
        # 조건만 있는 segment는 직전 필드가 constraints를 가질 수 있을 때만 붙임
        if not found and seg and last_field is not None:
            if last_field["name"] in ["password", "paragraphs", "number_between_1_100", "email_address"]:
                cdict = last_field.get("constraints", {})
                # password 조건
                if last_field["name"] == "password":
                    minlen = re.search(r'(\d+)\s*(자 이상|characters? minimum|minimum length)', seg, re.IGNORECASE)
                    upper = re.search(r'(\d+)\s*(대문자|upper)', seg, re.IGNORECASE)
                    lower = re.search(r'(\d+)\s*(소문자|lower)', seg, re.IGNORECASE)
                    numbers = re.search(r'(\d+)\s*(숫자|numbers?)', seg, re.IGNORECASE)
                    symbols = re.search(r'(\d+)\s*(기호|symbols?)', seg, re.IGNORECASE)
                    if minlen: cdict["min_length"] = int(minlen.group(1))
                    if upper: cdict["upper"] = int(upper.group(1))
                    if lower: cdict["lower"] = int(lower.group(1))
                    if numbers: cdict["numbers"] = int(numbers.group(1))
                    if symbols: cdict["symbols"] = int(symbols.group(1))
                # paragraphs 조건
                if last_field["name"] == "paragraphs":
                    para_min = re.search(r'at least (\d+)', seg, re.IGNORECASE)
                    para_max = re.search(r'no more than (\d+)', seg, re.IGNORECASE)
                    if para_min: cdict["min"] = int(para_min.group(1))
                    if para_max: cdict["max"] = int(para_max.group(1))
                # number_between_1_100 조건
                if last_field["name"] == "number_between_1_100":
                    under = re.search(r'under (\d+)', seg, re.IGNORECASE)
                    over = re.search(r'over (\d+)', seg, re.IGNORECASE)
                    at_least = re.search(r'at least (\d+)', seg, re.IGNORECASE)
                    decimals = re.search(r'decimals?\s*(\d+)', seg, re.IGNORECASE)
                    if under: cdict["max"] = int(under.group(1)) - 1  # 배타적 처리
                    if over: cdict["min"] = int(over.group(1))
                    if at_least: cdict["min"] = int(at_least.group(1))
                    if decimals: cdict["decimals"] = int(decimals.group(1))
                # email only gmail 등
                if last_field["name"] == "email_address":
                    only_gmail = re.search(r'(gmail only|only gmail)', seg, re.IGNORECASE)
                    if only_gmail: cdict["only"] = "gmail"
                if cdict:
                    last_field["constraints"] = cdict
                found = True
        if not found and seg:
            suggestion = suggest_type(seg, supported_types)
            if suggestion:
                return {"error": f"지원하지 않는 타입입니다: {seg}", "suggestion": suggestion}
            else:
                return {"error": f"지원하지 않는 타입입니다: {seg}"}

    if not fields:
        return {"error": "No valid fields found in input."}

    return {
        "count": count,
        "fields": fields
    }

if __name__ == "__main__":
    test_cases = [
        "비밀번호 8자 이상, 대문자 1개, 숫자 1개 2개",
        "paragraphs at least 2, no more than 4",
        "phone, gmail only, number over 10",
        "Generate 10 users with Gmail emails under 40 years old",
        "Create 5 samples, full name, email address only gmail, age over 20",
        "10 users, phone number, at least 2 paragraphs, no more than 5 paragraphs",
        "Generate 3 avatars, company, city, country",
        "fullname 2개, email address, under 30",
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