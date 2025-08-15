import re
from .base import ConstraintExtractor

class ParagraphsExtractor(ConstraintExtractor):
    type_name = "paragraphs"

    def extract(self, text: str) -> dict:
        c = {}
        
        # 한국어 문단/단락 표현들
        korean_patterns = [
            r'문단', r'단락', r'글의\s*문단', r'본문\s*단락', r'글\s*단락',
            r'글의\s*문단\s*수', r'본문\s*구성\s*단락', r'단락\s*수', r'문단\s*수',
            r'글의\s*각\s*단락', r'본문의\s*각\s*문단', r'글의\s*내용\s*단락',
            r'문단\s*개수', r'문단\s*수는', r'문단\s*개수를', r'문단\s*수를',
            r'문단\s*개수는', r'문단\s*수는', r'문단\s*개수를', r'문단\s*수를',
            r'본문은', r'본문이', r'본문을', r'본문의', r'본문에',
            r'문단으로\s*구성', r'문단으로\s*작성', r'문단을\s*작성', r'문단으로\s*맞춰',
            r'문단으로\s*유지', r'문단으로\s*제한', r'문단으로\s*범위', r'문단으로\s*사이',
            r'문단은\s*총', r'문단\s*수는\s*총', r'문단\s*개수는\s*총',
            r'문단은\s*정확히', r'문단\s*수는\s*정확히', r'문단\s*개수는\s*정확히',
            r'문단을\s*총', r'문단을\s*정확히', r'문단을\s*정확히\s*(\d+)개',
            r'문단은\s*최소', r'문단은\s*최대', r'문단\s*수는\s*최소', r'문단\s*수는\s*최대',
            r'문단\s*개수는\s*최소', r'문단\s*개수는\s*최대', r'본문은\s*최소', r'본문은\s*최대'
        ]
        
        # 영어 문단/단락 표현들
        english_patterns = [
            r'paragraphs?', r'text\s*paragraphs?', r'body\s*paragraphs?',
            r'content\s*paragraphs?', r'sections?', r'blocks?\s*of\s*text',
            r'written\s*paragraphs?', r'textual\s*paragraphs?', r'paragraph\s*units?',
            r'paragraph\s*blocks?', r'each\s*paragraph\s*in\s*the\s*text',
            r'paragraph\s*count', r'number\s*of\s*paragraphs?', r'paragraph\s*structure',
            r'paragraph\s*composition', r'paragraph\s*organization', r'paragraph\s*layout',
            r'your\s*text', r'your\s*writing', r'your\s*answer', r'your\s*content',
            r'the\s*content', r'the\s*text', r'the\s*writing', r'the\s*answer',
            r'composed\s*of', r'contain', r'include', r'have', r'keep', r'limit',
            r'provide', r'write', r'compose', r'organize', r'structure',
            r'your\s*response', r'your\s*response\s*must\s*have', r'your\s*text\s*must\s*have',
            r'your\s*writing\s*must\s*have', r'your\s*answer\s*must\s*have',
            r'provide\s*exactly', r'write\s*exactly', r'compose\s*exactly',
            r'include\s*exactly', r'contain\s*exactly', r'have\s*exactly',
            r'precisely\s*(\d+)', r'exactly\s*(\d+)', r'precisely\s*(\d+)\s*paragraphs?',
            r'exactly\s*(\d+)\s*paragraphs?', r'(\d+)\s*paragraphs?\s*exactly',
            r'(\d+)\s*paragraphs?\s*precisely'
        ]
        
        # 한국어+영어 혼합 표현들
        mixed_patterns = [
            r'문단\s*\(paragraph\)', r'단락\s*\(paragraph\)', r'본문\s*문단\s*\(body\s*paragraph\)',
            r'글\s*단락\s*\(text\s*paragraph\)', r'내용\s*단락\s*\(content\s*paragraph\)',
            r'단락\s*수\s*\(paragraph\s*count\)', r'문단\s*수\s*\(paragraph\s*count\)',
            r'글의\s*각\s*문단\s*\(each\s*paragraph\)', r'단락\s*블록\s*\(paragraph\s*block\)',
            r'글의\s*문단\s*구성\s*\(paragraph\s*structure\)',
            r'문단\s*\(3\s*to\s*5\s*paragraphs?\)', r'문단\s*\(3–5\s*paragraphs?\)',
            r'최소\s*(\d+)\s*\(at\s*least\s*\1\)', r'최대\s*(\d+)\s*\(no\s*more\s*than\s*\1\)',
            r'(\d+)\s*개\s*이상\s*(\d+)\s*개\s*이하\s*\(3–5\s*paragraphs?\)',
            r'(\d+)\s*개\s*이상\s*(\d+)\s*개\s*이하\s*\(at\s*least\s*\1,\s*no\s*more\s*than\s*\2\)',
            r'문단\s*수\s*\(3\s*to\s*5\)', r'문단\s*개수\s*\(3–5\s*paragraphs?\)',
            r'(\d+)\s*개\s*이상\s*(\d+)\s*개\s*이하의\s*문단\s*\(at\s*least\s*\1,\s*no\s*more\s*than\s*\2\)',
            r'(\d+)\s*–\s*(\d+)\s*개의\s*문단', r'(\d+)\s*to\s*(\d+)\s*개의\s*문단'
        ]
        
        # 모든 패턴을 하나로 결합
        all_patterns = korean_patterns + english_patterns + mixed_patterns
        pattern_str = '|'.join(all_patterns)
        
        # 텍스트에서 문단/단락 관련 표현이 있는지 확인
        if re.search(pattern_str, text, re.I):
            # 영어 숫자를 아라비아 숫자로 변환하는 함수
            def word_to_number(word):
                word = word.lower()
                number_map = {
                    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
                    'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20
                }
                return number_map.get(word, None)
            
            # 안전한 숫자 추출 함수
            def safe_extract_number(match):
                if match:
                    groups = match.groups()
                    for group in groups:
                        if group is not None:
                            if group.isdigit():
                                return int(group)
                            else:
                                # 영어 숫자인지 확인
                                num = word_to_number(group)
                                if num is not None:
                                    return num
                return None
            
            # 최소값 패턴
            min_pattern = '|'.join([
                r'최소\s*(\d+)', r'at\s*least\s*(\d+)', r'(\d+)\s*이상', r'(\d+)\s*개\s*이상',
                r'(\d+)\s*개\s*이상의', r'(\d+)\s*개\s*이상으로', r'minimum\s*of\s*(\d+)',
                r'no\s*fewer\s*than\s*(\d+)', r'a\s*minimum\s*of\s*(\d+)',
                r'최소\s*(\d+)\s*개', r'최소\s*(\d+)\s*개의', r'최소\s*(\d+)\s*개로',
                r'(\d+)\s*개\s*이상의\s*문단', r'(\d+)\s*개\s*이상으로\s*작성',
                r'(\d+)\s*개\s*이상\s*포함', r'(\d+)\s*개\s*이상\s*작성',
                r'at\s*least\s*(\d+)\s*paragraphs?', r'at\s*least\s*(\d+)\s*개',
                r'(\d+)\s*개\s*이상\s*\(at\s*least\s*\1\s*paragraphs?\)',
                r'최소\s*(\d+)\s*\(at\s*least\s*\1\s*paragraphs?\)',
                # 영어 숫자 패턴들
                r'at\s*least\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'minimum\s*of\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'no\s*fewer\s*than\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'a\s*minimum\s*of\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?'
            ])
            
            # 최대값 패턴
            max_pattern = '|'.join([
                r'최대\s*(\d+)', r'no\s*more\s*than\s*(\d+)', r'(\d+)\s*이하', r'(\d+)\s*개\s*이하',
                r'(\d+)\s*개\s*이하의', r'(\d+)\s*개\s*이하로', r'maximum\s*of\s*(\d+)',
                r'not\s*more\s*than\s*(\d+)', r'a\s*maximum\s*of\s*(\d+)',
                r'최대\s*(\d+)\s*개', r'최대\s*(\d+)\s*개까지만', r'최대\s*(\d+)\s*개로',
                r'(\d+)\s*개\s*이하로\s*작성', r'(\d+)\s*개\s*이하로\s*제한',
                r'(\d+)\s*개\s*까지만', r'(\d+)\s*개\s*까지만\s*작성',
                r'up\s*to\s*(\d+)', r'limit\s*to\s*(\d+)', r'limit\s*your\s*text\s*to\s*a\s*maximum\s*of\s*(\d+)',
                r'no\s*more\s*than\s*(\d+)\s*paragraphs?', r'no\s*more\s*than\s*(\d+)\s*개',
                r'(\d+)\s*개\s*이하\s*\(no\s*more\s*than\s*\1\s*paragraphs?\)',
                r'최대\s*(\d+)\s*\(no\s*more\s*than\s*\1\s*paragraphs?\)',
                # 영어 숫자 패턴들
                r'no\s*more\s*than\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'maximum\s*of\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'not\s*more\s*than\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'a\s*maximum\s*of\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'up\s*to\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?'
            ])
            
            # 범위 패턴들 (개별적으로 처리)
            range_patterns = [
                # 영어 숫자 패턴들 (우선순위 높음)
                r'between\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*and\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'between\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*and\s*(one|two|three|four|five|six|seven|eight|nine|ten)',
                r'(one|two|three|four|five|six|seven|eight|nine|ten)\s*to\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'(one|two|three|four|five|six|seven|eight|nine|ten)\s*to\s*(one|two|three|four|five|six|seven|eight|nine|ten)',
                r'from\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*to\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'from\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*to\s*(one|two|three|four|five|six|seven|eight|nine|ten)',
                r'in\s*the\s*range\s*of\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*to\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'in\s*the\s*range\s*of\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*to\s*(one|two|three|four|five|six|seven|eight|nine|ten)',
                r'anywhere\s*from\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*to\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'anywhere\s*from\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*to\s*(one|two|three|four|five|six|seven|eight|nine|ten)',
                # 숫자 패턴들
                r'(\d+)\s*~?\s*(\d+)', r'(\d+)\s*-\s*(\d+)', r'(\d+)\s*에서\s*(\d+)',
                r'between\s*(\d+)\s*and\s*(\d+)', r'(\d+)\s*to\s*(\d+)',
                r'(\d+)\s*개\s*~?\s*(\d+)\s*개', r'(\d+)\s*개\s*-\s*(\d+)\s*개',
                r'from\s*(\d+)\s*to\s*(\d+)', r'(\d+)\s*–\s*(\d+)', r'(\d+)\s*사이',
                r'(\d+)\s*개\s*사이', r'(\d+)\s*개\s*에서\s*(\d+)\s*개', r'(\d+)\s*개\s*범위',
                r'in\s*the\s*range\s*of\s*(\d+)\s*to\s*(\d+)', r'anywhere\s*from\s*(\d+)\s*to\s*(\d+)',
                r'(\d+)\s*to\s*(\d+)\s*paragraphs?', r'(\d+)\s*–\s*(\d+)\s*paragraphs?',
                r'from\s*(\d+)\s*to\s*(\d+)\s*paragraphs?', r'(\d+)\s*to\s*(\d+)\s*개의?\s*문단',
                r'(\d+)\s*–\s*(\d+)\s*개의?\s*문단', r'(\d+)\s*to\s*(\d+)\s*개의?\s*문단'
            ]
            
            # 정확한 개수 패턴
            exact_pattern = '|'.join([
                r'(\d+)\s*개', r'(\d+)\s*문단', r'(\d+)\s*단락', r'(\d+)\s*paragraphs?',
                r'(\d+)\s*sections?', r'(\d+)\s*blocks?',
                r'총\s*(\d+)\s*개', r'정확히\s*(\d+)\s*개', r'정확히\s*(\d+)\s*개의',
                r'(\d+)\s*개로\s*작성', r'(\d+)\s*개로\s*제한', r'(\d+)\s*개로\s*구성',
                r'(\d+)\s*개\s*문단', r'(\d+)\s*개\s*단락', r'(\d+)\s*개\s*paragraphs?',
                r'exactly\s*(\d+)', r'precisely\s*(\d+)', r'exactly\s*(\d+)\s*paragraphs?',
                r'precisely\s*(\d+)\s*paragraphs?', r'(\d+)\s*paragraphs?\s*exactly',
                r'(\d+)\s*개\s*\(exactly\s*\1\s*paragraphs?\)', r'정확히\s*(\d+)\s*\(exactly\s*\1\s*paragraphs?\)',
                r'(\d+)\s*paragraphs?로\s*구성', r'(\d+)\s*paragraphs?로\s*작성',
                # 영어 숫자 정확한 개수 패턴들
                r'exactly\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'precisely\s*(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?',
                r'(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?\s*exactly',
                r'(one|two|three|four|five|six|seven|eight|nine|ten)\s*paragraphs?\s*precisely'
            ])
            
            # 최소값 찾기
            m_min = re.search(min_pattern, text, re.I)
            if m_min:
                min_val = safe_extract_number(m_min)
                if min_val is not None:
                    c["at least"] = min_val
            
            # 최대값 찾기
            m_max = re.search(max_pattern, text, re.I)
            if m_max:
                max_val = safe_extract_number(m_max)
                if max_val is not None:
                    c["but no more than"] = max_val
            
            # 범위 찾기 (개별 패턴으로 처리)
            for pattern in range_patterns:
                m_range = re.search(pattern, text, re.I)
                if m_range:
                    groups = m_range.groups()
                    if len(groups) >= 2:
                        # 첫 번째 그룹을 최소값으로, 두 번째 그룹을 최대값으로 처리
                        min_val = None
                        max_val = None
                        
                        if groups[0] is not None:
                            if groups[0].isdigit():
                                min_val = safe_extract_number(re.match(r'(\d+)', groups[0]))
                            else:
                                min_val = word_to_number(groups[0])
                        
                        if groups[1] is not None:
                            if groups[1].isdigit():
                                max_val = safe_extract_number(re.match(r'(\d+)', groups[1]))
                            else:
                                max_val = word_to_number(groups[1])
                        
                        if min_val is not None and max_val is not None:
                            # 최소값과 최대값이 올바른 순서인지 확인
                            if min_val <= max_val:
                                # 범위가 이미 설정되지 않은 경우에만 설정
                                if "at least" not in c:
                                    c["at least"] = min_val
                                if "but no more than" not in c:
                                    c["but no more than"] = max_val
                            else:
                                # 순서가 바뀐 경우 교환
                                if "at least" not in c:
                                    c["at least"] = max_val
                                if "but no more than" not in c:
                                    c["but no more than"] = min_val
                        break  # 첫 번째 매칭된 패턴만 사용
            
            # 정확한 개수 찾기 (최소/최대가 설정되지 않은 경우)
            if "at least" not in c and "but no more than" not in c:
                m_exact = re.search(exact_pattern, text, re.I)
                if m_exact:
                    exact_val = safe_extract_number(m_exact)
                    if exact_val is not None:
                        c["at least"] = exact_val
                        c["but no more than"] = exact_val
        
        return c
