import re
from typing import Dict, Any, Optional


class EmailAddressConstraint:
    """이메일 주소 제약 조건 처리기"""
    
    type_name = "email_address"
    
    def __init__(self):
        # 지원하는 이메일 도메인 목록
        self.supported_domains = {
            "naver.com", "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "daum.net", "nate.com", "hanmail.net", "icloud.com", "protonmail.com",
            # 학교 메일 도메인
            "sejong.ac.kr", "snu.ac.kr", "korea.ac.kr", "yonsei.ac.kr", "kaist.ac.kr",
            "postech.ac.kr", "unist.ac.kr", "khu.ac.kr", "hanyang.ac.kr", "ewha.ac.kr",
            "inha.ac.kr", "pusan.ac.kr", "knu.ac.kr", "gist.ac.kr", "dgist.ac.kr",
            "cau.ac.kr", "sogang.ac.kr", "seoultech.ac.kr", "kookmin.ac.kr", "sookmyung.ac.kr",
            "ajou.ac.kr", "chosun.ac.kr", "kmu.ac.kr", "dankook.ac.kr"
        }
        
        # 한글 도메인명 → 영문 도메인명 매핑
        self.korean_domain_mapping = {
            "네이버": "naver.com",
            "구글": "gmail.com",
            "지메일": "gmail.com",
            "야후": "yahoo.com",
            "핫메일": "hotmail.com",
            "아웃룩": "outlook.com",
            "다음": "daum.net",
            "네이트": "nate.com",
            "한메일": "hanmail.net",
            "아이클라우드": "icloud.com",
            "프로톤메일": "protonmail.com",
            # 학교 메일 도메인 매핑
            "세종대": "sejong.ac.kr",
            "세종대학교": "sejong.ac.kr",
            "서울대": "snu.ac.kr",
            "서울대학교": "snu.ac.kr",
            "고려대": "korea.ac.kr",
            "고려대학교": "korea.ac.kr",
            "연세대": "yonsei.ac.kr",
            "연세대학교": "yonsei.ac.kr",
            "카이스트": "kaist.ac.kr",
            "한국과학기술원": "kaist.ac.kr",
            "포항공대": "postech.ac.kr",
            "포항공과대": "postech.ac.kr",
            "포항공과대학교": "postech.ac.kr",
            "울산과기원": "unist.ac.kr",
            "울산과학기술원": "unist.ac.kr",
            "경희대": "khu.ac.kr",
            "경희대학교": "khu.ac.kr",
            "한양대": "hanyang.ac.kr",
            "한양대학교": "hanyang.ac.kr",
            "이화여대": "ewha.ac.kr",
            "이화여자대": "ewha.ac.kr",
            "이화여자대학교": "ewha.ac.kr",
            "인하대": "inha.ac.kr",
            "인하대학교": "inha.ac.kr",
            "부산대": "pusan.ac.kr",
            "부산대학교": "pusan.ac.kr",
            "경북대": "knu.ac.kr",
            "경북대학교": "knu.ac.kr",
            "광주과기원": "gist.ac.kr",
            "광주과학기술원": "gist.ac.kr",
            "대구경북과기원": "dgist.ac.kr",
            "대구경북과학기술원": "dgist.ac.kr",
            "중앙대": "cau.ac.kr",
            "중앙대학교": "cau.ac.kr",
            "서강대": "sogang.ac.kr",
            "서강대학교": "sogang.ac.kr",
            "서울과기대": "seoultech.ac.kr",
            "서울과학기술대": "seoultech.ac.kr",
            "국민대": "kookmin.ac.kr",
            "국민대학교": "kookmin.ac.kr",
            "숙명여대": "sookmyung.ac.kr",
            "숙명여자대": "sookmyung.ac.kr",
            "아주대": "ajou.ac.kr",
            "아주대학교": "ajou.ac.kr",
            "조선대": "chosun.ac.kr",
            "조선대학교": "chosun.ac.kr",
            "계명대": "kmu.ac.kr",
            "계명대학교": "kmu.ac.kr",
            "단국대": "dankook.ac.kr",
            "단국대학교": "dankook.ac.kr"
        }
    
    def validate_constraints(self, constraints: Dict[str, Any]) -> bool:
        """제약 조건 유효성 검사"""
        if not constraints:
            return True
            
        # domain 제약 조건 검사
        if "domain" in constraints:
            domain = constraints["domain"]
            if not isinstance(domain, str):
                return False
            # 도메인 형식 검사 (기본적인 이메일 도메인 형식)
            if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
                return False
                
        # domains 제약 조건 검사 (여러 도메인 중 하나)
        if "domains" in constraints:
            domains = constraints["domains"]
            if not isinstance(domains, list):
                return False
            if not all(isinstance(d, str) and re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', d) for d in domains):
                return False
                
        # format 제약 조건 검사
        if "format" in constraints:
            format_str = constraints["format"]
            if not isinstance(format_str, str):
                return False
            # 기본적인 이메일 형식 검사
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', format_str):
                return False
                
        return True
    
    def apply_constraints(self, value: str, constraints: Dict[str, Any]) -> str:
        """제약 조건을 적용하여 이메일 주소 생성/수정"""
        if not constraints:
            return value
            
        # domain 제약 조건 적용
        if "domain" in constraints:
            domain = constraints["domain"]
            # 기존 이메일에서 로컬 부분만 추출하고 새로운 도메인 적용
            local_part = value.split('@')[0] if '@' in value else value
            return f"{local_part}@{domain}"
            
        # domains 제약 조건 적용 (첫 번째 도메인 사용)
        if "domains" in constraints:
            domains = constraints["domains"]
            if domains:
                domain = domains[0]
                local_part = value.split('@')[0] if '@' in value else value
                return f"{local_part}@{domain}"
                
        # format 제약 조건 적용
        if "format" in constraints:
            format_str = constraints["format"]
            # 형식에 맞게 이메일 주소 수정
            # 여기서는 간단히 형식 검사만 수행
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                # 기본 형식으로 수정
                return f"user@example.com"
                
        return value
    
    def get_supported_constraints(self) -> Dict[str, str]:
        """지원하는 제약 조건 목록 반환"""
        return {
            "domain": "특정 도메인으로 제한 (예: 'naver.com')",
            "domains": "여러 도메인 중 하나로 제한 (예: ['naver.com', 'gmail.com'])",
            "format": "이메일 형식 제한 (예: 'local@domain.com')"
        }
    
    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """텍스트에서 이메일 제약 조건 추출 (registry에서 호출되는 메서드)"""
        return self.parse_korean_constraints(text)
    
    def parse_korean_constraints(self, text: str) -> Optional[Dict[str, Any]]:
        """한글 텍스트에서 이메일 제약 조건 파싱"""
        constraints = {}
        
        # 1. 영문 도메인 직접 매칭 (예: "naver.com으로요", "To naver.com, please")
        for domain in self.supported_domains:
            # 한국어 패턴
            if f"{domain}으로요" in text or f"{domain}로요" in text:
                constraints["domain"] = domain
                return constraints
            # 영어 패턴
            if f"To {domain}" in text or f"to {domain}" in text:
                constraints["domain"] = domain
                return constraints
        
        # 2. 한글 도메인명 매칭 (확장된 패턴)
        for kor_domain, eng_domain in self.korean_domain_mapping.items():
            # 한국어 패턴들
            korean_patterns = [
                f"{kor_domain}만", f"{kor_domain} 이메일", f"{kor_domain} 메일", 
                f"{kor_domain} 계정 이메일", f"{kor_domain} 메일 주소", f"{kor_domain} 이메일",
                f"{kor_domain} 도메인 이메일", f"{kor_domain} 계정 쓰고 계신 이메일",
                f"{kor_domain} 계정 메일", f"{kor_domain} 아이디 이메일", f"{kor_domain} 도메인 메일",
                f"{kor_domain}로요", f"{kor_domain}으로요", f"{kor_domain} 주소로요"
            ]
            
            # 영어 패턴들 (도메인별로 매핑)
            english_patterns = []
            if kor_domain == "네이버":
                english_patterns = [
                    f"Naver email", f"Naver account email", f"Naver mail address",
                    f"Naver email address", f"Naver domain email", f"Naver account mail",
                    f"Naver ID email", f"Naver domain mail"
                ]
            elif kor_domain == "지메일" or kor_domain == "구글":
                english_patterns = [
                    f"Gmail email", f"Gmail account email", f"Gmail mail address",
                    f"Gmail email address", f"Gmail domain email", f"Gmail account mail",
                    f"Gmail ID email", f"Gmail domain mail"
                ]
            elif kor_domain == "야후":
                english_patterns = [
                    f"Yahoo email", f"Yahoo account email", f"Yahoo mail address",
                    f"Yahoo email address", f"Yahoo domain email", f"Yahoo account mail",
                    f"Yahoo ID email", f"Yahoo domain mail"
                ]
            elif kor_domain == "핫메일":
                english_patterns = [
                    f"Hotmail email", f"Hotmail account email", f"Hotmail mail address",
                    f"Hotmail email address", f"Hotmail domain email", f"Hotmail account mail",
                    f"Hotmail ID email", f"Hotmail domain mail"
                ]
            elif kor_domain == "아웃룩":
                english_patterns = [
                    f"Outlook email", f"Outlook account email", f"Outlook mail address",
                    f"Outlook email address", f"Outlook domain email", f"Outlook account mail",
                    f"Outlook ID email", f"Outlook domain mail"
                ]
            elif kor_domain == "다음":
                english_patterns = [
                    f"Daum email", f"Daum account email", f"Daum mail address",
                    f"Daum email address", f"Daum domain email", f"Daum account mail",
                    f"Daum ID email", f"Daum domain mail"
                ]
            elif kor_domain == "네이트":
                english_patterns = [
                    f"Nate email", f"Nate account email", f"Nate mail address",
                    f"Nate email address", f"Nate domain email", f"Nate account mail",
                    f"Nate ID email", f"Nate domain mail"
                ]
            elif kor_domain == "한메일":
                english_patterns = [
                    f"Hanmail email", f"Hanmail account email", f"Hanmail mail address",
                    f"Hanmail email address", f"Hanmail domain email", f"Hanmail account mail",
                    f"Hanmail ID email", f"Hanmail domain mail"
                ]
            elif kor_domain == "아이클라우드":
                english_patterns = [
                    f"iCloud email", f"iCloud account email", f"iCloud mail address",
                    f"iCloud email address", f"iCloud domain email", f"iCloud account mail",
                    f"iCloud ID email", f"iCloud domain mail"
                ]
            elif kor_domain == "프로톤메일":
                english_patterns = [
                    f"ProtonMail email", f"ProtonMail account email", f"ProtonMail mail address",
                    f"ProtonMail email address", f"ProtonMail domain email", f"ProtonMail account mail",
                    f"ProtonMail ID email", f"ProtonMail domain mail"
                ]
            # 학교 메일 도메인들
            elif kor_domain in ["세종대", "세종대학교", "서울대", "서울대학교", "고려대", "고려대학교", 
                               "연세대", "연세대학교", "카이스트", "한국과학기술원", "포항공대", "포항공과대", "포항공과대학교",
                               "울산과기원", "울산과학기술원", "경희대", "경희대학교", "한양대", "한양대학교", 
                               "이화여대", "이화여자대", "이화여자대학교", "인하대", "인하대학교", "부산대", "부산대학교", 
                               "경북대", "경북대학교", "광주과기원", "광주과학기술원", "대구경북과기원", "대구경북과학기술원", 
                               "중앙대", "중앙대학교", "서강대", "서강대학교", "서울과기대", "서울과학기술대",
                               "국민대", "국민대학교", "숙명여대", "숙명여자대", "아주대", "아주대학교", 
                               "조선대", "조선대학교", "계명대", "계명대학교", "단국대", "단국대학교"]:
                # 학교 메일은 영어 패턴이 제한적이므로 기본 패턴만 사용
                english_patterns = []
            
            # 혼합 패턴들
            mixed_patterns = [
                f"{kor_domain} email", f"{kor_domain} address", f"{kor_domain} domain email",
                f"{kor_domain} account mail", f"{kor_domain} account email", f"{kor_domain} ID email", f"{kor_domain} 도메인 mail",
                f"{kor_domain} 계정 email", f"{kor_domain} 계정 쓰고 계신 email", f"{kor_domain} 주소"
            ]
            
            # 모든 패턴 검사
            all_patterns = korean_patterns + english_patterns + mixed_patterns
            for pattern in all_patterns:
                if pattern in text:
                    constraints["domain"] = eng_domain
                    return constraints
        
        # 3. 임의의 도메인 패턴 매칭 (예: "sju.com 메일", "sju.com 형식")
        import re
        domain_pattern = r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s*(메일|형식|이메일|만|으로요|로요)'
        domain_match = re.search(domain_pattern, text)
        if domain_match:
            domain = domain_match.group(1)
            constraints["domain"] = domain
            return constraints
        
        # 4. 영어 표현 패턴 매칭
        english_domain_pattern = r'(To|to)\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        english_match = re.search(english_domain_pattern, text)
        if english_match:
            domain = english_match.group(2)
            constraints["domain"] = domain
            return constraints
        
        # 5. 긴 영어 패턴 매칭 (예: "To the email you use for your Naver account, please.")
        long_english_patterns = {
            "To the email you use for your Naver account, please.": "naver.com",
            "To the email you use for your Gmail account, please.": "gmail.com",
            "To the email you use for your Yahoo account, please.": "yahoo.com",
            "To the email you use for your Hotmail account, please.": "hotmail.com",
            "To the email you use for your Outlook account, please.": "outlook.com",
            "To the email you use for your Daum account, please.": "daum.net",
            "To the email you use for your Nate account, please.": "nate.com",
            "To the email you use for your Hanmail account, please.": "hanmail.net",
            "To the email you use for your iCloud account, please.": "icloud.com",
            "To the email you use for your ProtonMail account, please.": "protonmail.com"
        }
        
        for pattern, domain in long_english_patterns.items():
            if pattern in text:
                constraints["domain"] = domain
                return constraints
        
        # 6. @도메인형 패턴 매칭 (사용자가 임의의 도메인을 요청하는 경우)
        # 한국어 패턴: @도메인형으로, @도메인형로, @도메인형으로요, @도메인형로요 등
        at_domain_korean_pattern = r'@([a-zA-Z0-9.-]+)(형으로|형로|형으로요|형로요|형으로는|형로는|형으로만|형로만|형으로부터|형로부터|형으로 해주세요|형로 해주세요|형으로 부탁드립니다|형로 부탁드립니다|형으로 해주시면 됩니다|형로 해주시면 됩니다|형으로 작성해주세요|형로 작성해주세요|형 메일로|형 메일로요|형 메일 주소로|형 이메일로|형 이메일로요|형 계정으로|형 계정 이메일로)'
        at_domain_korean_match = re.search(at_domain_korean_pattern, text)
        if at_domain_korean_match:
            domain = at_domain_korean_match.group(1)
            constraints["domain"] = domain
            return constraints
        
        # 영어 패턴: @도메인형 email format, @도메인형 email, @도메인형 address 등
        at_domain_english_pattern = r'@([a-zA-Z0-9.-]+)(\s+email|\s+address|\s+format|\s+domain\s+email|\s+account\s+email)'
        at_domain_english_match = re.search(at_domain_english_pattern, text)
        if at_domain_english_match:
            domain = at_domain_english_match.group(1)
            constraints["domain"] = domain
            return constraints
        
        # 혼합 패턴: @도메인형으로, please. / Please, @도메인형 메일로요. 등
        at_domain_mixed_pattern = r'@([a-zA-Z0-9.-]+)(\s*,\s*please|\s*로요\s*,\s*please|\s*형으로\s*,\s*please|\s*형로요\s*,\s*please)'
        at_domain_mixed_match = re.search(at_domain_mixed_pattern, text)
        if at_domain_mixed_match:
            domain = at_domain_mixed_match.group(1)
            constraints["domain"] = domain
            return constraints
        
        # 간단한 @도메인형 패턴 (조사나 형식 지정이 없는 경우) - 더 유연하게 수정
        simple_at_domain_pattern = r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        simple_at_domain_match = re.search(simple_at_domain_pattern, text)
        if simple_at_domain_match:
            domain = simple_at_domain_match.group(1)
            constraints["domain"] = domain
            return constraints
                
        # 5. 여러 도메인 제약 조건 파싱 (예: "네이버나 구글 이메일", "naver.com 또는 daum.net")
        domains = []
        
        # 한국어 도메인 매핑에서 찾기
        for kor_domain, eng_domain in self.korean_domain_mapping.items():
            if kor_domain in text:
                domains.append(eng_domain)
        
        # 영어 도메인 패턴에서 찾기 (예: "naver.com 또는 daum.net")
        english_domain_patterns = [
            r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s*(?:또는|or)\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s*,\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        for pattern in english_domain_patterns:
            match = re.search(pattern, text)
            if match:
                domains.extend(match.groups())
                
        if len(domains) > 1:
            constraints["domain"] = domains
            return constraints
            
        return None if not constraints else constraints
