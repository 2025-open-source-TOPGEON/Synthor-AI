"""
System prompt processor for auto-generating field sets from overall purpose prompts.
"""
import re
from typing import Dict, Any, List
from ..utils.language_detect import detect_supported_language
from .korean_processor import parse_korean_text_to_json
from .english_processor import parse_english_text_to_json

class SystemPromptProcessor:
    """Processes system prompts to generate complete field sets."""
    
    def __init__(self):
        # 필드 타입 매핑 (응답 형식에 맞게 변환)
        self.field_type_mapping = {
            "full_name": "Full Name",
            "email_address": "Email Address", 
            "password": "Password",
            "datetime": "datetime",
            "phone": "Phone Number",
            "address": "Address",
            "city": "City",
            "state": "State",
            "country": "Country",
            "postal_code": "Postal Code",
            "username": "Username",
            "company_name": "Company Name",
            "job_title": "Job Title",
            "credit_card_number": "Credit Card Number",
            "credit_card_type": "Credit Card Type",
            "avatar": "Avatar",
            "url": "URL",
            "paragraphs": "Paragraphs",
            "time": "Time",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "number_between_1_100": "Number",
            "product_price": "Product Price",
            "currency": "Currency",
            "iban": "IBAN",
            "swift_bic": "SWIFT BIC",
            "mac_address": "MAC Address",
            "ip_v4_address": "IPv4 Address",
            "ip_v6_address": "IPv6 Address",
            "user_agent": "User Agent",
            "app_name": "App Name",
            "app_version": "App Version",
            "device_model": "Device Model",
            "device_brand": "Device Brand",
            "device_os": "Device OS",
            "domain_name": "Domain Name",
            "language": "Language",
            "color": "Color",
            "catch_phrase": "Catch Phrase",
            "product_description": "Product Description",
            "product_name": "Product Name",
            "product_category": "Product Category",
            "department_corporate": "Department",
            "department_retail": "Department",
            "street_address": "Street Address",
            "first_name": "First Name",
            "last_name": "Last Name",
            # 한국어 필드들
            "korean_full_name": "Korean Full Name",
            "korean_first_name": "Korean First Name", 
            "korean_last_name": "Korean Last Name",
            "korean_phone": "Korean Phone",
            "korean_address": "Korean Address",
            "korean_street_address": "Korean Street Address",
            "korean_city": "Korean City",
            "korean_state": "Korean State",
            "korean_country": "Korean Country",
            "korean_postal_code": "Korean Postal Code",
            "korean_company_name": "Korean Company Name",
            "korean_job_title": "Korean Job Title",
            "korean_department_corporate": "Korean Department",
            "korean_department_retail": "Korean Department",
            "korean_product_name": "Korean Product Name",
            "korean_product_category": "Korean Product Category",
            "korean_catch_phrase": "Korean Catch Phrase",
            "korean_product_description": "Korean Product Description",
            "korean_language": "Korean Language",
            "korean_color": "Korean Color",
        }
    
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
        
        # 2. 적절한 프로세서 선택
        if language == "ko":
            result = parse_korean_text_to_json(prompt)
        else:
            result = parse_english_text_to_json(prompt)
        
        # 3. 에러 처리
        if "error" in result:
            # 에러가 있으면 기본 필드 세트 생성
            return self._generate_default_fields(prompt)
        
        # 4. 응답 형식 변환
        return self._transform_response(result)
    
    def _generate_default_fields(self, prompt: str) -> Dict[str, Any]:
        """기본 필드 세트를 생성합니다."""
        # 프롬프트에서 키워드를 기반으로 기본 필드 추출
        prompt_lower = prompt.lower()
        
        default_fields = []
        
        # 사용자 등록 관련 키워드
        if any(keyword in prompt_lower for keyword in ["사용자", "user", "등록", "register", "회원", "member"]):
            default_fields.extend([
                {"name": "full_name", "type": "Full Name", "constraints": {}, "nullablePercent": 0},
                {"name": "email", "type": "Email Address", "constraints": {}, "nullablePercent": 0},
                {"name": "password", "type": "Password", "constraints": {"minimum_length": 8}, "nullablePercent": 0},
            ])
        
        # 쇼핑몰 관련 키워드
        if any(keyword in prompt_lower for keyword in ["쇼핑", "shopping", "구매", "purchase", "주문", "order"]):
            default_fields.extend([
                {"name": "address", "type": "Address", "constraints": {}, "nullablePercent": 10},
                {"name": "phone", "type": "Phone Number", "constraints": {}, "nullablePercent": 5},
            ])
        
        # 개인정보 관련 키워드
        if any(keyword in prompt_lower for keyword in ["개인정보", "personal", "정보", "information"]):
            if not any(field["name"] == "birth_date" for field in default_fields):
                default_fields.append({"name": "birth_date", "type": "datetime", "constraints": {"format": "yyyy-mm-dd"}, "nullablePercent": 10})
        
        # 기본 필드가 없으면 최소한의 필드 제공
        if not default_fields:
            default_fields = [
                {"name": "full_name", "type": "Full Name", "constraints": {}, "nullablePercent": 0},
                {"name": "email", "type": "Email Address", "constraints": {}, "nullablePercent": 0},
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
            field_name = field.get("name", "")
            field_type = self.field_type_mapping.get(field_name, field_name.title())
            
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
            
            # nullablePercent 처리
            nullable_percent = 0
            if "nullablePercent" in field:
                nullable_percent = field["nullablePercent"]
            
            transformed_fields.append({
                "name": field_name,
                "type": field_type,
                "constraints": transformed_constraints,
                "nullablePercent": nullable_percent
            })
        
        return {
            "count": result.get("count", len(transformed_fields)),
            "fields": transformed_fields
        }
