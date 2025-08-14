from .constraint_parser import Parser

test_cases = [

    #이름 테스트
    "엔샵이라는 성을 가진 사람",
    "성이 제갈인 사람",
    "성이 다혜인 사람",
    
    # 한국어 성씨 패턴 테스트
    # 1. 한국어 전용 패턴
    "성이 김인 사람",
    "성씨가 이인 사람",
    "성이 박으로 시작하는 사람",
    "성이 최로 시작하는 사람",
    "김 성을 가진 사람",
    "이 성씨를 가진 사람",
    "정 성을 쓰는 사람",
    "강 성씨를 쓰는 사람",
    "성이 윤인 사람",
    "성이 장임",
    "성씨가 임임",
    "성이 황으로 되어 있는 사람 nullable 10%",
    "성씨가 조로 되어 있는 사람",
    "성이 유라는 사람",
    "성씨가 한이라는 사람",
    "성이 오이신 분",
    "성씨가 서이신 분  NULL 5%",
    "성이 신이신 사람",
    "성씨가 권이신 사람",
    "성이 안으로 끝나는 사람 null 5퍼센트",
    "성이 프로그래밍인 사람"
    
    # 3. 한국어 + 영어 혼합 패턴
    "last name: 윤",
    "family name: 장",
    "full name starts with 유 missing 20%",
    "full name begins with 한",


    "장씨만 있고 nullable이 30이면 좋겠어",
    "다혜씨면 좋겠어",
    "성이 서인 사람이면 좋겠는 걸",
    "성이 서, 결측 20",
    "성이 다혜라는 사람인데 null 값이 10임",
]

parser = Parser()

for text in test_cases:
    print(f"입력: {text}")
    result = parser.parse_field_constraint(text)
    print(result)
    print("-" * 40)