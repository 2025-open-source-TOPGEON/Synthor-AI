from .constraint_parser import Parser

test_cases = [
      # Age/Number constraints        75
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
        "나이 소수점 1자리",
        "나이 소수 2자리",
        "나이는 정수만",
        "age decimals 2",
        "integer age only",
        "age 소수점 2자리",
        "integer 나이 only",
        "나이 빈값 10% 허용",
        "연령 결측치 5%",
        "나이는 NULL 20%",
        "age nullable 10%",
        "null age 5%",
        "missing age 20%",
        "나이 nullable 10%",
        "age 결측치 5%",
        "연령 NULL 15%",
        "number_between_1_100 min 3 max 3 decimals 3",
        
               
               
      
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