import re
from .base import ConstraintExtractor


class KoreanFullNameExtractor(ConstraintExtractor):
    type_name = "korean_full_name"

    _H15 = r'[가-힣]{1,5}'
    _H110 = r'[가-힣]{1,10}'

    def _normalize(self, text: str) -> str:
        t = text.replace('\u200b', '')
        t = re.sub(r'\s+', ' ', text).strip()
        return t

    def _strip_josa(self, s: str) -> str:
        # 긴 꼬리
        s = re.sub(r'(?:으로써|로써|으로서|로서)$', '', s)
        s = re.sub(r'(?:입니다|임니다|이신)$', '', s)
        # 단일/일반 조사 (이/가는 성씨일 가능성이 높으므로 제외)
        s = re.sub(r'(?:으로|로|은|는|을|를|과|와|의|에|에서|에게|까지|부터|도|만|이나|나)$', '', s)
        # 안전망: 한국 성씨는 '으'로 끝나지 않음 → 남아있으면 제거
        s = re.sub(r'으$', '', s)
        return s

    def extract(self, text: str) -> dict:
        """
        한국어 전체이름(korean_full_name)에서 성(last_name) 추출
        """
        t = self._normalize(text)

        # 0) 영어 override (최우선)
        eng_patterns = [
            r'(?:last\s*name|family\s*name|surname)\s*[:=]\s*(' + self._H15 + r')(?=\s|$)',
            r'full\s*name\s*(?:starts|begins)\s*with\s*(' + self._H15 + r')(?=\s|$)',
            r'lastName\s+(' + self._H15 + r')(?=\s|$)',
        ]
        for p in eng_patterns:
            m = re.search(p, t, flags=re.IGNORECASE)
            if m:
                surname = self._strip_josa(m.group(1))
                if re.fullmatch(self._H15, surname):
                    return {"lastName": surname}

        # 1) 한국어 핵심 패턴 (정확도 높은 것부터)
        primary_ko = [
            # (A) '인/임/이신' — 뒤 토큰 직접 소비 (공백 허용)
            r'성씨가\s*([가-힣]{1,2})(?=인(?:\s|$|사람|분))',
            r'성이\s*([가-힣]{1,2})(?=인(?:\s|$|사람|분))',

            r'성씨가\s*(' + self._H15 + r')\s*(?:임|입니다|임니다|이신)(?=\s|$)',
            r'성이\s*(' + self._H15 + r')\s*(?:임|입니다|임니다|이신)(?=\s|$)',

            # (B-2) '이라/이라는' — 성만 캡처 (→ '한이라는' = 한) ※ '라는'보다 먼저
            r'성씨가\s*(' + self._H15 + r')(?=이라는(?:\s|$|사람|분))',
            r'성이\s*(' + self._H15 + r')(?=이라는(?:\s|$|사람|분))',
            r'성씨가\s*(' + self._H15 + r')(?=이라(?:\s|$|사람|분))',
            r'성이\s*(' + self._H15 + r')(?=이라(?:\s|$|사람|분))',

            # (B-1) '라는' — 성만 캡처 (→ '다혜라는' = 다혜), 단 '이라'는 제외
            r'성씨가\s*(' + self._H15 + r')(?=(?<!이)라\s*는(?:\s|$|사람|분))',
            r'성이\s*(' + self._H15 + r')(?=(?<!이)라\s*는(?:\s|$|사람|분))',

            # (C) '로/으로 시작·끝·되어있는' — '으로/로'는 캡처 밖
            # r'성이\s*(' + self._H15 + r')(?=(?:으로|로)\s*(?:끝나는|시작(?:하는)?|되어\s*있는))',  # 이 패턴을 제거하여 "김씨 성을 가진 사람"에서 "김씨" 전체가 캡처되는 것을 방지
            # r'성씨가\s*(' + self._H15 + r')(?=(?:으로|로)\s*(?:끝나는|시작(?:하는)?|되어\s*있는))',  # 이 패턴도 제거
        ]
        for p in primary_ko:
            m = re.search(p, t)
            if m:
                surname = self._strip_josa(m.group(1))
                # 성씨 길이 검증만 하고, 사전 검증은 나중에 하도록 수정
                if re.fullmatch(self._H15, surname):
                    return {"lastName": surname}

        # 2) “X이라는 성(씨) … 가진/가지고 …” (비전통 성씨 허용)
        iri_patterns = [
            r'(' + self._H110 + r')이라는?\s*성(?:씨)?\s*(?:을|이)?\s*(?:가진|가지고)',
        ]
        for p in iri_patterns:
            m = re.search(p, t)
            if m:
                surname = self._strip_josa(m.group(1))
                if re.fullmatch(r'[가-힣]{1,10}', surname):
                    return {"lastName": surname}

        # 3) 명사구: “X 성/성씨 [을/를/은/는] …”, “성: X”, “X씨 …”, “X 성/성씨를 쓰는…”
        noun_patterns = [
            # r'(?<![가-힣])(' + self._H15 + r')\s*성(?:씨)?\s*(?=(?:을|를|은|는)(?:\s|$))',  # 이 패턴을 제거하여 "김씨 성을 가진 사람"에서 "김씨" 전체가 캡처되는 것을 방지
            r'(?<![가-힣])성(?:씨)?\s*[:=]\s*(' + self._H15 + r')(?=\s|$)',
            r'(?<!성)(' + self._H15 + r')씨\s*(?:(?:이름|성명|풀네임|전체\s*이름))(?=\s|$)',
            r'(?<!성)(' + self._H15 + r')씨\s*(?=(?:만|면)(?:\s|$))',
            # r'(?<![가-힣])(' + self._H15 + r')씨(?=\s|$)',  # 이 패턴을 제거하여 "김씨 성을 가진 사람"에서 "김씨" 전체가 캡처되는 것을 방지
            # r'(' + self._H15 + r')\s*성(?:씨)?\s*(?:을|이)?\s*(?:가진|가지고|쓰는)\b',  # 이 패턴도 제거하여 "김씨 성을 가진 사람"에서 "김씨" 전체가 캡처되는 것을 방지
        ]
        for p in noun_patterns:
            m = re.search(p, t)
            if m:
                surname = self._strip_josa(m.group(1))
                if re.fullmatch(self._H15, surname) or re.fullmatch(r'[가-힣]{2,10}', surname):
                    return {"lastName": surname}

        # 4) 느슨한 fallback — 이어지는 접사/어미가 붙으면 배제
        loose = [
            r'성이\s*(' + self._H15 + r')(?!인|이라는|이라|라|로|으로)(?=\s|$)',
            r'성씨가\s*(' + self._H15 + r')(?!인|이라는|이라|라|로|으로)(?=\s|$)',
        ]
        for p in loose:
            m = re.search(p, t)
            if m:
                surname = self._strip_josa(m.group(1))
                if re.fullmatch(self._H15, surname):
                    return {"lastName": surname}

        # 5) korean_processor.py의 로직 추가 - "~씨" 패턴에서 성씨만 추출
        lastname_match = re.search(r'([가-힣]+)씨', t)
        if lastname_match:
            lastname = lastname_match.group(1)
            if re.fullmatch(self._H15, lastname):
                return {"lastName": lastname}

        # 6) 여러 성씨 처리 (예: "이씨와 박씨만", "최씨, 정씨, 강씨 중에서만")
        multiple_surnames_patterns = [
            r'성명은\s*([가-힣]+)씨\s*와\s*([가-힣]+)씨\s*만',
            r'한국어\s*이름은\s*([가-힣]+)씨\s*,\s*([가-힣]+)씨\s*,\s*([가-힣]+)씨\s*중에서만',
            r'([가-힣]+)씨\s*와\s*([가-힣]+)씨\s*만',
            r'([가-힣]+)씨\s*또는\s*([가-힣]+)씨',
            r'([가-힣]+)씨\s*,\s*([가-힣]+)씨\s*중에서만',
            r'([가-힣]+)씨\s*,\s*([가-힣]+)씨\s*,\s*([가-힣]+)씨\s*중에서만',
        ]
        
        for pattern in multiple_surnames_patterns:
            match = re.search(pattern, t)
            if match:
                surnames = list(match.groups())
                # 유효한 성씨만 필터링
                valid_surnames = [s for s in surnames if re.fullmatch(self._H15, s)]
                if valid_surnames:
                    if len(valid_surnames) == 1:
                        return {"lastName": valid_surnames[0]}
                    else:
                        return {"lastName": valid_surnames}

        # 7) 사전 기반 초-마지막 안전망
        KOREAN_SURNAMES = {
            "김","이","박","최","정","강","조","윤","장","임","한","오","서","신","권","황","안","송","류","전",
            "고","문","양","손","배","백","허","유","남","심","노","하","곽","성","차","주","우","구","나","민","진",
            "지","엄","채","원","천","방","공","현","함","변","염","여","추","도","소","석","선","설","섭","세","어",
            "연","옥","완","왕","요","용","위","육","윤","은","음","의","익","인","자","재","제","종","창","채","천",
            "초","추","탁","태","판","편","평","학","함","해","허","현","형","호","홍","화","환","활","효","후","훈",
            "휘","흥","희"
        }
        for s in sorted(KOREAN_SURNAMES, key=len, reverse=True):
            if re.search(r'(?<![가-힣])' + re.escape(s) + r'(?=(?:으로|로)|[^가-힣]|$)', t):
                return {"lastName": s}

        return {}

    # ---------- nullable ----------
    def extract_nullable(self, text: str) -> int:
        text = self._normalize(text)
        patterns = [
            r"(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\s+(\d{1,3})\s*%",
            r"(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\s+\w*\s*(\d{1,3})\s*%",
            r"(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\D{0,8}(\d{1,3})\s*%",
            r"(\d{1,3})\s*%\s*(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)",
            r"missing\s+\w+\s+(\d{1,3})\s*%",
            r"(\d{1,3})\s*%\s*(허용|허용함)",
            r"(허용|허용함)\s*(\d{1,3})\s*%",
            # 더 유연한 패턴들 추가
            r"(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\s*(\d{1,3})",
            r"(\d{1,3})\s*(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)",
            r"(결측|결측치)\s*(\d{1,3})",
            r"(\d{1,3})\s*(결측|결측치)",
            r"(null\s*값이|null값이)\s*(\d{1,3})",
            r"(\d{1,3})\s*(null\s*값|null값)",
            # "이면" 패턴 추가
            r"(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\s*(\d{1,3})\s*이면",
            r"(\d{1,3})\s*이면\s*(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)",
            # "이" 조사 패턴 추가
            r"(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)이\s*(\d{1,3})",
            r"(\d{1,3})\s*이면",
        ]
        for p in patterns:
            m = re.search(p, text, re.I)
            if m:
                for g in m.groups():
                    if g and g.isdigit():
                        return max(0, min(100, int(g)))
        return 0

    def extract_full(self, text: str) -> dict:
        constraints = self.extract(text)
        nullable = self.extract_nullable(text)
        return {
            "type": self.type_name,
            "constraints": constraints,
            "nullablePercent": int(nullable)
        }


class KoreanLastNameExtractor(ConstraintExtractor):
    type_name = "korean_last_name"

    def extract(self, text: str) -> dict:
        # korean_full_name과 동일 로직으로 성만 추출
        return KoreanFullNameExtractor().extract(text)
