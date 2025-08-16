import re
from .base import ConstraintExtractor

class NumberBetweenExtractor(ConstraintExtractor):
    type_name = "number"

    _FW_TO_ASCII = str.maketrans(
        "０１２３４５６７８９％－～",
        "0123456789%-~"
    )

    # ---------- utils ----------
    def _normalize(self, text: str) -> str:
        t = text.translate(self._FW_TO_ASCII)
        t = re.sub(r"[–—−]", "-", t)   # 다양한 dash → '-'
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _to_number(self, s: str) -> float:
        return float(s.replace(",", ""))

    def _pick(self, *groups):
        for g in groups:
            if g is not None:
                return g
        return None

    # ---------- nullable ----------
    def extract_nullable(self, text: str) -> int:
        text = self._normalize(text)
        patterns = [
            r"(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\s+\w*\s*(\d{1,3})\s*%",
            r"(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\D{0,8}(\d{1,3})\s*%",
            r"(\d{1,3})\s*%\s*(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)",
            r"missing\s+\w+\s+(\d{1,3})\s*%",
            r"(\d{1,3})\s*%\s*(허용|허용함)",
            r"(허용|허용함)\s*(\d{1,3})\s*%",
        ]
        for p in patterns:
            m = re.search(p, text, re.I)
            if m:
                for g in m.groups():
                    if g and g.isdigit():
                        return max(0, min(100, int(g)))
        return 0

    # ---------- constraints only ----------
    def extract(self, text: str) -> dict:
        """
        항상 constraints만 반환합니다:
          {"min": <num>, "max": <num>, "decimals": <int>}
        (외부에서 type/nullablePercent를 붙이세요. 중첩 방지)
        """
        text = self._normalize(text)
        c = {}

        # 0) decimals (기본 0)
        m_dec = re.search(
            r"(?:소수점|소수)\s*(\d+)\s*자리|"
            r"(?:decimals?)\s*(\d+)|"
            r"(?:up to)\s*(\d+)\s*(?:decimals?)|"
            r"(?:정수\s*만|integer(?:\s*only)?)",
            text, re.I
        )
        if m_dec:
            if m_dec.group(1) or m_dec.group(2) or m_dec.group(3):
                dec = int(self._pick(m_dec.group(1), m_dec.group(2), m_dec.group(3)))
                c["decimals"] = max(0, dec)
            else:
                c["decimals"] = 0
        if "decimals" not in c:
            c["decimals"] = 0
        step = 10 ** (-c["decimals"]) if c["decimals"] > 0 else 1.0

        # 키워드 플래그
        is_age = re.search(r"\b(age|연령|나이)\b", text, re.I) is not None or re.search(r"(age|연령|나이)", text, re.I) is not None
        is_price = re.search(r"\b(price|amount|payment|가격|금액|결제금액|원|달러|USD|EUR|€|￥|£)\b", text, re.I) is not None
        is_quantity = re.search(r"\b(quantity|count|participants|items|order|수량|개수|참가자|개|명)\b", text, re.I) is not None
        is_length = re.search(r"\b(length|distance|width|길이|거리|폭|cm|m|km|inch|ft|meters)\b", text, re.I) is not None
        is_weight = re.search(r"\b(weight|mass|무게|질량|kg|g|ton|lb|oz|grams)\b", text, re.I) is not None
        is_temperature = re.search(r"\b(temperature|celsius|온도|섭씨|℃|℉|도)\b", text, re.I) is not None
        is_speed = re.search(r"\b(speed|driving speed|속도|주행속도|km/h|mph)\b", text, re.I) is not None
        is_time = re.search(r"\b(time|duration|minutes|hours|days|seconds|weeks|months|years|시간|기간|분|초|주|월|년)\b", text, re.I) is not None
        is_percentage = re.search(r"\b(success rate|probability|percentage|ratio|성공률|확률|퍼센트|비율|%)\b", text, re.I) is not None
        is_score = re.search(r"\b(score|grade|rating|점수|등급|평점|점)\b", text, re.I) is not None
        is_number_range = is_price or is_quantity or is_length or is_weight or is_temperature or is_speed or is_time or is_percentage or is_score

        # --- 1) '미만/under' 최우선(배타) + 락 ---
        exclusive_lock = False
        m_age_kor_under = re.search(r"(?:나이|연령)\s*(\d+)\s*세\s*미만", text)
        m_age_en_under = re.search(r"\bage\s+under\s*(\d+)\b", text, re.I)
        m_age_only_under = None
        if is_age and not (m_age_kor_under or m_age_en_under):
            m_age_only_under = re.search(r"(\d+)\s*세?\s*미만", text)
        m_under = m_age_kor_under or m_age_en_under or m_age_only_under
        if m_under:
            v = self._to_number(m_under.group(1))
            c["min"] = 1 if is_age else 1
            c["max"] = v - step  # 배타
            if c["decimals"] == 0:
                c["max"] = int(c["max"])
            exclusive_lock = True

        # --- 2) 정확히(고정값) ---
        if "min" not in c or "max" not in c:
            m_exact = re.search(
                r"(?:exactly|equals|정확히|정확한|같은|고정|으로\s*고정|동일|값은|fixed\s*at)\s*(\d+)", text, re.I
            )
            if not m_exact:
                m_exact = re.search(r"(?:^|[^><\d])=+\s*(\d+)\b", text)
            if not m_exact:
                m_exact = re.search(r"(\d+)세\s*(?:로\s*고정|동일)", text)
            if not m_exact:
                m_exact = re.search(r"exact\s+age\s+is\s+(\d+)", text, re.I)
            if m_exact:
                v = self._to_number(m_exact.group(1))
                c["min"] = v
                c["max"] = v

        # --- 3) from~to / between~and / ~ / - / 부터~까지 ---
        if "min" not in c and "max" not in c:
            m_between = re.search(r"(?:between|from)\s*(\d+)\s*(?:and|to|-|~)\s*(\d+)", text, re.I)
            if not m_between:
                m_between = re.search(r"(\d+)\s*[~-]\s*(\d+)", text)
            if not m_between:
                m_between = re.search(r"(\d+)\s*(?:부터|에서)\s*(\d+)\s*(?:까지)?", text)
            if m_between:
                a = self._to_number(m_between.group(1))
                b = self._to_number(m_between.group(2))
                lo, hi = (a, b) if a <= b else (b, a)
                c["min"], c["max"] = lo, hi

        # --- 4) 복합(포함) 세트 ---
        if "min" not in c or "max" not in c:
            m_range = re.search(r"(\d+)\s*이상\s*(\d+)\s*이하", text)
            if not m_range:
                m_range = re.search(r"(\d+)세\s*이상\s*(\d+)세\s*이하", text)
            if not m_range:
                m_range = re.search(r"(\d+)세\s*부터\s*(\d+)세\s*까지", text)
            if not m_range:
                m_range = re.search(
                    r"greater\s+than\s+or\s+equal\s+to\s+(\d+)\s+and\s+less\s+than\s+or\s+equal\s+to\s+(\d+)",
                    text, re.I
                )
            if m_range:
                a = self._to_number(m_range.group(1))
                b = self._to_number(m_range.group(2))
                lo, hi = (a, b) if a <= b else (b, a)
                c["min"], c["max"] = lo, hi

        # --- 5) 명시적 min/max 패턴 (최우선) ---
        if "min" not in c:
            m_min_explicit = re.search(r'min\s+(\d+)', text, re.I)
            if m_min_explicit:
                c["min"] = self._to_number(m_min_explicit.group(1))
        
        if "max" not in c:
            m_max_explicit = re.search(r'max\s+(\d+)', text, re.I)
            if m_max_explicit:
                c["max"] = self._to_number(m_max_explicit.group(1))

        # --- 6) and/or 분해 개별 규칙 ---
        if ("min" not in c or "max" not in c) and not exclusive_lock:
            parts = re.split(r'\s+and\s+|\s+or\s+', text, flags=re.I)

            min_patterns = [
                r"(\d+)\s*세?\s*이상",
                r"(\d+)\s*이상",
                r"at\s*least\s*(\d+)",
                r"greater\s*than\s*or\s*equal\s*to\s*(\d+)",
                r"(\d+)\s*세?\s*초과",
                r"greater\s*than\s*(\d+)",
                r"(\d+)\s*초과",
                r"over\s*(\d+)",
                r"최소\s*(\d+)",
                r"minimum\s*age\s*is\s*(\d+)",
                r"최소\s*age\s*(\d+)",
            ]
            # 포함(≤)에서 under 제외, 배타(<)는 여기서도 처리하지만 exclusive_lock이면 스킵
            max_patterns = [
                r"(\d+)\s*세?\s*이하",
                r"(\d+)\s*이하",
                r"at\s*most\s*(\d+)",
                r"less\s*than\s*or\s*equal\s*to\s*(\d+)",
                r"최대\s*(\d+)",
                r"maximum\s*(?:age\s*)?is\s*(\d+)",
                r"(\d+)\s*세?\s*미만",
                r"less\s*than\s*(\d+)",
                r"(\d+)\s*미만",
                r"under\s*(\d+)",  # 배타
            ]

            for part in parts:
                part = part.strip()
                if not part:
                    continue

                if "min" not in c:
                    for i, pat in enumerate(min_patterns):
                        m = re.search(pat, part, re.I)
                        if m:
                            v = self._to_number(m.group(1))
                            if i in [4, 5, 6, 7]:  # 초과/greater than/over → 배타
                                c["min"] = v + step
                            else:
                                c["min"] = v
                            break

                if "max" not in c and not exclusive_lock:
                    for i, pat in enumerate(max_patterns):
                        m = re.search(pat, part, re.I)
                        if m:
                            v = self._to_number(m.group(1))
                            if i in [6, 7, 8, 9]:  # 미만/less than/under → 배타
                                c["max"] = v - step
                                if c["decimals"] == 0:
                                    c["max"] = int(c["max"])
                            else:
                                c["max"] = v
                            break

        # --- 6) 일반 포함/배타 ---
        if "min" not in c:
            m_min_inc = re.search(r"(?:>=|greater\s*than\s*or\s*equal\s*to|이상|at\s*least)\s*(\d+)", text, re.I)
            if m_min_inc:
                v = self._to_number(self._pick(*m_min_inc.groups()))
                c["min"] = v
            else:
                m_min_exc = re.search(r"(?:greater\s*than|>\s*)(\d+)|(\d+)\s*(?:초과)(?:\s|$)", text, re.I)
                if m_min_exc:
                    v = self._to_number(self._pick(*m_min_exc.groups()))
                    c["min"] = v + step

        if "max" not in c and not exclusive_lock:
            m_max_inc = re.search(r"(?:<=|less\s*than\s*or\s*equal\s*to|이하|at\s*most)\s*(\d+)", text, re.I)
            if m_max_inc:
                v = self._to_number(self._pick(*m_max_inc.groups()))
                c["max"] = v
            else:
                m_max_exc = re.search(r"(?:less\s*than|<\s*)(\d+)|(\d+)\s*(?:미만)", text, re.I)
                if m_max_exc:
                    v = self._to_number(self._pick(*m_max_exc.groups()))
                    c["max"] = v - step
                    if c["decimals"] == 0:
                        c["max"] = int(c["max"])

        # --- 7) 보강 표현 ---
        if "max" not in c and not exclusive_lock:
            m_max_alt = re.search(r"(?:최대|이내|no\s*more\s*than|up\s*to|at\s*most|maximum)\s*(\d+)", text, re.I)
            if m_max_alt:
                c["max"] = self._to_number(m_max_alt.group(1))
        if "min" not in c:
            m_min_alt = re.search(r"(?:최소|at\s*least|minimum)\s+(\d+)(?:\s|$)", text, re.I)
            if m_min_alt:
                c["min"] = self._to_number(m_min_alt.group(1))

        # --- 8) 기본값 (스펙상 1~100) ---
        # 명시적으로 min, max가 지정되지 않은 경우에만 기본값 적용
        # 입력에서 min, max가 명시적으로 지정된 경우 기본값을 덮어쓰지 않음
        if "min" not in c and not re.search(r'min\s+\d+', text, re.I):
            c["min"] = 1
        if "max" not in c and not re.search(r'max\s+\d+', text, re.I):
            c["max"] = 100

        # --- 9) 정리/클램프 ---
        if "min" in c and "max" in c and c["min"] > c["max"]:
            c["min"], c["max"] = c["max"], c["min"]

        # Remove hard clamping to allow values outside 1-100 range
        if "min" in c:
            c["min"] = float(c["min"])
        if "max" in c:
            c["max"] = float(c["max"])

        if c["decimals"] == 0:
            def _maybe_int(x):
                xf = float(x)
                return int(xf) if xf.is_integer() else xf
            if "min" in c:
                c["min"] = _maybe_int(c["min"])
            if "max" in c:
                c["max"] = _maybe_int(c["max"])

        # ✅ constraints만 반환 (순서: min, max, decimals)
        result = {}
        if "min" in c:
            result["min"] = c["min"]
        if "max" in c:
            result["max"] = c["max"]
        result["decimals"] = int(c["decimals"])
        return result

    # ---------- 최종 형식이 바로 필요하면 ----------
    def extract_full(self, text: str) -> dict:
        constraints = self.extract(text)
        nullable = self.extract_nullable(text)
        return {
            "type": self.type_name,
            "constraints": constraints,
            "nullablePercent": int(nullable)
        }
