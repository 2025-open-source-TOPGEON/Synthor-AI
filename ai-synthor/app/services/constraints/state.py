import re
from .base import ConstraintExtractor
from ..constants_types import SUPPORTED_STATES
from ..mappings import KOR_TO_ENG_VALUE

class StateExtractor(ConstraintExtractor):
    type_name = "state"

    def extract(self, text: str) -> dict:
        """
        - 여러 개 나열 시 모두 허용하여 options: [ ... ] 로 반환
        - 한/영/혼용 자연어: "state: A, B and C", "A와 B, C만", "only A / B", "A 또는 B"
        - 괄호 포함/악센트 포함 명칭 허용
        - 한국어 표기는 KOR_TO_ENG_VALUE로 영문 정규화 후 SUPPORTED_STATES에 있는 값만 포함
        - 미지원 값은 예외 없이 무시
        """

        t = text.strip()

        # 후보 추출 패턴
        patterns = [
            r'(?:states?|지역|주|도)\s*[:=]\s*([^\n\r]+)',                 # state: A, B and C
            r'\bonly\b\s+([A-Za-z\u00C0-\u024F \-\(\)/\|,&]+)',           # only A / B
            r'([A-Za-z\u00C0-\u024F가-힣 \-\(\)/\|,&]+?)\s*만',            # A와 B, C만
        ]

        raw_candidates: list[str] = []

        for pat in patterns:
            m = re.search(pat, t, flags=re.IGNORECASE)
            if m:
                raw_list = m.group(1)
                # 콤마, 슬래시, 파이프, 한글 쉼표, and/or/및/또는/그리고/와/과/하고/이랑/랑 로 분리
                # \b를 사용해서 단어 경계에서만 매칭되도록 함
                parts = re.split(
                    r'\s*(?:,|，|、|/|\|)\s*|'
                    r'\s+(?:\band\b|\bor\b|및|또는|그리고|와|과|하고|이랑|랑)\s+',
                    raw_list,
                    flags=re.IGNORECASE
                )
                raw_candidates.extend([p for p in parts if p.strip()])
                break  # 첫 번째 매칭만 사용

        # 패턴에서 못 찾으면 SUPPORTED_STATES나 별칭 스캔
        if not raw_candidates:
            for st in SUPPORTED_STATES:
                if re.search(r'(?<!\w)' + re.escape(st) + r'(?!\w)', t, flags=re.IGNORECASE):
                    raw_candidates.append(st)
            for alias, eng in KOR_TO_ENG_VALUE.items():
                if re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', t, flags=re.IGNORECASE):
                    raw_candidates.append(alias)

        if not raw_candidates:
            return {}

        # 정규화 함수
        def normalize_name(s: str) -> str:
            s = s.strip().strip('\'"“”‘’')
            s = re.sub(r'\s+', ' ', s)
            mapped = KOR_TO_ENG_VALUE.get(s, s)
            if mapped in SUPPORTED_STATES:
                return mapped
            # 괄호 제거 버전도 시도
            no_paren = re.sub(r'\s*\([^)]*\)\s*', '', s).strip()
            mapped2 = KOR_TO_ENG_VALUE.get(no_paren, no_paren)
            if mapped2 in SUPPORTED_STATES:
                return mapped2
            return None  # 매핑 실패 시 None

        normalized: list[str] = []
        for raw in raw_candidates:
            name = normalize_name(raw)
            if name and name not in normalized:
                normalized.append(name)

        if not normalized:
            return {}

        return {"options": normalized}
