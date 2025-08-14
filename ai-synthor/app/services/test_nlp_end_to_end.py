from .constraint_parser import Parser

test_cases = [
    
    # 1. naver.com
    "naver.com으로요.",
    "네이버 메일로요.",
    "네이버 계정 이메일로요.",
    "네이버 메일 주소로요.",
    "네이버 이메일로요.",
    "네이버 도메인 이메일로요.",
    "네이버 계정 쓰고 계신 이메일로요.",
    "네이버 계정 메일로요.",
    "네이버 아이디 이메일로요.",
    "네이버 도메인 메일로요.",
    
    # 영어
    "To naver.com, please.",
    "With your Naver email, please.",
    "Using your Naver account email, please.",
    "To your Naver mail address, please.",
    "Using your Naver email address, please.",
    "With your Naver domain email, please.",
    "To the email you use for your Naver account, please.",
    "Using your Naver account mail, please.",
    "With your Naver ID email, please.",
    "Using your Naver domain mail, please.",
    
    # 한국어+영어
    "naver.com으로요, please.",
    "네이버 메일로요, please.",
    "네이버 계정 email로요.",
    "네이버 메일 address로요.",
    "네이버 email로요.",
    "네이버 domain email로요.",
    "네이버 계정 쓰고 계신 email로요.",
    "네이버 account mail로요.",
    "네이버 ID email로요.",
    "네이버 도메인 mail로요.",
    
    # 2. gmail.com
    "gmail.com으로요.",
    "지메일로요.",
    "지메일 계정 이메일로요.",
    "지메일 주소로요.",
    "지메일 이메일로요.",
    "지메일 도메인 이메일로요.",
    "지메일 계정 쓰고 계신 이메일로요.",
    
    # 영어
    "To gmail.com, please.",
    "With your Gmail email, please.",
    "Using your Gmail account email, please.",
    "To your Gmail mail address, please.",
    "Using your Gmail email address, please.",
    "With your Gmail domain email, please.",
    "To the email you use for your Gmail account, please.",
    
    # 한국어+영어
    "gmail.com으로요, please.",
    "지메일로요, please.",
    "지메일 account email로요.",
    "지메일 메일 address로요.",
    "지메일 email로요.",
    "지메일 domain email로요.",
    "지메일 계정 쓰고 계신 email로요.",
    
    # 3. yahoo.com
    "yahoo.com으로요.",
    "야후 메일로요.",
    "야후 계정 이메일로요.",
    "야후 메일 주소로요.",
    "야후 이메일로요.",
    "야후 도메인 이메일로요.",
    "야후 계정 쓰고 계신 이메일로요.",
    
    # 영어
    "To yahoo.com, please.",
    "With your Yahoo email, please.",
    "Using your Yahoo account email, please.",
    "To your Yahoo mail address, please.",
    "Using your Yahoo email address, please.",
    "With your Yahoo domain email, please.",
    "To the email you use for your Yahoo account, please.",
    
    # 한국어+영어
    "yahoo.com으로요, please.",
    "야후 메일로요, please.",
    "야후 account email로요.",
    "야후 메일 address로요.",
    "야후 email로요.",
    "야후 domain email로요.",
    "야후 계정 쓰고 계신 email로요.",
    
    # 4. hotmail.com
    "hotmail.com으로요.",
    "핫메일로요.",
    "핫메일 계정 이메일로요.",
    "핫메일 주소로요.",
    "핫메일 이메일로요.",
    "핫메일 도메인 이메일로요.",
    "핫메일 계정 쓰고 계신 이메일로요.",
    
    # 영어
    "To hotmail.com, please.",
    "With your Hotmail email, please.",
    "Using your Hotmail account email, please.",
    "To your Hotmail mail address, please.",
    "Using your Hotmail email address, please.",
    "With your Hotmail domain email, please.",
    "To the email you use for your Hotmail account, please.",
    
    # 한국어+영어
    "hotmail.com으로요, please.",
    "핫메일로요, please.",
    "핫메일 account email로요.",
    "핫메일 메일 address로요.",
    "핫메일 email로요.",
    "핫메일 domain email로요.",
    "핫메일 계정 쓰고 계신 email로요.",
    
    # 5. outlook.com
    "outlook.com으로요.",
    "아웃룩 메일로요.",
    "아웃룩 계정 이메일로요.",
    "아웃룩 주소로요.",
    "아웃룩 이메일로요.",
    "아웃룩 도메인 이메일로요.",
    "아웃룩 계정 쓰고 계신 이메일로요.",
    
    # 영어
    "To outlook.com, please.",
    "With your Outlook email, please.",
    "Using your Outlook account email, please.",
    "To your Outlook mail address, please.",
    "Using your Outlook email address, please.",
    "With your Outlook domain email, please.",
    "To the email you use for your Outlook account, please.",
    
    # 한국어+영어
    "outlook.com으로요, please.",
    "아웃룩 메일로요, please.",
    "아웃룩 account email로요.",
    "아웃룩 메일 address로요.",
    "아웃룩 email로요.",
    "아웃룩 domain email로요.",
    "아웃룩 계정 쓰고 계신 email로요.",
    
    # 6. 추가 도메인들
    # daum.net
    "daum.net으로요.",
    "다음 메일로요.",
    "다음 계정 이메일로요.",
    "To daum.net, please.",
    "With your Daum email, please.",
    "To the email you use for your Daum account, please.",
    
    # nate.com
    "nate.com으로요.",
    "네이트 메일로요.",
    "네이트 계정 이메일로요.",
    "To nate.com, please.",
    "With your Nate email, please.",
    "To the email you use for your Nate account, please.",
    
    # hanmail.net
    "hanmail.net으로요.",
    "한메일 메일로요.",
    "한메일 계정 이메일로요.",
    "To hanmail.net, please.",
    "With your Hanmail email, please.",
    "To the email you use for your Hanmail account, please.",
    
    # icloud.com
    "icloud.com으로요.",
    "아이클라우드 메일로요.",
    "아이클라우드 계정 이메일로요.",
    "To icloud.com, please.",
    "With your iCloud email, please.",
    "To the email you use for your iCloud account, please.",
    
    # protonmail.com
    "protonmail.com으로요.",
    "프로톤메일 메일로요.",
    "프로톤메일 계정 이메일로요.",
    "To protonmail.com, please.",
    "With your ProtonMail email, please.",
    "To the email you use for your ProtonMail account, please.",
    
    # 7. 학교 메일 도메인들
    # 세종대학교
    "sejong.ac.kr으로요.",
    "세종대 메일로요.",
    "세종대 이메일로요.",
    "세종대 계정 이메일로요.",
    "세종대학교 메일로요.",
    "세종대학교 이메일로요.",
    
    # 서울대학교
    "snu.ac.kr으로요.",
    "서울대 메일로요.",
    "서울대 이메일로요.",
    "서울대 계정 이메일로요.",
    "서울대학교 메일로요.",
    "서울대학교 이메일로요.",
    
    # 고려대학교
    "korea.ac.kr으로요.",
    "고려대 메일로요.",
    "고려대 이메일로요.",
    "고려대 계정 이메일로요.",
    "고려대학교 메일로요.",
    "고려대학교 이메일로요.",
    
    # 연세대학교
    "yonsei.ac.kr으로요.",
    "연세대 메일로요.",
    "연세대 이메일로요.",
    "연세대 계정 이메일로요.",
    "연세대학교 메일로요.",
    "연세대학교 이메일로요.",
    
    # 카이스트
    "kaist.ac.kr으로요.",
    "카이스트 메일로요.",
    "카이스트 이메일로요.",
    "카이스트 계정 이메일로요.",
    "한국과학기술원 메일로요.",
    "한국과학기술원 이메일로요.",
    
    # 포항공과대학교
    "postech.ac.kr으로요.",
    "포항공대 메일로요.",
    "포항공대 이메일로요.",
    "포항공대 계정 이메일로요.",
    "포항공과대학교 메일로요.",
    "포항공과대학교 이메일로요.",
    
    # 경희대학교
    "khu.ac.kr으로요.",
    "경희대 메일로요.",
    "경희대 이메일로요.",
    "경희대 계정 이메일로요.",
    "경희대학교 메일로요.",
    "경희대학교 이메일로요.",
    
    # 한양대학교
    "hanyang.ac.kr으로요.",
    "한양대 메일로요.",
    "한양대 이메일로요.",
    "한양대 계정 이메일로요.",
    "한양대학교 메일로요.",
    "한양대학교 이메일로요.",
    
    # 이화여자대학교
    "ewha.ac.kr으로요.",
    "이화여대 메일로요.",
    "이화여대 이메일로요.",
    "이화여대 계정 이메일로요.",
    "이화여자대학교 메일로요.",
    "이화여자대학교 이메일로요.",
    
    # 인하대학교
    "inha.ac.kr으로요.",
    "인하대 메일로요.",
    "인하대 이메일로요.",
    "인하대 계정 이메일로요.",
    "인하대학교 메일로요.",
    "인하대학교 이메일로요.",
    
    # 부산대학교
    "pusan.ac.kr으로요.",
    "부산대 메일로요.",
    "부산대 이메일로요.",
    "부산대 계정 이메일로요.",
    "부산대학교 메일로요.",
    "부산대학교 이메일로요.",
    
    # 경북대학교
    "knu.ac.kr으로요.",
    "경북대 메일로요.",
    "경북대 이메일로요.",
    "경북대 계정 이메일로요.",
    "경북대학교 메일로요.",
    "경북대학교 이메일로요.",
    
    # 중앙대학교
    "cau.ac.kr으로요.",
    "중앙대 메일로요.",
    "중앙대 이메일로요.",
    "중앙대 계정 이메일로요.",
    "중앙대학교 메일로요.",
    "중앙대학교 이메일로요.",
    
    # 서강대학교
    "sogang.ac.kr으로요.",
    "서강대 메일로요.",
    "서강대 이메일로요.",
    "서강대 계정 이메일로요.",
    "서강대학교 메일로요.",
    "서강대학교 이메일로요.",
    
    # 국민대학교
    "kookmin.ac.kr으로요.",
    "국민대 메일로요.",
    "국민대 이메일로요.",
    "국민대 계정 이메일로요.",
    "국민대학교 메일로요.",
    "국민대학교 이메일로요.",
    
    # 아주대학교
    "ajou.ac.kr으로요.",
    "아주대 메일로요.",
    "아주대 이메일로요.",
    "아주대 계정 이메일로요.",
    "아주대학교 메일로요.",
    "아주대학교 이메일로요.",
    
    # 조선대학교
    "chosun.ac.kr으로요.",
    "조선대 메일로요.",
    "조선대 이메일로요.",
    "조선대 계정 이메일로요.",
    "조선대학교 메일로요.",
    "조선대학교 이메일로요.",
    
    # 계명대학교
    "kmu.ac.kr으로요.",
    "계명대 메일로요.",
    "계명대 이메일로요.",
    "계명대 계정 이메일로요.",
    "계명대학교 메일로요.",
    "계명대학교 이메일로요.",
    
    # 단국대학교
    "dankook.ac.kr으로요.",
    "단국대 메일로요.",
    "단국대 이메일로요.",
    "단국대 계정 이메일로요.",
    "단국대학교 메일로요.",
    "단국대학교 이메일로요.",
    
    # 8. @도메인형 패턴 테스트 (임의의 도메인 지원)
    # 한국어 패턴
    "@am.dk형으로",
    "@am.dk형로",
    "@am.dk형으로요",
    "@am.dk형로요",
    "@am.dk형으로는",
    "@am.dk형로는",
    "@am.dk형으로만",
    "@am.dk형로만",
    "@am.dk형으로부터",
    "@am.dk형로부터",
    "@am.dk형으로 해주세요",
    "@am.dk형로 해주세요",
    "@am.dk형으로 부탁드립니다",
    "@am.dk형로 부탁드립니다",
    "@am.dk형으로 해주시면 됩니다",
    "@am.dk형로 해주시면 됩니다",
    "@am.dk형으로 작성해주세요",
    "@am.dk형로 작성해주세요",
    "@am.dk형 메일로",
    "@am.dk형 메일로요",
    "@am.dk형 메일 주소로",
    "@am.dk형 이메일로",
    "@am.dk형 이메일로요",
    "@am.dk형 계정으로",
    "@am.dk형 계정 이메일로",
    
    # 영어 패턴
    "Make it in @am.dk email format.",
    "Please use an email with @am.dk.",
    "I need it as an @am.dk address.",
    "With an @am.dk email, please.",
    "Using @am.dk domain email, please.",
    "Please make it an @am.dk account email.",
    "Set it to @am.dk format.",
    "Use @am.dk only.",
    "Please send it from @am.dk.",
    "Please write it with @am.dk.",
    
    # 한국어 + 영어 혼합 패턴
    "@am.dk형으로, please.",
    "@am.dk형로요, please.",
    "Please, @am.dk형 메일로요.",
    "@am.dk형 account email로요.",
    "@am.dk형 메일 address로요.",
    "@am.dk형 email로 부탁드려요.",
    "@am.dk형 domain email로요.",
    "Please send it from @am.dk형.",
    "@am.dk형 only, 부탁드립니다.",
    "Set it to @am.dk형 format으로요.",
    
    # 다른 도메인 테스트
    "@example.com형으로요.",
    "@test.org형 메일로요.",
    "@company.co.kr형 이메일로요.",
    "@university.edu형 계정으로요.",
    "@startup.io형으로 해주세요.",
    
         # 임의의 도메인 테스트 (실제 도메인 형식이 아닌 경우)
     "@3920형으로요.",
     "@abc123형 메일로요.",
     "@test형 이메일로요.",
     "@mycompany형 계정으로요.",
     "@random형으로 해주세요.",
     "@12345형으로요.",
     "@hello형 메일로요.",
     "@world형 이메일로요.",
     
     # 추가 임의의 도메인 테스트
     "@company형으로요.",
     "@school형 메일로요.",
     "@work형 이메일로요.",
     "@home형 계정으로요.",
     "@office형으로 해주세요.",
     "@team형으로요.",
     "@group형 메일로요.",
     "@project형 이메일로요.",
     "@service형으로요.",
     "@app형 메일로요.",
     "@site형 이메일로요.",
     "@web형 계정으로요.",
     "@user형으로 하고 결측치 30.",
     "@admin형으로요.",
     "@support형 메일로요.",
     "@info로 null 10&",
]

parser = Parser()

for text in test_cases:
    print(f"입력: {text}")
    result = parser.parse_field_constraint(text)
    print(result)
    print("-" * 40)