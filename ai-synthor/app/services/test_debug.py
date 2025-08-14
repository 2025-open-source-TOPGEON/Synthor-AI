from app.services.detectors import FieldDetector
from app.services.mappings import KOR_TO_ENG_FIELD, EN_TO_TYPE_FIELD
from app.services.constraint_parser import Parser
from app.services.constraints.number_between import NumberBetweenExtractor
import re

def test_field_detection():
    detector = FieldDetector()
    
    test_cases = [
        "minimum payment is 10 EUR",
        "minimum payment 10 EUR",
        "payment is 10 EUR",
        "minimum 10 EUR",
        "EUR 10",
    ]
    
    for text in test_cases:
        result = detector.detect_first(text)
        print(f"'{text}' -> {result}")
        
        # 소문자 변환 후 매칭 확인
        low = text.lower()
        print(f"  lowercase: '{low}'")
        
        # 매칭되는 키워드 찾기
        for eng_key, eng_value in EN_TO_TYPE_FIELD.items():
            if eng_key.lower() in low:
                print(f"    matches: '{eng_key}' -> '{eng_value}'")
        print()

def test_full_parsing():
    parser = Parser()
    
    test_cases = [
        "minimum payment is 10 EUR",
        "missing age 20%",
    ]
    
    for text in test_cases:
        result = parser.parse_field_constraint(text)
        print(f"'{text}' -> {result}")
        print()

def test_number_between_extractor():
    extractor = NumberBetweenExtractor()
    
    test_cases = [
        "minimum payment is 10 EUR",
        "missing age 20%",
    ]
    
    for text in test_cases:
        try:
            result = extractor.extract(text)
            print(f"'{text}' -> {result}")
        except Exception as e:
            print(f"'{text}' -> ERROR: {e}")
        print()

def test_nullable_patterns():
    text = "missing age 20%"
    print(f"Testing: '{text}'")
    
    nullable_patterns = [
        r"(nullable|null|빈값|결측|없어도|옵션|optional|missing)\s+\w*\s*(\d{1,3})\s*%",
        r"(nullable|null|빈값|결측|없어도|옵션|optional|missing)\D{0,8}(\d{1,3})\s*%",
        r"(\d{1,3})\s*%\s*(nullable|null|빈값|결측|없어도|옵션|optional|missing)",
        r"(결측치|missing)\s*(\d{1,3})\s*%",
        r"(\d{1,3})\s*%\s*(결측치|missing)",
        r"(\d{1,3})\s*%\s*(허용|허용함)",
        r"(허용|허용함)\s*(\d{1,3})\s*%",
        r"missing\s+\w+\s+(\d{1,3})\s*%",
    ]
    
    for i, pattern in enumerate(nullable_patterns):
        m = re.search(pattern, text, re.I)
        if m:
            print(f"  Pattern {i}: '{pattern}' -> MATCH: {m.groups()}")
            print(f"    group(1): '{m.group(1)}', isdigit: {m.group(1).isdigit()}")
            if len(m.groups()) > 1:
                print(f"    group(2): '{m.group(2)}', isdigit: {m.group(2).isdigit()}")
        else:
            print(f"  Pattern {i}: '{pattern}' -> NO MATCH")

def test_nullable_logic():
    text = "missing age 20%"
    print(f"Testing nullable logic for: '{text}'")
    
    pattern = r"(nullable|null|빈값|결측|없어도|옵션|optional|missing)\s+\w*\s*(\d{1,3})\s*%"
    m = re.search(pattern, text, re.I)
    
    if m:
        print(f"  Match found: {m.groups()}")
        print(f"  group(1): '{m.group(1)}', isdigit: {m.group(1).isdigit()}")
        print(f"  group(2): '{m.group(2)}', isdigit: {m.group(2).isdigit()}")
        print(f"  len(groups): {len(m.groups())}")
        
        # 현재 로직 시뮬레이션
        if m.group(1).isdigit():
            pct = int(m.group(1))
            print(f"  Using group(1): {pct}")
        elif len(m.groups()) > 1 and m.group(2).isdigit():
            pct = int(m.group(2))
            print(f"  Using group(2): {pct}")
        else:
            print(f"  No valid number found")

