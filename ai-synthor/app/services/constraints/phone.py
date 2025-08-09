import re
from .base import ConstraintExtractor

class PhoneExtractor(ConstraintExtractor):
    type_name = "phone"

    def extract(self, text: str) -> dict:
        """
        - 아래 8가지 포맷 중 사용자가 '자연어/기호'로 언급한 첫 번째 포맷만 채택
        - literal(#, (, ), -, 공백, +) 표기 또는 대표적인 설명형 표현을 함께 인식
        - 어떤 포맷도 발견 못 하면 {}
        """
        patterns_for = {
            "###-###-####": [
                r'\#\#\#-\#\#\#-\#\#\#\#',
                r'xxx-xxx-xxxx',
                r'\b3\s*[-–]\s*3\s*[-–]\s*4\b',
                r'(?:하이픈|대시|dash).*(3\s*[-–]\s*3\s*[-–]\s*4)',
                r'\d{3}-\d{3}-\d{4}',
                r'세\s*자리\s*[-–]\s*세\s*자리\s*[-–]\s*네\s*자리',
                r'three\s*digits?\s*dash\s*three\s*digits?\s*dash\s*four\s*digits?',
                r'앞\s*3\s*자리.*뒤\s*4\s*자리.*하이픈',
                r'지역번호\s*[-–]\s*국번\s*[-–]\s*가입자번호',
                r'area\s*code\s*[-–]\s*exchange\s*[-–]\s*number',
                r'일반\s*전화\s*형식',
                r'landline\s*format',
                r'표준\s*전화번호\s*형식',
                r'3\s*자리\s*[-–]\s*3\s*자리\s*[-–]\s*4\s*자리',
                r'(?:hyphen|dash)[-\s]*separated\s*3\s*[-–]\s*3\s*[-–]\s*4',
                r'하이픈\s*구분\s*3\s*[-–]\s*3\s*[-–]\s*4',
            ],
            "(###) ###-####": [
                r'\(\#\#\#\)\s*\#\#\#-\#\#\#\#',
                r'\(xxx\)\s*xxx-xxxx',
                r'(?:괄호|parentheses).*지역|area\s*code',
                r'\(\d{3}\)\s*\d{3}-\d{4}',
                r'괄호\s*안에\s*지역번호',
                r'area\s*code\s*in\s*parentheses',
                r'지역번호\s*괄호\s*표시',
                r'미국\s*스타일\s*전화번호',
                r'US\s*phone\s*format',
                r'북미\s*전화번호\s*형식',
                r'NANP\s*format',
                r'소괄호\s*포함',
                r'괄호\s*지역번호\s*공백\s*3\s*[-–]?\s*4',
                r'area\s*code\s*in\s*\(parentheses\)\s*then\s*3-4',
                r'NANP.*parentheses',
            ],
            "### ### ####": [
                r'\#\#\#\s\#\#\#\s\#\#\#\#',
                r'xxx\sxxx\sxxxx',
                r'(?:공백|스페이스|space).*(3\s*3\s*4)|(?:3\s*3\s*4).*(?:공백|space)',
                r'\d{3}\s+\d{3}\s+\d{4}',
                r'띄어쓰기\s*형식',
                r'space\s*separated',
                r'스페이스\s*구분',
                r'공백\s*구분\s*전화번호',
                r'간격\s*있는\s*전화번호',
                r'세\s*자리씩\s*띄어서',
                r'three\s*digits\s*space\s*three\s*digits\s*space\s*four\s*digits',
                r'깔끔한\s*형식',
                r'공백만\s*사용.*3\s*3\s*4',
                r'without\s*dashes?,?\s*with\s*spaces',
                r'space[-\s]*only\s*format',
            ],
            "+# ### ### ####": [
                r'\+\#\s\#\#\#\s\#\#\#\s\#\#\#\#',
                r'\+x\sxxx\sxxx\sxxxx',
                r'\+\s*\d\s*3\s*3\s*4',
                r'\+\d\s+\d{3}\s+\d{3}\s+\d{4}',
                r'국제\s*전화\s*형식',
                r'international\s*format',
                r'국가코드\s*포함',
                r'country\s*code\s*included',
                r'플러스\s*국가번호',
                r'\+.*국가.*코드',
                r'해외\s*전화\s*형식',
                r'overseas\s*call\s*format',
                r'E\.164\s*format',
                r'ITU\s*standard',
                r'국가코드\s*한\s*자리.*공백.*3\s*3\s*4',
                r'one[-\s]digit\s*country\s*code.*spaces',
            ],
            "+# (###) ###-####": [
                r'\+\#\s\(\#\#\#\)\s\#\#\#-\#\#\#\#',
                r'\+x\s\(xxx\)\sxxx-xxxx',
                r'\+\d\s+\(\d{3}\)\s+\d{3}-\d{4}',
                r'국제.*괄호.*형식',
                r'international.*parentheses',
                r'국가코드.*괄호.*지역번호',
                r'plus.*area.*code.*parentheses',
                r'plus\s*digit\s*country\s*code.*\(area\s*code\).*3-4',
                r'국가코드.*\(\s*지역번호\s*\).*3[-–]4',
            ],
            "+#-###-###-####": [
                r'\+\#-\#\#\#-\#\#\#-\#\#\#\#',
                r'\+x-xxx-xxx-xxxx',
                r'국가코드.*하이픈.*3-3-4',
                r'\+\d-\d{3}-\d{3}-\d{4}',
                r'모든.*구간.*하이픈',
                r'all.*sections.*dash',
                r'국가코드부터.*하이픈',
                r'완전.*하이픈.*형식',
                r'full.*dash.*format',
                r'plus\s*digit\s*then\s*dashes\s*3-3-4',
                r'국가코드\s*뒤.*하이픈.*3[-–]3[-–]4',
            ],
            "#-(###) ###-####": [
                r'\#-\(\#\#\#\)\s\#\#\#-\#\#\#\#',
                r'x-\(xxx\)\sxxx-xxxx',
                r'\d-\(\d{3}\)\s+\d{3}-\d{4}',
                r'국가번호.*하이픈.*괄호',
                r'country.*digit.*dash.*parentheses',
                r'한\s*자리.*국가코드.*하이픈',
                r'single.*digit.*country.*code',
                r'한\s*자리\s*접두.*하이픈.*\(\s*지역번호\s*\).*3-4',
                r'single\s*digit\s*prefix\s*-\s*\(area\s*code\)\s*\d{3}-\d{4}',
                r'\b\d-\(\d{3}\)\s*\d{3}-\d{4}\b',
            ],
            "##########": [
                r'\#\#\#\#\#\#\#\#\#\#',
                r'\b10\s*(?:digits|자리)\b',
                r'(?:하이픈|공백|구분자)\s*없이\s*10\s*자리',
                r'no\s*separators',
                r'\d{10}',
                r'연속\s*숫자\s*10\s*자리',
                r'붙여서\s*쓰기',
                r'continuous\s*digits',
                r'no\s*spaces?\s*no\s*dashes?',
                r'구분자\s*없이',
                r'straight\s*numbers?',
                r'plain\s*digits?',
                r'raw\s*format',
                r'숫자만\s*연속',
                r'compact\s*format',
                r'숫자만\s*10\s*자리',
                r'\bten\s*digits?\s*only\b',
                r'no\s*spaces?,?\s*no\s*dashes?,?\s*10\s*digits',
            ],
        }

        earliest = None
        for fmt, plist in patterns_for.items():
            for pat in plist:
                for m in re.finditer(pat, text, flags=re.IGNORECASE):
                    pos = m.start()
                    if earliest is None or pos < earliest[0]:
                        earliest = (pos, fmt)

        if earliest:
            return {"format": earliest[1]}
        return {}
