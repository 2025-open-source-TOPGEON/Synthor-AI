from typing import Dict
from .detectors import FieldDetector
from .nullables import NullablePercentExtractor
from .qualifiers import GlobalQualifiersExtractor
from .constants_types import CONSTRAINT_TYPES
from .constraints.registry import ConstraintRegistry
from .constraints.default import DefaultExtractor

# 개별 Extractor 등록
from .constraints.password import PasswordExtractor
from .constraints.phone import PhoneExtractor
from .constraints.avatar import AvatarExtractor
from .constraints.state import StateExtractor
from .constraints.country import CountryExtractor
from .constraints.datetime import DatetimeExtractor
from .constraints.time import TimeExtractor
from .constraints.url import UrlExtractor 
from .constraints.credit_card_number import CreditCardNumberExtractor
from .constraints.credit_card_type import CreditCardTypeExtractor
from .constraints.paragraphs import ParagraphsExtractor
from .constraints.number_between import NumberBetweenExtractor
from .constraints.korean_full_name import KoreanFullNameExtractor, KoreanLastNameExtractor
from .constraints.email import EmailExtractor

class Parser:
    def __init__(self):
        self.detector = FieldDetector()
        self.nullables = NullablePercentExtractor()
        self.qualifiers = GlobalQualifiersExtractor()
        self.registry = self._build_registry()
        self.default_extractor = DefaultExtractor()

    def _build_registry(self) -> ConstraintRegistry:
        reg = ConstraintRegistry()
        for ext in [
            PasswordExtractor(), PhoneExtractor(), AvatarExtractor(),
            StateExtractor(), CountryExtractor(), DatetimeExtractor(),
            TimeExtractor(), UrlExtractor(), CreditCardNumberExtractor(),
            CreditCardTypeExtractor(), ParagraphsExtractor(), 
            KoreanFullNameExtractor(), KoreanLastNameExtractor(), EmailExtractor(),
            NumberBetweenExtractor()  # 숫자범위는 마지막에 배치
        ]:
            reg.register(ext)
        return reg

    def parse_field_constraint(self, text: str) -> Dict:
        # 날짜/포맷 지시어가 있으면 datetime 타입으로 고정 (우선순위: DateFormat > Nullable% > NumberBetween)
        import re
        
        # 문단/단락 키워드가 있으면 paragraphs로 우선 처리
        paragraph_keywords = [
            r'\b(?:문단|단락|paragraphs?|sections?|blocks?\s*of\s*text)\b',
            r'\b(?:text\s*paragraphs?|body\s*paragraphs?|content\s*paragraphs?)\b',
            r'\b(?:written\s*paragraphs?|textual\s*paragraphs?|paragraph\s*units?|paragraph\s*blocks?)\b',
            r'\b(?:paragraph\s*count|number\s*of\s*paragraphs?|paragraph\s*structure)\b',
            r'\b(?:본문|글의\s*문단|본문\s*단락|글\s*단락|글의\s*문단\s*수|본문\s*구성\s*단락)\b',
            r'\b(?:단락\s*수|문단\s*수|글의\s*각\s*단락|본문의\s*각\s*문단|글의\s*내용\s*단락)\b',
            r'\b(?:문단\s*개수|문단\s*수는|문단\s*개수를|문단\s*수를|문단\s*개수는)\b',
            r'\b(?:문단으로\s*구성|문단으로\s*작성|문단을\s*작성|문단으로\s*맞춰|문단으로\s*유지|문단으로\s*제한)\b',
            r'\b(?:문단은\s*총|문단\s*수는\s*총|문단\s*개수는\s*총|문단은\s*정확히|문단\s*수는\s*정확히|문단\s*개수는\s*정확히)\b',
            r'\b(?:문단을\s*총|문단을\s*정확히|문단은\s*최소|문단은\s*최대|문단\s*수는\s*최소|문단\s*수는\s*최대)\b',
            r'\b(?:문단\s*개수는\s*최소|문단\s*개수는\s*최대|본문은\s*최소|본문은\s*최대)\b',
            # 더 구체적인 패턴들 추가
            r'\d+\s*~?\s*\d+\s*개의?\s*문단',
            r'\d+\s*-\s*\d+\s*개의?\s*문단',
            r'\d+\s*에서\s*\d+\s*개의?\s*문단',
            r'between\s*\d+\s*and\s*\d+\s*paragraphs?',
            r'\d+\s*to\s*\d+\s*paragraphs?',
            r'from\s*\d+\s*to\s*\d+\s*paragraphs?',
            r'\d+\s*–\s*\d+\s*paragraphs?',
            r'최소\s*\d+\s*최대\s*\d+\s*개의?\s*문단',
            r'at\s*least\s*\d+\s*no\s*more\s*than\s*\d+\s*paragraphs?',
            r'문단.*\d+\s*개.*\d+\s*개',
            r'paragraphs?.*\d+.*\d+',
            r'본문.*\d+\s*개.*\d+\s*개',
            r'본문.*\d+\s*이상.*\d+\s*이하',
            # 더 구체적인 패턴들
            r'최소\s*\d+\s*최대\s*\d+\s*개의?\s*문단',
            r'at\s*least\s*\d+\s*no\s*more\s*than\s*\d+\s*paragraphs?',
            r'문단.*최소.*최대',
            r'paragraphs?.*minimum.*maximum',
            r'문단.*at\s*least.*no\s*more\s*than',
            r'본문.*\d+\s*개.*\d+\s*개.*문단',
            r'본문.*\d+\s*이상.*\d+\s*이하.*문단',
            r'문단.*\d+\s*이상.*\d+\s*이하',
            r'paragraphs?.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*–\s*\d+',
            r'paragraphs?.*\d+\s*–\s*\d+',
            # 더 강력한 패턴들
            r'최소\s*\d+\s*최대\s*\d+\s*개의?\s*문단',
            r'at\s*least\s*\d+\s*no\s*more\s*than\s*\d+\s*paragraphs?',
            r'문단.*최소.*최대',
            r'paragraphs?.*minimum.*maximum',
            r'문단.*at\s*least.*no\s*more\s*than',
            r'본문.*\d+\s*개.*\d+\s*개.*문단',
            r'본문.*\d+\s*이상.*\d+\s*이하.*문단',
            r'문단.*\d+\s*이상.*\d+\s*이하',
            r'paragraphs?.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*–\s*\d+',
            r'paragraphs?.*\d+\s*–\s*\d+',
            # 추가 강력한 패턴들
            r'문단.*\d+\s*개.*\d+\s*개',
            r'paragraphs?.*\d+.*\d+',
            r'본문.*\d+\s*개.*\d+\s*개',
            r'본문.*\d+\s*이상.*\d+\s*이하',
            r'문단.*\d+\s*개.*\d+\s*개',
            r'paragraphs?.*\d+.*\d+',
            r'본문.*\d+\s*개.*\d+\s*개',
            r'본문.*\d+\s*이상.*\d+\s*이하',
            # 더 강력한 패턴들 추가
            r'최소\s*\d+\s*최대\s*\d+\s*개의?\s*문단',
            r'at\s*least\s*\d+\s*no\s*more\s*than\s*\d+\s*paragraphs?',
            r'문단.*최소.*최대',
            r'paragraphs?.*minimum.*maximum',
            r'문단.*at\s*least.*no\s*more\s*than',
            r'본문.*\d+\s*개.*\d+\s*개.*문단',
            r'본문.*\d+\s*이상.*\d+\s*이하.*문단',
            r'문단.*\d+\s*이상.*\d+\s*이하',
            r'paragraphs?.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*–\s*\d+',
            r'paragraphs?.*\d+\s*–\s*\d+',
            # 영어 숫자 표현 포함
            r'between\s*(?:three|four|five|six|seven|eight|nine|ten)\s*and\s*(?:three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
            r'at\s*least\s*(?:three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
            r'no\s*more\s*than\s*(?:three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
            r'exactly\s*(?:three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
            r'precisely\s*(?:three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
            r'minimum\s*of\s*(?:three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
            r'maximum\s*of\s*(?:three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
            # 더 구체적인 패턴들
            r'문단.*\d+\s*개.*\d+\s*개.*문단',
            r'paragraphs?.*\d+.*\d+.*paragraphs?',
            r'본문.*\d+\s*개.*\d+\s*개.*문단',
            r'본문.*\d+\s*이상.*\d+\s*이하.*문단',
            r'문단.*\d+\s*이상.*\d+\s*이하',
            r'paragraphs?.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*–\s*\d+',
            r'paragraphs?.*\d+\s*–\s*\d+',
            # 최소/최대 패턴들
            r'최소\s*\d+\s*최대\s*\d+\s*개의?\s*문단',
            r'at\s*least\s*\d+\s*no\s*more\s*than\s*\d+\s*paragraphs?',
            r'문단.*최소.*최대',
            r'paragraphs?.*minimum.*maximum',
            r'문단.*at\s*least.*no\s*more\s*than',
            r'본문.*\d+\s*개.*\d+\s*개.*문단',
            r'본문.*\d+\s*이상.*\d+\s*이하.*문단',
            r'문단.*\d+\s*이상.*\d+\s*이하',
            r'paragraphs?.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*to\s*\d+',
            r'문단.*\d+\s*–\s*\d+',
            r'paragraphs?.*\d+\s*–\s*\d+',
            # 추가 패턴들 - 더 포괄적인 문단 감지
            r'문단\s*개수',
            r'문단\s*수',
            r'문단\s*개',
            r'문단\s*개로',
            r'문단\s*개를',
            r'문단\s*개가',
            r'문단\s*개는',
            r'문단\s*개에',
            r'문단\s*개와',
            r'문단\s*개와\s*함께',
            r'문단\s*개\s*포함',
            r'문단\s*개\s*작성',
            r'문단\s*개\s*구성',
            r'문단\s*개\s*제한',
            r'문단\s*개\s*범위',
            r'문단\s*개\s*사이',
            r'문단\s*개\s*이상',
            r'문단\s*개\s*이하',
            r'문단\s*개\s*정확히',
            r'문단\s*개\s*정확한',
            r'문단\s*개\s*고정',
            r'문단\s*개\s*동일',
            r'문단\s*개\s*같은',
            r'문단\s*개\s*최소',
            r'문단\s*개\s*최대',
            r'문단\s*개\s*at\s*least',
            r'문단\s*개\s*no\s*more\s*than',
            r'문단\s*개\s*between',
            r'문단\s*개\s*from',
            r'문단\s*개\s*to',
            r'문단\s*개\s*and',
            r'문단\s*개\s*or',
            r'문단\s*개\s*또는',
            r'문단\s*개\s*그리고',
            r'문단\s*개\s*포함해주세요',
            r'문단\s*개\s*포함해\s*주세요',
            r'문단\s*개\s*작성해주세요',
            r'문단\s*개\s*작성해\s*주세요',
            r'문단\s*개\s*구성해주세요',
            r'문단\s*개\s*구성해\s*주세요',
            r'문단\s*개\s*제한됩니다',
            r'문단\s*개\s*제한',
            r'문단\s*개\s*범위',
            r'문단\s*개\s*사이',
            r'문단\s*개\s*이상',
            r'문단\s*개\s*이하',
            r'문단\s*개\s*정확히',
            r'문단\s*개\s*정확한',
            r'문단\s*개\s*고정',
            r'문단\s*개\s*동일',
            r'문단\s*개\s*같은',
            r'문단\s*개\s*최소',
            r'문단\s*개\s*최대',
            r'문단\s*개\s*at\s*least',
            r'문단\s*개\s*no\s*more\s*than',
            r'문단\s*개\s*between',
            r'문단\s*개\s*from',
            r'문단\s*개\s*to',
            r'문단\s*개\s*and',
            r'문단\s*개\s*or',
            r'문단\s*개\s*또는',
            r'문단\s*개\s*그리고',
            # 더 간단하고 포괄적인 패턴들
            r'문단',
            r'paragraphs?',
            r'단락',
            r'sections?',
            r'blocks?\s*of\s*text',
            r'text\s*paragraphs?',
            r'body\s*paragraphs?',
            r'content\s*paragraphs?',
            r'written\s*paragraphs?',
            r'textual\s*paragraphs?',
            r'paragraph\s*units?',
            r'paragraph\s*blocks?',
            r'paragraph\s*count',
            r'number\s*of\s*paragraphs?',
            r'paragraph\s*structure',
            r'본문',
            r'글의\s*문단',
            r'본문\s*단락',
            r'글\s*단락',
            r'글의\s*문단\s*수',
            r'본문\s*구성\s*단락',
            r'단락\s*수',
            r'문단\s*수',
            r'글의\s*각\s*단락',
            r'본문의\s*각\s*문단',
            r'글의\s*내용\s*단락',
            r'문단\s*개수',
            r'문단\s*수는',
            r'문단\s*개수를',
            r'문단\s*수를',
            r'문단\s*개수는',
            r'문단으로\s*구성',
            r'문단으로\s*작성',
            r'문단을\s*작성',
            r'문단으로\s*맞춰',
            r'문단으로\s*유지',
            r'문단으로\s*제한',
            r'문단은\s*총',
            r'문단\s*수는\s*총',
            r'문단\s*개수는\s*총',
            r'문단은\s*정확히',
            r'문단\s*수는\s*정확히',
            r'문단\s*개수는\s*정확히',
            r'문단을\s*총',
            r'문단을\s*정확히',
            r'문단은\s*최소',
            r'문단은\s*최대',
            r'문단\s*수는\s*최소',
            r'문단\s*수는\s*최대',
            r'문단\s*개수는\s*최소',
            r'문단\s*개수는\s*최대',
            r'본문은\s*최소',
            r'본문은\s*최대'
        ]
        is_paragraph_text = any(re.search(pattern, text, re.I) for pattern in paragraph_keywords)
        
        # 나이/연령 키워드가 있으면 number_between_1_100으로 우선 처리
        age_keywords = [r'\b(?:나이|연령|age)\b']
        is_age_text = any(re.search(pattern, text, re.I) for pattern in age_keywords)
        
        # integer 키워드가 나이/연령과 함께 있으면 숫자로 인식
        integer_age_pattern = r'\b(?:integer|정수)\s+(?:나이|연령|age)\b'
        is_integer_age = bool(re.search(integer_age_pattern, text, re.I))
        
        datetime_indicators = [
            r'\b(?:date\s*format|m/d/yyyy|mm/dd/yyyy|d/m/yyyy|yyyy-mm-dd|yyyy-mm)\b',
            r'\b(?:e\.?g\.?|example|sample|예시는|샘플|예|샘)[:\s]',
            r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',
            r'\d{1,2}[-/.]\d{1,2}[-/.]\d{4}',
            r'\d{2}[-/.]\d{1,2}[-/.]\d{1,2}',
            # 나이/연령 컨텍스트가 아닐 때만 from/between을 날짜로 인식 (to는 이메일에서도 사용되므로 제외)
            r'(?<!나이|연령)\b(?:from|through|between|range|기간|조회기간|시작일|종료일|start|end)\b(?!\s*\d+)',
            r'\b(?:fmt)\b',  # use 제거 (이메일에서도 사용됨)
            r'\b(?:d/m/yyyy|m/d/yyyy|mm/dd/yyyy|yyyy-mm-dd|yyyy-mm)\b',
            r'\b(?:같은|설정)\b',  # only 제거 (이메일에서도 사용됨)
        ]
        
        is_datetime_text = any(re.search(pattern, text, re.I) for pattern in datetime_indicators)
        
        # 이메일 도메인/패턴이 보이면 datetime 우선순위를 끈다
        email_first_patterns = [
            r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',    # @domain.com
            r'@[a-zA-Z0-9.-]+형',                 # @domain형
            r'@[a-zA-Z0-9.-]+(?:로|으로)\b',     # @domain로, @domain으로
            r'\b(?:naver\.com|gmail\.com|yahoo\.com|hotmail\.com|outlook\.com|daum\.net|nate\.com|hanmail\.net|icloud\.com|protonmail\.com)\b',
        ]
        if any(re.search(p, text, re.I) for p in email_first_patterns):
            is_datetime_text = False
        
        # 추가 날짜 감지: 날짜 패턴이 있으면 무조건 datetime
        date_patterns = [
            r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',  # 2023-07-09, 2023/07/09
            r'\d{1,2}[-/.]\d{1,2}[-/.]\d{4}',  # 25/12/2023, 12/25/2023
            r'\d{2}[-/.]\d{1,2}[-/.]\d{1,2}',  # 23/12/25
            r'\d{4}[-/.]\d{1,2}',  # 2023-01, 2023.1
        ]
        has_date_pattern = any(re.search(pattern, text) for pattern in date_patterns)
        
        # 날짜 패턴이 있으면 무조건 datetime으로 설정
        if has_date_pattern:
            is_datetime_text = True
        
        # 더 강력한 날짜 감지: 숫자-숫자-숫자 패턴이 있으면 무조건 datetime
        # 단, 나이/연령 키워드가 있으면 제외
        if not is_age_text and not is_integer_age and re.search(r'\d+[-/.]\d+[-/.]\d+', text):
            is_datetime_text = True
        
        # 문단/단락 관련 텍스트면 paragraphs 타입으로 강제 (최우선)
        if is_paragraph_text:
            field = "paragraphs"
            extractor = self.registry.get("paragraphs") or self.default_extractor
        else:
            field = self.detector.detect_first(text)
            if not field:
                if is_datetime_text:
                    field = "datetime"
                else:
                    return {"type": None, "constraints": {}, "nullablePercent": None}

            # 날짜 관련 텍스트면 datetime 타입으로 강제 (FieldDetector 결과 무시)
            # 단, 나이/연령 키워드가 있으면 number_between_1_100으로 유지
            if is_datetime_text and not is_age_text and not is_integer_age:
                field = "datetime"
                extractor = self.registry.get("datetime") or self.default_extractor
            else:
                extractor = self.registry.get(field) or self.default_extractor

        # 비밀번호 제약 조건 컨텍스트 후처리 (문단 키워드가 없을 때만)
        if field == "number_between_1_100" and not is_paragraph_text:
            # 더 구체적인 비밀번호 키워드만 사용
            password_specific_keywords = ["비밀번호", "패스워드", "비번", "password", "대문자", "소문자", "특수문자", "특수기호", "symbol", "uppercase", "lowercase"]
            # "숫자는 1에서 100 사이" 같은 경우는 number_between_1_100으로 유지
            if re.search(r'숫자.*\d+.*\d+', text) and not any(keyword in text for keyword in ["비밀번호", "패스워드", "password"]):
                field = "number_between_1_100"
                extractor = self.registry.get("number_between_1_100") or self.default_extractor
            # 숫자 키워드는 비밀번호 컨텍스트에서만 사용
            elif any(keyword in text for keyword in password_specific_keywords) or ("숫자" in text and ("비밀번호" in text or "패스워드" in text or "password" in text)):
                field = "password"
                extractor = self.registry.get("password") or self.default_extractor

        # 최종 extractor 설정
        if not extractor:
            extractor = self.registry.get(field) or self.default_extractor

        # 1) 타입별 constraints - korean_* 타입들을 해당 타입으로 변환
        if field == "korean_phone":
            phone_extractor = self.registry.get("phone")
            if phone_extractor:
                phone_constraints = phone_extractor.extract(text) or {}
                if phone_constraints:  # phone constraints가 있으면 korean_phone → phone으로 변경
                    field = "phone"
                    extractor = phone_extractor
        
        elif field == "korean_state":
            state_extractor = self.registry.get("state")
            if state_extractor:
                state_constraints = state_extractor.extract(text) or {}
                if state_constraints:  # state constraints가 있으면 korean_state → state로 변경
                    field = "state"
                    extractor = state_extractor
        
        elif field == "korean_country":
            country_extractor = self.registry.get("country")
            if country_extractor:
                country_constraints = country_extractor.extract(text) or {}
                if country_constraints:  # country constraints가 있으면 korean_country → country로 변경
                    field = "country"
                    extractor = country_extractor
        
        elif field == "korean_full_name":
            # korean_full_name은 그대로 유지
            korean_full_name_extractor = self.registry.get("korean_full_name")
            if korean_full_name_extractor:
                extractor = korean_full_name_extractor
        
        elif field == "email_address":
            email_extractor = self.registry.get("email_address")
            if email_extractor:
                email_constraints = email_extractor.extract(text) or {}
                if email_constraints:  # email constraints가 있으면 email_address → email_address로 유지
                    extractor = email_extractor
        

        
        try:
            constraints = extractor.extract(text) or {}
        except ValueError as e:
            return {"type": None, "constraints": {}, "nullablePercent": None}

        # datetime 필드명 매핑 (from/to 유지)
        # if field == "datetime" and constraints:
        #     if "from" in constraints:
        #         constraints["min_date"] = constraints.pop("from")
        #     if "to" in constraints:
        #         constraints["max_date"] = constraints.pop("to")

        # 2) 전역 보조 제약 merge (password/phone 등 제한 타입일 때만 반영하려면 여기서 merge)
        global_c = self.qualifiers.extract(text)
        constraints.update(global_c)

        # 3) nullablePercent
        nullable = self.nullables.extract(text)

                    # 4) 최종 JSON 조립 (원 코드와 완전 동일 포맷)
        if field in CONSTRAINT_TYPES:
            # 모든 타입을 소문자로 반환
            type_name = field
            return {"type": type_name, "constraints": constraints, "nullablePercent": nullable}
        else:
            type_name = field
            return {"type": type_name, "constraints": {}, "nullablePercent": nullable}