def test_minimum_payment_patterns():
    text = "minimum payment is 10 EUR"
    print(f"Testing minimum payment patterns for: '{text}'")
    
    patterns = [
        r"minimum\s*(?:payment|order)\s*is\s*(\d+)",
        r"minimum\s*(?:payment|order)\s*is\s*(\d+)\s*(?:USD|EUR|€|달러|원)?",
    ]
    
    for i, pattern in enumerate(patterns):
        m = re.search(pattern, text, re.I)
        if m:
            print(f"  Pattern {i}: '{pattern}' -> MATCH: {m.groups()}")
            print(f"    group(1): '{m.group(1)}'")
        else:
            print(f"  Pattern {i}: '{pattern}' -> NO MATCH")

def test_all_patterns():
    text = "minimum payment is 10 EUR"
    print(f"Testing all patterns for: '{text}'")
    
    patterns = [
        r"(?:at\s*least|>=|greater\s*than\s*or\s*equal\s*to|이상)\s*(\d+)",
        r"(?:greater\s*than|>\s*)(\d+)|(\d+)\s*(?:초과)(?:\s|$)",
        r"(?:under|<=|less\s*than\s*or\s*equal\s*to|이하)\s*(\d+)",
        r"(?:less\s*than|<\s*)(\d+)|(\d+)\s*(?:미만)",
        r"minimum\s*(?:payment|order)\s*is\s*(\d+)",
        r"(\d+)\s*(만원|천원|원|달러|USD|EUR|€|￥|£)\s*이하",
        r"(\d+)\s*(만|천)?\s*원\s*이하",
        r"(\d+)\s*(만원|천원|원|달러|USD|EUR|€|￥|£)\s*이상",
        r"최소\s*결제금액\s*(\d+)",
        r"최소\s*(주문\s*)?수량\s*(\d+)",
        r"minimum\s*order\s*(\d+)",
        r"minimum\s*(?:payment|order)\s*is\s*(\d+)\s*(?:USD|EUR|€|달러|원)?",
    ]
    
    for i, pattern in enumerate(patterns):
        m = re.search(pattern, text, re.I)
        if m:
            print(f"  Pattern {i}: '{pattern}' -> MATCH: {m.groups()}")
            for j, group in enumerate(m.groups()):
                if group is not None:
                    print(f"    group({j+1}): '{group}'")
        else:
            print(f"  Pattern {i}: '{pattern}' -> NO MATCH")

def test_under_seventy():
    extractor = NumberBetweenExtractor()
    
    test_cases = [
        "70세 미만",
        "under 70",
        "age under 70",
        "나이 70세 미만",
        "70 미만",
        "under 70 years old",
    ]
    
    print("=== Testing 'under 70' patterns ===")
    for text in test_cases:
        try:
            result = extractor.extract(text)
            print(f"'{text}' -> {result}")
            if result.get("max") != 69:
                print(f"  ⚠️  WARNING: Expected max=69, got max={result.get('max')}")
            else:
                print(f"  ✅ Correct: max=69")
        except Exception as e:
            print(f"'{text}' -> ERROR: {e}")
        print()

if __name__ == "__main__":
    print("=== Field Detection Test ===")
    test_field_detection()
    print("\n=== Full Parsing Test ===")
    test_full_parsing()
    print("\n=== NumberBetweenExtractor Test ===")
    test_number_between_extractor()
    print("\n=== Under Seventy Test ===")
    test_under_seventy()
    print("\n=== Nullable Patterns Test ===")
    test_nullable_patterns()
    print("\n=== Nullable Logic Test ===")
    test_nullable_logic()
    print("\n=== Minimum Payment Patterns Test ===")
    test_minimum_payment_patterns()
    print("\n=== All Patterns Test ===")
    test_all_patterns()
