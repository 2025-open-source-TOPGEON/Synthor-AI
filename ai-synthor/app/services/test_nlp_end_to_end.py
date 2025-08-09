from korean_processor import parse_korean_text_to_json
from english_processor import parse_english_text_to_json

def detect_language(text):
    # 간단한 예시: 한글 포함 여부로 감지
    if any('\uac00' <= c <= '\ud7a3' for c in text):
        return "ko"
    return "en"

test_cases = [
    # 한글
    "전체 이름 5개",
    "서울만 state로 3개",
    "비밀번호 8자 이상, 대문자 1개, 숫자 1개인 데이터 2개",
    # 영어
    "Generate 10 users with Gmail emails under 40 years old",
    "password minimum length 8 upper 1 lower 1 numbers 1 symbols 1",
    "avatar size 50x50 format png",
    # 혼합
    "10 users, 이메일은 gmail만, 나이는 under 40",
    "fullname 2개, email address, under 30",
    # 오타/붙여쓰기/자유문장
    "전체이름5개",
    "이름은 영어로, 주소는 한국어로 3개",
    "Create 5 samples, full name, email address only gmail, age over 20",
    "Generate 3 avatars, company, city, country",
    "paragraphs at least 2, no more than 4",
    "phone, gmail only, number over 10",
    "state: California, country: United States",
    "datetime from 2024-01-01 to 2024-12-31 format yyyy-mm-dd",
    "time from 9am to 6pm 24 hour",
    "url protocol host path query",
    "credit card number Visa",
    "credit card type Mastercard",
    "latitude, longitude, product price, swift bic, iban"
]

for text in test_cases:
    lang = detect_language(text)
    if lang == "ko":
        result = parse_korean_text_to_json(text)
    else:
        result = parse_english_text_to_json(text)
    print(f"입력: {text}")
    print(result)
    print("-" * 40)