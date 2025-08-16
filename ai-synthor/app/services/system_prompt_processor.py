"""
System prompt processor for auto-generating field sets from overall purpose prompts.
"""
import re
from typing import Dict, Any, List
from ..utils.language_detect import detect_supported_language
from .korean_processor import parse_korean_text_to_json
from .english_processor import parse_english_text_to_json
from .parser import Parser

class SystemPromptProcessor:
    """Processes system prompts to generate complete field sets."""
    
    def __init__(self):
        # 필드 타입 매핑 (백엔드용 내부 타입 키)
        self.field_type_mapping = {
            "full_name": "full_name",
            "email_address": "email_address", 
            "password": "password",
            "datetime": "datetime",
            "phone": "phone",
            "address": "address",
            "city": "city",
            "state": "state",
            "country": "country",
            "postal_code": "postal_code",
            "username": "username",
            "company_name": "company_name",
            "job_title": "job_title",
            "credit_card_number": "credit_card_number",
            "credit_card_type": "credit_card_type",
            "avatar": "avatar",
            "url": "url",
            "paragraphs": "paragraphs",
            "time": "time",
            "latitude": "latitude",
            "longitude": "longitude",
            "number_between_1_100": "number_between_1_100",
            "product_price": "product_price",
            "currency": "currency",
            "iban": "iban",
            "swift_bic": "swift_bic",
            "mac_address": "mac_address",
            "ip_v4_address": "ip_v4_address",
            "ip_v6_address": "ip_v6_address",
            "user_agent": "user_agent",
            "app_name": "app_name",
            "app_version": "app_version",
            "device_model": "device_model",
            "device_brand": "device_brand",
            "device_os": "device_os",
            "domain_name": "domain_name",
            "language": "language",
            "color": "color",
            "catch_phrase": "catch_phrase",
            "product_description": "product_description",
            "product_name": "product_name",
            "product_category": "product_category",
            "department_corporate": "department_corporate",
            "department_retail": "department_retail",
            "street_address": "street_address",
            "first_name": "first_name",
            "last_name": "last_name",
            # 한국어 필드들
            "korean_full_name": "korean_full_name",
            "korean_first_name": "korean_first_name", 
            "korean_last_name": "korean_last_name",
            "korean_phone": "korean_phone",
            "korean_address": "korean_address",
            "korean_street_address": "korean_street_address",
            "korean_city": "korean_city",
            "korean_state": "korean_state",
            "korean_country": "korean_country",
            "korean_postal_code": "korean_postal_code",
            "korean_company_name": "korean_company_name",
            "korean_job_title": "korean_job_title",
            "korean_department_corporate": "korean_department_corporate",
            "korean_department_retail": "korean_department_retail",
            "korean_product_name": "korean_product_name",
            "korean_product_category": "korean_product_category",
            "korean_catch_phrase": "korean_catch_phrase",
            "korean_product_description": "korean_product_description",
            "korean_language": "korean_language",
            "korean_color": "korean_color",
        }
        
        # 필드명 생성 규칙
        self.field_name_patterns = {
            "full_name": ["full_name", "name", "fullname"],
            "email_address": ["email", "email_address", "emailAddress"],
            "password": ["password", "pwd", "pass"],
            "datetime": ["birth_date", "birthDate", "date", "datetime", "created_at", "updated_at"],
            "phone": ["phone", "phone_number", "phoneNumber", "tel", "telephone"],
            "address": ["address", "home_address", "shipping_address"],
            "city": ["city", "town"],
            "state": ["state", "province", "region"],
            "country": ["country", "nation"],
            "postal_code": ["postal_code", "zip_code", "zipCode", "postcode"],
            "username": ["username", "user_name", "login_id"],
            "company_name": ["company_name", "companyName", "company", "organization"],
            "job_title": ["job_title", "jobTitle", "position", "title"],
            "credit_card_number": ["credit_card_number", "cardNumber", "card_number"],
            "credit_card_type": ["credit_card_type", "cardType", "card_type"],
            "avatar": ["avatar", "profile_image", "profileImage"],
            "url": ["url", "website", "link"],
            "paragraphs": ["description", "bio", "about", "content"],
            "time": ["time", "created_time", "updated_time"],
            "number_between_1_100": ["age", "quantity", "count"],
        }
        
        # 개별 필드 파서 초기화
        self.parser = Parser()
    
    def process_system_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Process a system prompt to generate a complete field set.
        
        Args:
            prompt: The overall purpose prompt (e.g., "쇼핑몰에서 사용자 등록을 위한 정보")
            
        Returns:
            Dict with count and fields array
        """
        # 1. 자연어 필드명과 제약 조건 파싱 시도 (한국어 + 영어 모두) - 우선순위 높음
        parsed_fields = self._extract_fields_from_prompt(prompt)
        if parsed_fields:
            return {
                "count": len(parsed_fields),
                "fields": parsed_fields
            }
        
        # 2. 언어 감지
        language = detect_supported_language(prompt)
        
        # 3. 기존 프로세서 선택
        if language == "ko":
            result = parse_korean_text_to_json(prompt)
        else:
            result = parse_english_text_to_json(prompt)
        
        # 4. 에러 처리
        if "error" in result:
            # 에러가 있으면 기본 필드 세트 생성
            return self._generate_default_fields(prompt)
        
        # 5. 응답 형식 변환
        return self._transform_response(result)
    
    def _extract_fields_from_prompt(self, prompt: str) -> List[Dict[str, Any]]:
        """자연어로 된 필드 요청을 파싱합니다."""
        fields = []
        processed_field_types = set()  # 중복 방지를 위한 세트
        
        # 필드명 추출 패턴 (한국어 + 영어) - 더 포괄적으로 확장
        field_keywords = [
            # 프로필/아바타
            "프로필 이미지", "아바타", "avatar", "profile image", "profile picture", "profile photo",
            # 나이/연령
            "나이", "연령", "user age", "user's age",
            # 이름
            "이름", "name", "성명", "full name", "first name", "last name", "korean full name",
            # 이메일
            "이메일", "email", "이메일주소", "email address",
            # 비밀번호
            "비밀번호", "password", "패스워드",
            # 전화번호
            "전화번호", "phone", "휴대폰", "phone number", "telephone", "korean phone", "연락처", "010으로 시작",
            # 주소
            "주소", "address", "street address", "korean address", "배송주소", "회사 주소",
            # 생년월일
            "생년월일", "birth date", "생일", "date of birth", "birthday", "datetime", "yyyy-mm-dd",
            # 사용자명
            "사용자명", "username", "아이디", "user name", "login id",
            # 회사
            "회사명", "company name", "company", "organization", "korean company name",
            # 직책
            "직책", "job title", "직위", "position", "title", "korean job title",
            # 도시/주/국가
            "도시", "city", "korean city",
            "korean state", 
            "국가", "country", "korean country",
            "우편번호", "postal code", "zip code", "korean postal code",
            # 기타
            "url", "website", "link", "웹사이트",
            "time", "시간",
                         # 문단/설명 (구체적인 키워드만)
             "자기소개 문단", "자기소개", "3개의 문단", "3개 문단", "문단", "paragraphs",
        ]
        
        found_fields = []
        
        # 각 키워드가 프롬프트에 있는지 확인 (순서 유지)
        for keyword in field_keywords:
            if keyword.lower() in prompt.lower():
                found_fields.append(keyword)
        
        # 프롬프트에서 나타나는 순서대로 필드 정렬
        ordered_fields = []
        for keyword in found_fields:
            # 프롬프트에서 해당 키워드가 나타나는 위치를 찾아서 정렬
            position = prompt.lower().find(keyword.lower())
            ordered_fields.append((position, keyword))
        
        # 위치 순서대로 정렬
        ordered_fields.sort(key=lambda x: x[0])
        
        # 각 필드에 대해 처리 (순서대로)
        for position, field_name in ordered_fields:
            # 타입 추론
            field_type = self._infer_field_type(field_name, prompt)
            
            # None인 경우 특별 처리 (인식하지 못하는 필드)
            if field_type is None:
                # 제약 조건만 있는 필드인지 확인
                if any(keyword in field_name.lower() for keyword in ["010으로 시작", "yyyy-mm-dd"]):
                    continue  # 제약 조건만 있는 필드는 건너뛰기
                else:
                    # 인식하지 못하는 필드의 경우 null 타입으로 생성
                    fields.append({
                        "name": field_name.lower().replace(" ", "_").replace("-", "_"),
                        "type": None,
                        "constraints": {},
                        "nullablePercent": None
                    })
                    continue
            
            # 중복 방지: 같은 타입의 필드는 한 번만 처리
            if field_type in processed_field_types:
                continue
            
            processed_field_types.add(field_type)
            
            # 기존 constraint parser 사용
            field_constraints = self._parse_constraints_with_existing_parsers(prompt, field_type)
            
            # 필드명 생성 (영어로)
            generated_name = self._generate_english_field_name(field_name, field_type)
            
            # nullable_percent를 constraints에서 제거하고 별도 필드로 설정
            nullable_percent = field_constraints.pop("nullable_percent", 0) if "nullable_percent" in field_constraints else 0
            
            fields.append({
                "name": generated_name,
                "type": self.field_type_mapping.get(field_type, field_type.title()),
                "constraints": field_constraints,
                "nullablePercent": nullable_percent
            })
        
        return fields
    
    def _generate_english_field_name(self, field_name: str, field_type: str) -> str:
        """영어 필드명을 생성합니다."""
        # 필드 타입에 따른 기본 영어 필드명
        type_to_name = {
            "full_name": "full_name",
            "korean_full_name": "full_name",
            "email_address": "email",
            "password": "password",
            "phone": "phone",
            "korean_phone": "phone",
            "address": "address",
            "korean_address": "address",
            "datetime": "birth_date",
            "username": "username",
            "company_name": "company_name",
            "korean_company_name": "company_name",
            "job_title": "job_title",
            "korean_job_title": "job_title",
            "paragraphs": "description",
            "avatar": "profile_image",
            "city": "city",
            "korean_city": "city",
            "state": "state",
            "korean_state": "state",
            "country": "country",
            "korean_country": "country",
            "postal_code": "postal_code",
            "korean_postal_code": "postal_code",
            "url": "url",
            "time": "time",
            "number_between_1_100": "age",
        }
        
        # 타입에 따른 기본 이름 반환
        if field_type in type_to_name:
            return type_to_name[field_type]
        
        # 기본 변환: 공백을 언더스코어로, 소문자로
        return field_name.lower().replace(" ", "_").replace("-", "_")
    
    def _parse_constraints_with_existing_parsers(self, prompt: str, field_type: str) -> Dict[str, Any]:
        """기존 constraint parser들을 사용해서 제약 조건을 파싱합니다."""
        constraints = {}
        
        # nullable 퍼센트 파싱 (기존 nullables 모듈 사용)
        try:
            from .nullables import NullablePercentExtractor
            nullable_extractor = NullablePercentExtractor()
            nullable_percent = nullable_extractor.extract(prompt)
            if nullable_percent:
                constraints["nullable_percent"] = nullable_percent
        except:
            pass
        
        # 필드 타입별로 적절한 constraint parser 사용
        if field_type == "password":
            try:
                from .constraints.password import PasswordExtractor
                password_extractor = PasswordExtractor()
                password_constraints = password_extractor.extract(prompt)
                if password_constraints:
                    constraints.update(password_constraints)
                
                # 비밀번호 최소 길이 파싱 개선
                import re
                min_length_patterns = [
                    r'최소\s*(\d+)\s*자', r'(\d+)\s*자\s*이상', r'minimum\s*(\d+)\s*characters?',
                    r'(\d+)\s*characters?\s*or\s*more', r'at\s*least\s*(\d+)\s*characters?',
                    r'minimum\s*length\s*(\d+)', r'min\s*length\s*(\d+)'
                ]
                
                for pattern in min_length_patterns:
                    match = re.search(pattern, prompt, re.I)
                    if match and match.group(1).isdigit():
                        min_length = int(match.group(1))
                        if "minimum_length" not in constraints or constraints["minimum_length"] < min_length:
                            constraints["minimum_length"] = min_length
                        break
            except:
                pass
        
        elif field_type in ["phone", "korean_phone"]:
            try:
                from .constraints.phone import PhoneExtractor
                phone_extractor = PhoneExtractor()
                phone_constraints = phone_extractor.extract(prompt)
                if phone_constraints:
                    constraints.update(phone_constraints)
                
                # 전화번호 시작 번호 파싱 개선
                import re
                start_patterns = [
                    r'(\d{3})\s*으로\s*시작', r'(\d{3})\s*로\s*시작', r'starts?\s*with\s*(\d{3})',
                    r'begin\s*with\s*(\d{3})', r'(\d{3})\s*로\s*시작하는', r'(\d{3})\s*으로\s*시작하는',
                    r'(\+\d{2})\s*으로\s*시작', r'(\+\d{2})\s*로\s*시작', r'starts?\s*with\s*(\+\d{2})',
                    r'begin\s*with\s*(\+\d{2})', r'(\+\d{2})\s*로\s*시작하는', r'(\+\d{2})\s*으로\s*시작하는',
                    r'(\d{2})\s*으로\s*시작', r'(\d{2})\s*로\s*시작', r'starts?\s*with\s*(\d{2})',
                    r'begin\s*with\s*(\d{2})', r'(\d{2})\s*로\s*시작하는', r'(\d{2})\s*으로\s*시작하는'
                ]
                
                for pattern in start_patterns:
                    match = re.search(pattern, prompt, re.I)
                    if match:
                        start_number = match.group(1)
                        # 전화번호 시작 번호에 따라 format만 설정 (starts_with 제거)
                        if start_number == "010":
                            constraints["format"] = "###-###-####"
                        elif start_number.startswith("+82"):
                            constraints["format"] = "+# ### ### ####"
                        elif start_number.startswith("82"):
                            constraints["format"] = "#-###-###-####"
                        else:
                            constraints["format"] = "###-###-####"  # 기본 형식
                        break
            except:
                pass
        
        elif field_type == "datetime":
            try:
                from .constraints.datetime import DatetimeExtractor
                datetime_extractor = DatetimeExtractor()
                datetime_constraints = datetime_extractor.extract(prompt)
                if datetime_constraints:
                    constraints.update(datetime_constraints)
                
                # datetime 범위 파싱 개선
                import re
                date_range_patterns = [
                    r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*부터\s*(\d{1,2})월\s*(\d{1,2})일\s*까지',
                    r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*부터\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*까지',
                    r'(\d{4})-(\d{1,2})-(\d{1,2})\s*부터\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*까지',
                    r'from\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*to\s*(\d{4})-(\d{1,2})-(\d{1,2})',
                    r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*부터\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일'
                ]
                
                for i, pattern in enumerate(date_range_patterns):
                    match = re.search(pattern, prompt, re.I)
                    if match:
                        groups = match.groups()
                        
                        if i == 0:  # 첫 번째 패턴: 같은 년도 내에서 월/일만 다른 경우
                            if len(groups) >= 5:
                                # 시작 날짜
                                start_year = groups[0]
                                start_month = groups[1].zfill(2)
                                start_day = groups[2].zfill(2)
                                constraints["from"] = f"{start_year}-{start_month}-{start_day}"
                                
                                # 종료 날짜 (같은 년도)
                                end_year = start_year
                                end_month = groups[3].zfill(2)
                                end_day = groups[4].zfill(2)
                                constraints["to"] = f"{end_year}-{end_month}-{end_day}"
                                break
                        else:  # 다른 패턴들
                            if len(groups) >= 6:
                                # 시작 날짜
                                start_year = groups[0]
                                start_month = groups[1].zfill(2)
                                start_day = groups[2].zfill(2)
                                constraints["from"] = f"{start_year}-{start_month}-{start_day}"
                                
                                # 종료 날짜
                                end_year = groups[3]
                                end_month = groups[4].zfill(2)
                                end_day = groups[5].zfill(2)
                                constraints["to"] = f"{end_year}-{end_month}-{end_day}"
                                break
            except:
                pass
        
        elif field_type == "number_between_1_100":
            try:
                from .constraints.number_between import NumberBetweenExtractor
                number_extractor = NumberBetweenExtractor()
                number_constraints = number_extractor.extract(prompt)
                if number_constraints:
                    constraints.update(number_constraints)
                
                # 숫자 범위 파싱 개선
                import re
                range_patterns = [
                    r'(\d+)\s*에서\s*(\d+)\s*까지', r'(\d+)\s*이상\s*(\d+)\s*이하', r'(\d+)\s*to\s*(\d+)', r'(\d+)\s*-\s*(\d+)',
                    r'between\s*(\d+)\s*and\s*(\d+)', r'(\d+)\s*~?\s*(\d+)'
                ]
                
                decimal_patterns = [
                    r'소수점\s*(\d+)\s*자리', r'(\d+)\s*decimal\s*places?', r'decimals?\s*(\d+)'
                ]
                
                for pattern in range_patterns:
                    match = re.search(pattern, prompt, re.I)
                    if match and match.group(1).isdigit() and match.group(2).isdigit():
                        min_val = int(match.group(1))
                        max_val = int(match.group(2))
                        if min_val <= max_val:
                            constraints["min"] = min_val
                            constraints["max"] = max_val
                        else:
                            constraints["min"] = max_val
                            constraints["max"] = min_val
                        break
                
                for pattern in decimal_patterns:
                    match = re.search(pattern, prompt, re.I)
                    if match and match.group(1).isdigit():
                        constraints["decimals"] = int(match.group(1))
                        break
            except:
                pass
        
        elif field_type == "avatar":
            try:
                from .constraints.avatar import AvatarExtractor
                avatar_extractor = AvatarExtractor()
                avatar_constraints = avatar_extractor.extract(prompt)
                if avatar_constraints:
                    constraints.update(avatar_constraints)
                
                # 아바타 크기와 형식 파싱 개선
                import re
                size_patterns = [
                    r'(\d+)x(\d+)', r'(\d+)\s*x\s*(\d+)', r'(\d+)\s*×\s*(\d+)',
                    r'size\s*(\d+)x(\d+)', r'(\d+)\s*by\s*(\d+)'
                ]
                
                format_patterns = [
                    r'(png|jpg|jpeg|gif|webp)', r'format\s*(png|jpg|jpeg|gif|webp)',
                    r'형식\s*(png|jpg|jpeg|gif|webp)', r'(png|jpg|jpeg|gif|webp)\s*형식'
                ]
                
                for pattern in size_patterns:
                    match = re.search(pattern, prompt, re.I)
                    if match and match.group(1).isdigit() and match.group(2).isdigit():
                        width = int(match.group(1))
                        height = int(match.group(2))
                        constraints["size"] = f"{width}x{height}"
                        break
                
                for pattern in format_patterns:
                    match = re.search(pattern, prompt, re.I)
                    if match:
                        constraints["format"] = match.group(1).lower()
                        break
            except:
                pass
        
        elif field_type == "email_address":
            try:
                from .constraints.email import EmailExtractor
                email_extractor = EmailExtractor()
                email_constraints = email_extractor.extract(prompt)
                if email_constraints:
                    constraints.update(email_constraints)
                
                # 이메일 도메인 제약 조건 파싱 개선
                import re
                domain_patterns = [
                    r'(\w+\.com)\s*만', r'(\w+\.com)\s*only', r'only\s*(\w+\.com)',
                    r'(\w+\.com)\s*도메인', r'domain\s*(\w+\.com)', r'(\w+\.com)\s*domain'
                ]
                
                for pattern in domain_patterns:
                    match = re.search(pattern, prompt, re.I)
                    if match:
                        domain = match.group(1).lower()
                        constraints["domain"] = domain
                        break
            except:
                pass
        
        elif field_type == "paragraphs":
            try:
                from .constraints.paragraphs import ParagraphsExtractor
                paragraphs_extractor = ParagraphsExtractor()
                paragraphs_constraints = paragraphs_extractor.extract(prompt)
                if paragraphs_constraints:
                    constraints.update(paragraphs_constraints)
                
                # 문단 개수 파싱 개선
                import re
                exact_count_patterns = [
                    r'정확히\s*(\d+)\s*개의?\s*문단', r'(\d+)\s*개의?\s*문단', r'exactly\s*(\d+)\s*paragraphs?',
                    r'(\d+)\s*paragraphs?\s*exactly', r'precisely\s*(\d+)\s*paragraphs?'
                ]
                
                for pattern in exact_count_patterns:
                    match = re.search(pattern, prompt, re.I)
                    if match and match.group(1).isdigit():
                        count = int(match.group(1))
                        constraints["at least"] = count
                        constraints["but no more than"] = count
                        break
            except:
                pass
        
        elif field_type in ["full_name", "korean_full_name"]:
            try:
                from .constraints.korean_full_name import KoreanFullNameExtractor
                name_extractor = KoreanFullNameExtractor()
                name_constraints = name_extractor.extract(prompt)
                # 명시적으로 성씨를 요청하지 않은 경우 빈 객체 유지
                if name_constraints and "lastName" in name_constraints:
                    # 성씨 관련 키워드가 프롬프트에 있는지 확인
                    surname_keywords = ["성씨", "성", "씨", "lastName", "last name", "family name", "surname"]
                    if any(keyword in prompt.lower() for keyword in surname_keywords):
                        constraints.update(name_constraints)
                    # 명시적으로 성씨를 요청하지 않았으면 lastName 제거
                    else:
                        pass  # 빈 객체 유지
            except:
                pass
        
        elif field_type in ["address", "korean_address"]:
            try:
                from .constraints.default import DefaultExtractor
                address_extractor = DefaultExtractor()
                address_constraints = address_extractor.extract(prompt)
                if address_constraints:
                    constraints.update(address_constraints)
            except:
                pass
        
        elif field_type in ["city", "korean_city"]:
            try:
                from .constraints.default import DefaultExtractor
                city_extractor = DefaultExtractor()
                city_constraints = city_extractor.extract(prompt)
                if city_constraints:
                    constraints.update(city_constraints)
            except:
                pass
        
        elif field_type in ["state", "korean_state"]:
            try:
                from .constraints.state import StateExtractor
                state_extractor = StateExtractor()
                state_constraints = state_extractor.extract(prompt)
                if state_constraints:
                    constraints.update(state_constraints)
            except:
                pass
        
        elif field_type in ["country", "korean_country"]:
            try:
                from .constraints.country import CountryExtractor
                country_extractor = CountryExtractor()
                country_constraints = country_extractor.extract(prompt)
                if country_constraints:
                    constraints.update(country_constraints)
            except:
                pass
        
        elif field_type in ["postal_code", "korean_postal_code"]:
            try:
                from .constraints.default import DefaultExtractor
                postal_extractor = DefaultExtractor()
                postal_constraints = postal_extractor.extract(prompt)
                if postal_constraints:
                    constraints.update(postal_constraints)
            except:
                pass
        
        elif field_type == "url":
            try:
                from .constraints.url import URLExtractor
                url_extractor = URLExtractor()
                url_constraints = url_extractor.extract(prompt)
                if url_constraints:
                    constraints.update(url_constraints)
            except:
                pass
        
        elif field_type == "time":
            try:
                from .constraints.time import TimeExtractor
                time_extractor = TimeExtractor()
                time_constraints = time_extractor.extract(prompt)
                if time_constraints:
                    constraints.update(time_constraints)
            except:
                pass
        
        # 전역 qualifiers 파싱 (기존 qualifiers 모듈 사용)
        try:
            from .qualifiers import GlobalQualifiersExtractor
            qualifiers_extractor = GlobalQualifiersExtractor()
            global_constraints = qualifiers_extractor.extract(prompt)
            if global_constraints:
                constraints.update(global_constraints)
        except:
            pass
        
        return constraints
    
    def _infer_field_type(self, field_name: str, constraints_text: str) -> str:
        """필드명과 제약 조건을 기반으로 타입을 추론합니다."""
        field_name_lower = field_name.lower()
        constraints_text_lower = constraints_text.lower()
        
        # 필드명 기반 추론 (더 구체적인 매칭부터)
        if any(keyword in field_name_lower for keyword in ["프로필 이미지", "profile image", "profile picture", "profile photo", "아바타", "avatar"]):
            return "avatar"
        elif any(keyword in field_name_lower for keyword in ["나이", "age", "연령"]):
            return "number_between_1_100"
        elif any(keyword in field_name_lower for keyword in ["이름", "name", "성명", "full name", "first name", "last name"]):
            return "korean_full_name"
        elif any(keyword in field_name_lower for keyword in ["korean full name"]):
            return "korean_full_name"
        elif any(keyword in field_name_lower for keyword in ["이메일", "email", "이메일주소", "email address"]):
            return "email_address"
        elif any(keyword in field_name_lower for keyword in ["비밀번호", "패스워드", "password"]):
            return "password"
        elif any(keyword in field_name_lower for keyword in ["전화번호", "휴대폰", "phone", "phone number", "telephone", "연락처"]):
            return "phone"
        elif any(keyword in field_name_lower for keyword in ["korean phone"]):
            return "korean_phone"
        elif any(keyword in field_name_lower for keyword in ["주소", "address", "street address", "배송주소", "회사 주소"]):
            return "address"
        elif any(keyword in field_name_lower for keyword in ["korean address"]):
            return "korean_address"
        elif any(keyword in field_name_lower for keyword in ["생년월일", "생일", "birth", "birthday", "date of birth", "datetime"]):
            return "datetime"
        elif any(keyword in field_name_lower for keyword in ["자기소개 문단", "자기소개", "문단", "paragraphs"]):
            return "paragraphs"
        elif any(keyword in field_name_lower for keyword in ["사용자명", "username", "아이디", "user name", "login id"]):
            return "username"
        elif any(keyword in field_name_lower for keyword in ["회사명", "company name", "company", "organization"]):
            return "company_name"
        elif any(keyword in field_name_lower for keyword in ["korean company name"]):
            return "korean_company_name"
        elif any(keyword in field_name_lower for keyword in ["직책", "job title", "직위", "position", "title"]):
            return "job_title"
        elif any(keyword in field_name_lower for keyword in ["korean job title"]):
            return "korean_job_title"
        elif any(keyword in field_name_lower for keyword in ["도시", "city"]):
            return "city"
        elif any(keyword in field_name_lower for keyword in ["korean city"]):
            return "korean_city"
        elif any(keyword in field_name_lower for keyword in ["주"]):
            return "state"
        elif any(keyword in field_name_lower for keyword in ["korean state"]):
            return "korean_state"
        elif any(keyword in field_name_lower for keyword in ["국가", "country"]):
            return "country"
        elif any(keyword in field_name_lower for keyword in ["korean country"]):
            return "korean_country"
        elif any(keyword in field_name_lower for keyword in ["우편번호", "postal code", "zip code"]):
            return "postal_code"
        elif any(keyword in field_name_lower for keyword in ["korean postal code"]):
            return "korean_postal_code"
        elif any(keyword in field_name_lower for keyword in ["url", "website", "link", "웹사이트"]):
            return "url"
        elif any(keyword in field_name_lower for keyword in ["time", "시간"]):
            return "time"
        elif any(keyword in field_name_lower for keyword in ["010으로 시작", "yyyy-mm-dd"]):
            return None  # 이 필드들은 제약 조건만 있고 실제 필드가 아님
        
        # 인식하지 못하는 필드의 경우 null 반환
        return None  # 기본값
    
    def _generate_default_fields(self, prompt: str) -> Dict[str, Any]:
        """기본 필드 세트를 생성합니다."""
        # 프롬프트에서 키워드를 기반으로 기본 필드 추출
        prompt_lower = prompt.lower()
        
        default_fields = []
        
        # 사용자 등록 관련 키워드
        if any(keyword in prompt_lower for keyword in ["사용자", "user", "등록", "register", "회원", "member"]):
            default_fields.extend([
                {"name": "full_name", "type": self.field_type_mapping["full_name"], "constraints": {}, "nullablePercent": 0},
                {"name": "email", "type": self.field_type_mapping["email_address"], "constraints": {}, "nullablePercent": 0},
                {"name": "password", "type": self.field_type_mapping["password"], "constraints": {"minimum_length": 8}, "nullablePercent": 0},
            ])
        
        # 쇼핑몰 관련 키워드
        if any(keyword in prompt_lower for keyword in ["쇼핑", "shopping", "구매", "purchase", "주문", "order"]):
            default_fields.extend([
                {"name": "address", "type": self.field_type_mapping["address"], "constraints": {}, "nullablePercent": 0},
                {"name": "phone", "type": self.field_type_mapping["phone"], "constraints": {}, "nullablePercent": 0},
            ])
        
        # 개인정보 관련 키워드
        if any(keyword in prompt_lower for keyword in ["개인정보", "personal", "정보", "information"]):
            if not any(field["name"] == "birth_date" for field in default_fields):
                default_fields.append({"name": "birth_date", "type": self.field_type_mapping["datetime"], "constraints": {"format": "yyyy-mm-dd"}, "nullablePercent": 0})
        
        # 기본 필드가 없으면 최소한의 필드 제공
        if not default_fields:
            default_fields = [
                {"name": "full_name", "type": self.field_type_mapping["full_name"], "constraints": {}, "nullablePercent": 0},
                {"name": "email", "type": self.field_type_mapping["email_address"], "constraints": {}, "nullablePercent": 0},
            ]
        
        return {
            "count": len(default_fields),
            "fields": default_fields
        }
    
    def _transform_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """기존 프로세서 결과를 새로운 응답 형식으로 변환합니다."""
        if "fields" not in result:
            return self._generate_default_fields("")
        
        transformed_fields = []
        
        for field in result["fields"]:
            field_type = field.get("type", "")
            field_name = field.get("name", "")
            
            # 기존 필드명이 있으면 그대로 사용, 없으면 생성
            if not field_name:
                field_name = self._generate_field_name(field_type)
            
            # 타입 매핑 (백엔드용 내부 타입 키)
            mapped_type = self.field_type_mapping.get(field_type, field_type)
            
            # 제약 조건 변환
            constraints = field.get("constraints", {})
            transformed_constraints = {}
            
            for key, value in constraints.items():
                # 키 이름 변환
                if key == "min_length":
                    transformed_constraints["minimum_length"] = value
                elif key == "min":
                    transformed_constraints["minimum"] = value
                elif key == "max":
                    transformed_constraints["maximum"] = value
                elif key == "format":
                    transformed_constraints["format"] = value
                elif key == "only":
                    transformed_constraints["only"] = value
                else:
                    transformed_constraints[key] = value
            
            # nullablePercent 처리 - 사용자가 명시적으로 요청하지 않으면 0
            nullable_percent = field.get("nullablePercent", 0) if field.get("nullablePercent") is not None else 0
            
            transformed_fields.append({
                "name": field_name,
                "type": mapped_type,
                "constraints": transformed_constraints,
                "nullablePercent": nullable_percent
            })
        
        return {
            "count": len(transformed_fields),
            "fields": transformed_fields
        }
    
    def _generate_field_name(self, field_type: str) -> str:
        """필드 타입에 따라 적절한 필드명을 생성합니다."""
        # 기본 패턴에서 첫 번째 이름 사용
        if field_type in self.field_name_patterns:
            return self.field_name_patterns[field_type][0]
        
        # 기본 규칙: snake_case로 변환
        return field_type.lower().replace(" ", "_")


# 모듈 직접 실행 시 테스트
if __name__ == "__main__":
    from .system_prompt_processor import SystemPromptProcessor
    
    test_cases = [
        "쇼핑몰에서 사용자 등록을 위한 정보",
        "프로필 이미지 100x100 png 형식으로 설정해주고, 나이는 20 이상 60 이하, 소수점 1자리, nullable 10%",
        "비밀번호는 최소 12자 이상이고 대문자 2개, 소문자 2개, 숫자 2개, 특수문자 2개 포함, 이메일은 naver.com만",
        "전화번호는 010으로 시작하고, 생년월일은 yyyy-mm-dd 형식으로, nullable 5%",
        "E-commerce user registration form with profile image 150x150 jpg format",
        "Password minimum 10 characters with uppercase, lowercase, numbers, symbols. Email only gmail.com",
        "온라인 교육 플랫폼 회원가입: 이름, 이메일(gmail.com만), 비밀번호(최소 10자 대문자 1개 소문자 1개 숫자 1개), 프로필 이미지(300x300 png), 나이(15 이상 70 이하), nullable 10%",
        "온라인 교육 플랫폼 회원가입: 이름, 이메일(gmail.com만), 비밀번호(최소 10자 대문자 1개 소문자 1개 숫자 1개), 프로필 이미지(300x300 png), 나이(15 이상 70 이하",
        "정확히 3개의 문단, null 10",
        # 전체 프롬프트 테스트 케이스 추가
        "사용자 프로필: 이름, 나이, 이메일, 비밀번호, 프로필 이미지",
        "회원가입 폼: 이름, 이메일, 비밀번호, 전화번호, 주소",
        "개인정보 입력: 이름, 생년월일, 나이, 이메일, 전화번호, 주소, 도시, 주, 국가, 우편번호",
        "사용자 등록: 이름, 이메일, 비밀번호, 프로필 이미지, 나이, 문단",
        "회원 정보: 이름, 이메일, 비밀번호, 전화번호, 주소, 회사명, 직책",
        "온라인 쇼핑몰 회원가입: 이름, 이메일, 비밀번호, 전화번호, 배송주소, 도시, 주, 국가, 우편번호",
        "교육 플랫폼 가입: 이름, 이메일, 비밀번호, 나이, 프로필 이미지, 자기소개 문단",
        "소셜 미디어 프로필: 이름, 이메일, 비밀번호, 프로필 이미지, 자기소개, 웹사이트 URL",
        "기업 회원가입: 회사명, 직책, 이름, 이메일, 비밀번호, 전화번호, 회사 주소",
        "개인 포트폴리오: 이름, 이메일, 프로필 이미지, 자기소개 문단, 웹사이트 URL, 연락처",
        "온라인 뱅킹 가입: 이름, 이메일, 비밀번호, 전화번호, 주소, 생년월일, 나이",
        "전화번호는 +82로 시작하고, 이메일은 gmail.com만",
        "전화번호는 82로 시작하고, 이름은 장씨만"
    ]
    
    processor = SystemPromptProcessor()
    
    for i, text in enumerate(test_cases, 1):
        print(f"## 테스트 {i}: {text}")
        try:
            result = processor.process_system_prompt(text)
            print(f"결과: {result}")
            print(f"필드 수: {result.get('count', 0)}")
            print(f"필드 목록:")
            for field in result.get('fields', []):
                print(f"  - {field.get('name')} ({field.get('type')})")
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()