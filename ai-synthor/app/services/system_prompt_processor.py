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
            "number_between_1_100": ["age", "quantity", "count", "number"],
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
        # 1. 언어 감지
        language = detect_supported_language(prompt)
        
        # 2. 자연어 필드명과 제약 조건 파싱 시도 (한국어 + 영어 모두)
        parsed_fields = self._parse_natural_language_fields(prompt)
        if parsed_fields:
            return {
                "count": len(parsed_fields),
                "fields": parsed_fields
            }
        
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
    
    def _parse_natural_language_fields(self, prompt: str) -> List[Dict[str, Any]]:
        """자연어로 된 필드 요청을 파싱합니다."""
        fields = []
        
        # 문단 관련 특별 처리 - "정확히 3개의 문단" 같은 표현 우선 감지
        if "문단" in prompt:
            # 문단 필드 타입 추론
            field_type = "paragraphs"
            
            # 기존 constraint parser 사용
            field_constraints = self._parse_constraints_with_existing_parsers(prompt, field_type)
            
            # 필드명 생성 (영어로)
            generated_name = self._generate_english_field_name("문단", field_type)
            
            # nullable_percent를 constraints에서 제거하고 별도 필드로 설정
            nullable_percent = field_constraints.pop("nullable_percent", 0) if "nullable_percent" in field_constraints else 0
            
            fields.append({
                "name": generated_name,
                "type": self.field_type_mapping.get(field_type, field_type.title()),
                "constraints": field_constraints,
                "nullablePercent": nullable_percent
            })
            
            return fields
        
        # 필드명 추출 패턴 (한국어 + 영어)
        field_keywords = [
            # 프로필/아바타
            "프로필 이미지", "아바타", "avatar", "profile image", "profile picture", "profile photo",
            # 나이/연령
            "나이", "age", "연령",
            # 이름
            "이름", "name", "성명", "full name", "first name", "last name",
            # 이메일
            "이메일", "email", "이메일주소", "email address",
            # 비밀번호
            "비밀번호", "password", "패스워드",
            # 전화번호
            "전화번호", "phone", "휴대폰", "phone number", "telephone",
            # 주소
            "주소", "address", "street address",
            # 생년월일
            "생년월일", "birth date", "생일", "date of birth", "birthday",
            # 사용자명
            "사용자명", "username", "아이디", "user name", "login id",
            # 회사
            "회사명", "company name", "company", "organization",
            # 직책
            "직책", "job title", "직위", "position", "title",
            # 문단/설명
            "단락", "paragraph", "description", "설명", "내용", "content",
            # 기타
            "city", "state", "country", "postal code", "zip code"
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
            "email_address": "email",
            "password": "password",
            "phone": "phone",
            "address": "address",
            "datetime": "birth_date",
            "number_between_1_100": "age",
            "avatar": "profile_image",
            "username": "username",
            "company_name": "company_name",
            "job_title": "job_title",
            "paragraphs": "description",
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
            except:
                pass
        
        elif field_type == "phone":
            try:
                from .constraints.phone import PhoneExtractor
                phone_extractor = PhoneExtractor()
                phone_constraints = phone_extractor.extract(prompt)
                if phone_constraints:
                    constraints.update(phone_constraints)
            except:
                pass
        
        elif field_type == "datetime":
            try:
                from .constraints.datetime import DatetimeExtractor
                datetime_extractor = DatetimeExtractor()
                datetime_constraints = datetime_extractor.extract(prompt)
                if datetime_constraints:
                    constraints.update(datetime_constraints)
            except:
                pass
        
        elif field_type == "number_between_1_100":
            try:
                from .constraints.number_between import NumberBetweenExtractor
                number_extractor = NumberBetweenExtractor()
                number_constraints = number_extractor.extract(prompt)
                if number_constraints:
                    constraints.update(number_constraints)
            except:
                pass
        
        elif field_type == "avatar":
            try:
                from .constraints.avatar import AvatarExtractor
                avatar_extractor = AvatarExtractor()
                avatar_constraints = avatar_extractor.extract(prompt)
                if avatar_constraints:
                    constraints.update(avatar_constraints)
            except:
                pass
        
        elif field_type == "email_address":
            try:
                from .constraints.email import EmailExtractor
                email_extractor = EmailExtractor()
                email_constraints = email_extractor.extract(prompt)
                if email_constraints:
                    constraints.update(email_constraints)
            except:
                pass
        
        elif field_type == "paragraphs":
            try:
                from .constraints.paragraphs import ParagraphsExtractor
                paragraphs_extractor = ParagraphsExtractor()
                paragraphs_constraints = paragraphs_extractor.extract(prompt)
                if paragraphs_constraints:
                    constraints.update(paragraphs_constraints)
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
        
        # 제약 조건 기반 추론 (우선순위 높음)
        if "문단" in constraints_text_lower or "paragraph" in constraints_text_lower:
            return "paragraphs"
        elif "소수점" in constraints_text_lower or "decimal" in constraints_text_lower:
            return "number_between_1_100"
        elif "형식" in constraints_text_lower or "format" in constraints_text_lower:
            return "datetime"
        
        # 필드명 기반 추론 (더 구체적인 매칭부터)
        if any(keyword in field_name_lower for keyword in ["프로필 이미지", "profile image", "profile picture", "profile photo", "아바타", "avatar"]):
            return "avatar"
        elif any(keyword in field_name_lower for keyword in ["나이", "age"]):
            return "number_between_1_100"
        elif any(keyword in field_name_lower for keyword in ["이름", "name"]):
            return "full_name"
        elif any(keyword in field_name_lower for keyword in ["이메일", "email"]):
            return "email_address"
        elif any(keyword in field_name_lower for keyword in ["비밀번호", "패스워드", "password"]):
            return "password"
        elif any(keyword in field_name_lower for keyword in ["전화번호", "휴대폰", "phone"]):
            return "phone"
        elif any(keyword in field_name_lower for keyword in ["주소", "address"]):
            return "address"
        elif any(keyword in field_name_lower for keyword in ["생년월일", "생일", "birth"]):
            return "datetime"
        elif any(keyword in field_name_lower for keyword in ["문단", "단락", "paragraph", "description", "설명", "내용"]):
            return "paragraphs"
        
        return "full_name"  # 기본값
    
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
            
            # 필드명 생성
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
    ]
    
    processor = SystemPromptProcessor()
    
    for i, text in enumerate(test_cases, 1):
        print(f"## 입력: {text}")
        try:
            result = processor.process_system_prompt(text)
            print(f"{result}")
        except Exception as e:
            print(f"Error: {e}")
        print()