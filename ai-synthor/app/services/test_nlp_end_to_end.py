from .constraint_parser import Parser

test_cases = [
    # 나이 관련 테스트 케이스들
    "나이는 20 이상 60 이하, 소수점 1자리, nullable 10%",
    "나이 120 이하",
    "age between 25 and 65",
    "연령 30 이상 50 이하",
    "나이 20~30세",
    "연령 25-35세",
    "나이는 18부터 65까지",
    "나이 1세 이상 100세 이하",
    "연령대 30~50",
    "15세부터 20세까지",
    "age between 20 and 30",
    "age from 18 to 65",
    "age 25-35",
    "age at least 21 and at most 30",
    "age greater than or equal to 18 and less than or equal to 65",
    "나이 between 20 and 30",
    "연령 from 18 to 65",
    "나이 21세 이상 and 30세 이하",
    "age 18세 이상 65세 이하",
   
    # 금액/가격 테스트
    "가격 5천원 이상",
    "금액 3만 원 이하",
    "최소 결제금액 1,000원",
    "price at least 50 USD",
    "amount less than 100 dollars",
    "minimum payment is 10 EUR",
    "가격 at least 100 USD",
    "price 3만원 이하",
    
    # 수량/개수 테스트
    "수량 10개 이하",
    "최소 주문 수량 5개",
    "참가자 20명 이상",
    "quantity up to 10",
    "minimum order 5 items",
    "participants at least 20",
    "수량 at least 5",
    "participants 10명 이하",
    
    # 길이/거리 테스트
    "길이 30cm 이상",
    "거리 5km 이하",
    "폭 2m 초과",
    "length greater than 30 cm",
    "distance less than 5 km",
    "width over 2 meters",
    "길이 30cm at least",
    "distance 5km 이하",
    
    # 무게/질량 테스트
    "무게 10kg 미만",
    "질량 500g 이상",
    "weight less than 10 kg",
    "mass at least 500 grams",
    "무게 less than 10 kg",
    "mass 500g 이상",
    
    # 온도 테스트
    "온도 20도 이상",
    "섭씨 30도 이하",
    "temperature at least 20 ℃",
    "celsius less than 30",
    "온도 at most 25 ℃",
    "temperature 30도 이하",
    
    # 속도 테스트
    "속도 60km/h 초과",
    "주행 속도 100km/h 이하",
    "speed greater than 60 km/h",
    "driving speed less than 100 km/h",
    "속도 greater than 60 km/h",
    "speed 100km/h 이하",
    
    # 시간/기간 테스트
    "10분 이상",
    "2시간 이하",
    "기간 3일~5일",
    "at least 10 minutes",
    "duration less than 2 hours",
    "between 3 and 5 days",
    "기간 at least 3 days",
    "between 2시간 and 5시간",
    
    # 퍼센트/비율 테스트
    "성공률 80% 이상",
    "확률 50% 이하",
    "success rate at least 80%",
    "probability less than 50%",
    "성공률 at most 90%",
    "probability 70% 이상",
    
    # 등급/점수 테스트
    "점수 80점 이상",
    "등급 1~3",
    "score at least 80",
    "grade between 1 and 3",
    "점수 at least 80",
    "grade 1~3등급",
    
    # 최소 나이 테스트
    "나이 18세 이상",
    "연령 21세 이상",
    "나이는 최소 20세",
    "나이 19세 초과",
    "연령 greater than 17세",
    "age at least 18",
    "age greater than or equal to 21",
    "age over 18",
    "minimum age is 20",
    "age greater than 17",
    "나이 at least 18",
    "연령 greater than or equal to 21",
    "age 20세 이상",
    "최소 age 18",
    
    # 최대 나이 테스트
    "나이 65세 이하",
    "연령 30세 이하",
    "나이는 최대 50세",
    "나이 70세 미만",
    "연령 less than 40세",
    "age at most 65",
    "age less than or equal to 30",
    "maximum age is 50",
    "age under 70",
    "age less than 40",
    "나이 at most 65",
    "연령 less than or equal to 30",
    "age 최대 50세",
    "age 40세 이하",
    
    # 정확한 나이 테스트
    "나이는 정확히 30세",
    "연령 25세로 고정",
    "나이 40세 동일",
    "나이 값은 18세",
    "age exactly 30",
    "exact age is 25",
    "age fixed at 40",
    "age equals 18",
    "나이는 exactly 30",
    "연령 fixed at 25",
    "age는 정확히 40세",
    
    # 소수점 자리 테스트
    "나이 소수점 1자리",
    "나이 소수 2자리",
    "나이는 정수만",
    "age up to 1 decimal",
    "age decimals 2",
    "integer age only",
    "나이 up to 1 decimal",
    "age 소수점 2자리",
    "integer 나이 only",
    
    # Nullable 비율 테스트
    "나이 빈값 10% 허용",
    "연령 결측치 5%",
    "나이는 NULL 20%",
    "age nullable 10%",
    "null age 5%",
    "missing age 20%",
    "나이 nullable 10%",
    "age 결측치 5%",
    "연령 NULL 15%",
]

parser = Parser()

for text in test_cases:
    print(f"입력: {text}")
    result = parser.parse_field_constraint(text)
    print(result)
    print("-" * 40)