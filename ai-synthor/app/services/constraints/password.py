import re
from .base import ConstraintExtractor

class PasswordExtractor(ConstraintExtractor):
    type_name = "password"

    def extract(self, text: str) -> dict:
        c = {}

        def pick(m):
            if not m:
                return None
            # 포함 패턴의 경우 그룹이 비어있으면 기본값 1 반환
            groups = list(filter(None, m.groups()))
            if groups:
                # 숫자인지 확인 후 변환
                for group in groups:
                    if group.isdigit():
                        return int(group)
                # 숫자가 없으면 포함 패턴으로 간주하고 기본값 1 반환
                return 1
            else:
                # 포함 패턴으로 매치된 경우 기본값 1 반환
                return 1

        def pick_range(m):
            """범위 패턴 (예: 6자리에서 16자리)에서 두 번째 숫자를 반환"""
            if not m:
                return None
            groups = list(filter(None, m.groups()))
            if len(groups) >= 2:
                # 두 번째 숫자를 max_length로 사용
                for group in groups[1:]:
                    if group.isdigit():
                        return int(group)
            return None

        def pick_min_range(m):
            """범위 패턴 (예: 6자리에서 16자리)에서 첫 번째 숫자를 반환"""
            if not m:
                return None
            groups = list(filter(None, m.groups()))
            if len(groups) >= 2:
                # 첫 번째 숫자를 min_length로 사용
                for group in groups[:1]:
                    if group.isdigit():
                        return int(group)
            return None

        #최소 길이 (숫자 명시형만, ≥N)
        m_min = re.search(
            r'(\d+)\s*(?:자|글자|자리)\s*이상\s*(\d+)\s*(?:자|글자|자리)\s*이하|'  # 8자 이상 20자 이하 (첫 번째 숫자)
            r'(\d+)\s*(?:자|글자|자리)\s*에서\s*(\d+)\s*(?:자|글자|자리)|'  # 6자리에서 16자리 (첫 번째 숫자)
            r'(?:최소|적어도)\s*(\d+)\s*(?:자|글자|자리)|'            # 최소 10자
            r'(\d+)\s*(?:자|글자|자리)\s*(?:이상)|'                  # 10자 이상
            r'최소\s*길이(?:가)?[:\s]*(\d+)|길이\s*최소[:\s]*(\d+)|'  # 최소 길이(가) 10 / 길이 최소 10
            r'최소\s*length\s*(\d+)\s*이상|'                        # 최소 length 10 이상
            r'length\s*는\s*(\d+)\s*이상|'                          # length는 10 이상
            r'min(?:imum)?(?:\s*length)?[:\s]*(\d+)|'               # minimum length: 10
            r'minimum_length\s*(\d+)|'                              # minimum_length 10
            r'min(?:imum)?\s*length\s*of\s*(\d+)|'                  # minimum length of 10
            r'length\s*(?:at\s*least|>=)\s*(\d+)|'                  # length at least 10 / length >= 10
            r'length\s*must\s*be\s*(\d+)\s*or\s*more|'              # length must be 10 or more
            r'(\d+)\s*or\s*more\s*(?:chars?|characters?)|'          # 10 or more characters
            r'(\d+)\s*or\s*longer|'                                 # 10 or longer
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*(?:chars?|characters?|letters?)|'
            r'min[:\s]*(\d+)\s*(?:chars?|characters?)|'             # min 10 chars
            r'(\d+)\s*(?:자|글자|자리)\s*(?:이상|또는\s*더\s*많이)|'  # 10자 이상 또는 더 많이
            r'(\d+)\s*(?:chars?|characters?)\s*(?:or\s*more|or\s*longer)|'  # 10 characters or more
            r'(\d+)\s*(?:자|글자|자리)\s*이상|'                      # 10자 이상 (다른 패턴)
            r'(\d+)\s*(?:chars?|characters?)\s*이상',               # 10 characters 이상
            text, re.I
        )

        #최대 길이 (숫자 명시형만, ≤N)
        m_max = re.search(
            r'(?:최대|많아야)\s*(\d+)\s*(?:자|글자|자리)|'            # 최대 20자
            r'(\d+)\s*(?:자|글자|자리)\s*(?:이하)|'                  # 20자 이하
            r'최대\s*길이(?:가)?[:\s]*(\d+)|길이\s*최대[:\s]*(\d+)|'  # 최대 길이(가) 20 / 길이 최대 20
            r'최대\s*length\s*(\d+)\s*이하|'                        # 최대 length 20 이하
            r'length\s*는\s*(\d+)\s*이하|'                          # length는 20 이하
            r'max(?:imum)?(?:\s*length)?[:\s]*(\d+)|'               # maximum length: 20
            r'max(?:imum)?\s*length\s*of\s*(\d+)|'                  # maximum length of 20
            r'length\s*(?:at\s*most|<=)\s*(\d+)|'                   # length at most 20 / length <= 20
            r'length\s*must\s*be\s*(\d+)\s*or\s*less|'              # length must be 20 or less
            r'(\d+)\s*or\s*less\s*(?:chars?|characters?)|'          # 20 or less characters
            r'(\d+)\s*or\s*shorter|'                                # 20 or shorter
            r'(?:at\s*most|no\s*more\s*than)\s*(\d+)\s*(?:chars?|characters?|letters?)|'
            r'max[:\s]*(\d+)\s*(?:chars?|characters?)|'             # max 20 chars
            r'(\d+)\s*(?:자|글자|자리)\s*(?:이하|또는\s*더\s*적게)|'  # 20자 이하 또는 더 적게
            r'(\d+)\s*(?:chars?|characters?)\s*(?:or\s*less|or\s*shorter)|'  # 20 characters or less
            r'(\d+)\s*(?:자|글자|자리)\s*이하|'                      # 20자 이하 (다른 패턴)
            r'(\d+)\s*(?:chars?|characters?)\s*이하|'               # 20 characters 이하
            r'(\d+)\s*(?:자|글자|자리)\s*에서\s*(\d+)\s*(?:자|글자|자리)|'  # 6자리에서 16자리
            r'(\d+)\s*(?:자|글자|자리)\s*이상\s*(\d+)\s*(?:자|글자|자리)\s*이하',  # 8자 이상 20자 이하
            text, re.I
        )

        #대문자 개수 (숫자 명시형만, ≥N)
        m_up  = re.search(
            r'대문자\s*(\d+)\s*(?:개|자)|'                          # 대문자 2개
            r'(?:대문자|영문\s*대문자)\s*(\d+)\s*개\s*이상|'         # 대문자 2개 이상
            r'대문자\s*최소[:\s]*(\d+)|'                            # 대문자 최소 2
            r'upper(?:case)?[:\s]*:?[\s]*(\d+)|'                    # uppercase: 2
            r'uppercase\s*>=\s*(\d+)|'                              # uppercase >= 2
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*uppercase(?:\s*letters?)?|'
            r'capitals?[:\s]*:?[\s]*(\d+)|'                         # capital: 2
            r'at\s*least\s*(\d+)\s*capitals?|'                      # at least 1 capital
            r'(?:with|포함)\s*(?:uppercase|대문자)|'                 # with uppercase
            r'(?:uppercase|대문자)(?:\s*and\s*(?:lowercase|소문자|numbers?|숫자|symbols?|특수문자))?|'  # uppercase (with and)
            r'(대문자.*?포함.*?(?:되어야|해야)|포함.*?대문자)|'        # 대문자 포함되어야 해
            r'(?:대문자|uppercase).*?포함.*?(?:되어야|해야|필수)|'    # 대문자 포함되어야 해
            r'포함.*?(?:대문자|uppercase).*?(?:되어야|해야|필수)|'    # 포함 대문자 되어야 해
            r'(?:대문자|uppercase).*?(?:include|including|contain)|' # 대문자 include/contain
            r'(?:include|including|contain).*?(?:대문자|uppercase)|' # include 대문자
            r'(?:대문자|uppercase).*?(?:and|또는|그리고)|'           # 대문자 and/또는
            r'(?:대문자|uppercase).*?포함|포함.*?(?:대문자|uppercase)|' # 대문자 포함 / 포함 대문자
            r'(?:대문자|uppercase).*?(?:들어가야|들어가야\s*합니다|들어가야\s*함)|'  # 대문자 들어가야 합니다
            r'(?:들어가야|들어가야\s*합니다|들어가야\s*함).*?(?:대문자|uppercase)|'  # 들어가야 대문자
            r'(?:대문자|uppercase)\s*\+\s*(?:소문자|lowercase)|'       # uppercase + lowercase
            r'(?:소문자|lowercase)\s*\+\s*(?:대문자|uppercase)|'       # lowercase + uppercase
            r'(?:대문자|uppercase)\s*\+\s*(?:숫자|number)|'            # uppercase + number
            r'(?:숫자|number)\s*\+\s*(?:대문자|uppercase)|'            # number + uppercase
            r'(?:대문자|uppercase)\s*\+\s*(?:symbol|특수문자|특문|기호)|' # uppercase + symbol
            r'(?:symbol|특수문자|특문|기호)\s*\+\s*(?:대문자|uppercase)|' # symbol + uppercase
            r'(?:대문자|uppercase).*?(?:1개\s*이상|one\s*or\s*more)|'  # 대문자 1개 이상
            r'(?:대문자|uppercase).*?(?:필수|required|must)|'          # 대문자 필수
            r'(?:대문자|uppercase).*?(?:꼭|반드시|must|should)',       # 대문자 꼭/반드시
            text, re.I
        )

        #소문자 개수 (숫자 명시형만, ≥N)
        m_low = re.search(
            r'소문자\s*(\d+)\s*(?:개|자)|'
            r'(?:소문자|영문\s*소문자)\s*(\d+)\s*개\s*이상|'
            r'소문자\s*최소[:\s]*(\d+)|'
            r'lower(?:case)?[:\s]*:?[\s]*(\d+)|'
            r'lowercase\s*>=\s*(\d+)|'
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*lowercase(?:\s*letters?)?|'
            r'(?:with|포함)\s*(?:lowercase|소문자)|'                   # with lowercase
            r'(?:lowercase|소문자)(?:\s*and\s*(?:uppercase|대문자|numbers?|숫자|symbols?|특수문자))?|'  # lowercase (with and)
            r'(소문자.*?포함.*?(?:되어야|해야)|포함.*?소문자)|'
            r'(?:소문자|lowercase).*?포함.*?(?:되어야|해야|필수)|'    # 소문자 포함되어야 해
            r'포함.*?(?:소문자|lowercase).*?(?:되어야|해야|필수)|'    # 포함 소문자 되어야 해
            r'(?:소문자|lowercase).*?(?:include|including|contain)|' # 소문자 include/contain
            r'(?:include|including|contain).*?(?:소문자|lowercase)|' # include 소문자
            r'(?:소문자|lowercase).*?(?:and|또는|그리고)|'           # 소문자 and/또는
            r'(?:소문자|lowercase).*?포함|포함.*?(?:소문자|lowercase)|' # 소문자 포함 / 포함 소문자
            r'(?:소문자|lowercase).*?(?:들어가야|들어가야\s*합니다|들어가야\s*함)|'  # 소문자 들어가야 합니다
            r'(?:들어가야|들어가야\s*합니다|들어가야\s*함).*?(?:소문자|lowercase)|'  # 들어가야 소문자
            r'(?:소문자|lowercase)\s*\+\s*(?:숫자|number)|'            # lowercase + number
            r'(?:숫자|number)\s*\+\s*(?:소문자|lowercase)|'            # number + lowercase
            r'(?:소문자|lowercase)\s*\+\s*(?:symbol|특수문자|특문|기호)|' # lowercase + symbol
            r'(?:symbol|특수문자|특문|기호)\s*\+\s*(?:소문자|lowercase)|' # symbol + lowercase
            r'(?:소문자|lowercase).*?(?:1개\s*이상|one\s*or\s*more)|'  # 소문자 1개 이상
            r'(?:소문자|lowercase).*?(?:필수|required|must)|'          # 소문자 필수
            r'(?:소문자|lowercase).*?(?:꼭|반드시|must|should)',       # 소문자 꼭/반드시
            text, re.I
        )

        #숫자/디지트 개수 (숫자 명시형만, ≥N)
        m_num = re.search(
            r'(?:숫자|수자)\s*(\d+)\s*(?:개|자)|'
            r'(?:숫자|수자)\s*(\d+)\s*개\s*이상|'
            r'숫자\s*최소[:\s]*(\d+)|'
            r'numbers?[:\s]*:?[\s]*(\d+)|'
            r'digits?[:\s]*:?[\s]*(\d+)|'
            r'numerals?[:\s]*:?[\s]*(\d+)|'                         #numeral: 2
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*(?:digits?|numbers?|numerals?)|'
            r'(?:with|포함)\s*(?:numbers?|숫자)|'                     # with numbers
            r'(?:numbers?|숫자)(?:\s*and\s*(?:uppercase|대문자|lowercase|소문자|symbols?|특수문자))?|'  # numbers (with and)
            r'(숫자.*?포함.*?(?:되어야|해야)|포함.*?숫자)|'              # 숫자 포함되어야 해
            r'(?:숫자|number).*?포함.*?(?:되어야|해야|필수)|'          # 숫자 포함되어야 해
            r'포함.*?(?:숫자|number).*?(?:되어야|해야|필수)|'          # 포함 숫자 되어야 해
            r'(?:숫자|number).*?(?:1개\s*이상|one\s*or\s*more)|'      # 숫자 1개 이상
            r'(?:숫자|number).*?(?:필수|required|must)|'              # 숫자 필수
            r'(?:숫자|number).*?(?:꼭|반드시|must|should)|'           # 숫자 꼭/반드시
            r'(?:숫자|number).*?(?:include|including|contain)|'       # 숫자 include/contain
            r'(?:include|including|contain).*?(?:숫자|number)|'       # include 숫자
            r'(?:숫자|number).*?(?:and|또는|그리고)|'                 # 숫자 and/또는
            r'(?:숫자|number).*?포함|포함.*?(?:숫자|number)|'         # 숫자 포함 / 포함 숫자
            r'(?:숫자|number).*?(?:들어가야|들어가야\s*합니다|들어가야\s*함)|'  # 숫자 들어가야 합니다
            r'(?:들어가야|들어가야\s*합니다|들어가야\s*함).*?(?:숫자|number)|'  # 들어가야 숫자
            r'(?:숫자|number)\s*\+\s*(?:symbol|특수문자|특문|기호)|'   # number + symbol
            r'(?:symbol|특수문자|특문|기호)\s*\+\s*(?:숫자|number)',   # symbol + number
            text, re.I
        )

        #특수문자/기호 개수 (숫자 명시형만, ≥N)
        m_sym = re.search(
            r'(?:특수문자|특문|기호|특수\s*기호)\s*(\d+)\s*(?:개|자)|'
            r'(?:특수문자|특문|기호|특수\s*기호)\s*(\d+)\s*개\s*이상|'
            r'(?:특수문자|특문|기호)\s*최소[:\s]*(\d+)|'
            r'special\s*(?:chars?|characters?)[:\s]*:?[\s]*(\d+)|'  #special characters: 2
            r'symbols?[:\s]*:?[\s]*(\d+)|'
            r'punctuation[:\s]*:?[\s]*(\d+)|'
            r'non[- ]?alphanumeric[:\s]*:?[\s]*(\d+)|'
            r'(?:at\s*least|no\s*less\s*than)\s*(\d+)\s*(?:symbols?|punctuation|special\s*(?:chars?|characters?))|'
            r'(?:with|포함)\s*(?:symbols?|특수문자|특문|기호)|'       # with symbols
            r'(?:symbols?|특수문자|특문|기호)(?:\s*and\s*(?:uppercase|대문자|lowercase|소문자|numbers?|숫자))?|'  # symbols (with and)
            r'((?:특수.*?문자|특문|기호).*?포함.*?(?:되어야|해야)|포함.*?(?:특수.*?문자|특문|기호))|'  # 특수 문자 포함되어야 해
            r'(?:특수.*?문자|특문|기호|special\s*char|symbol).*?포함.*?(?:되어야|해야|필수)|'  # 특수문자 포함되어야 해
            r'포함.*?(?:특수.*?문자|특문|기호|special\s*char|symbol).*?(?:되어야|해야|필수)|'  # 포함 특수문자 되어야 해
            r'(?:특수.*?문자|특문|기호|special\s*char|symbol).*?(?:1개\s*이상|one\s*or\s*more)|'  # 특수문자 1개 이상
            r'(?:특수.*?문자|특문|기호|special\s*char|symbol).*?(?:필수|required|must)|'  # 특수문자 필수
            r'(?:특수.*?문자|특문|기호|special\s*char|symbol).*?(?:꼭|반드시|must|should)|'  # 특수문자 꼭/반드시
            r'(?:특수.*?문자|특문|기호|special\s*char|symbol).*?(?:include|including|contain)|'  # 특수문자 include/contain
            r'(?:include|including|contain).*?(?:특수.*?문자|특문|기호|special\s*char|symbol)|'  # include 특수문자
            r'(?:특수.*?문자|특문|기호|special\s*char|symbol).*?(?:and|또는|그리고)|'  # 특수문자 and/또는
            r'(?:특수.*?문자|특문|기호|special\s*char|symbol).*?포함|포함.*?(?:특수.*?문자|특문|기호|special\s*char|symbol)|'  # 특수문자 포함 / 포함 특수문자
            r'(?:특수.*?문자|특문|기호|special\s*char|symbol).*?(?:들어가야|들어가야\s*합니다|들어가야\s*함)|'  # 특수문자 들어가야 합니다
            r'(?:들어가야|들어가야\s*합니다|들어가야\s*함).*?(?:특수.*?문자|특문|기호|special\s*char|symbol)|'  # 들어가야 특수문자
            r'(?:at\s*least|no\s*less\s*than)\s*(?:one|1)\s*(?:special\s*char|special\s*character|symbol)|'  # at least one special character
            r'(?:special\s*char|special\s*character|symbol).*?(?:at\s*least|no\s*less\s*than)\s*(?:one|1)|'  # special character at least one
            r'(?:special\s*char|special\s*character|symbol)',  # special character (단순 포함)
            text, re.I
        )

        categories = {
            "minimum_length": m_min,
            "max_length": m_max,
            "upper": m_up, 
            "lower": m_low,
            "numbers": m_num,
            "symbols": m_sym
        }
        
        for category, match in categories.items():
            if match:
                if category == "max_length":
                    val = pick_range(match)
                elif category == "minimum_length":
                    # 범위 패턴인 경우에만 pick_min_range 사용
                    groups = list(filter(None, match.groups()))
                    if len(groups) >= 2:
                        val = pick_min_range(match)  # 첫 번째 숫자를 minimum_length로 사용
                    else:
                        val = pick(match)  # 단일 숫자인 경우
                else:
                    val = pick(match)
                if val is not None:
                    c[category] = val
        
        return c
