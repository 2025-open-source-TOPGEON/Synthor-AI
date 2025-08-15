import re

class NullablePercentExtractor:
    def extract(self, text: str) -> int:
        # 우선순위: null field percentage → ko → blank → nullable → null → missing → ratio
        checks = [
            # Handle "null field_name percentage%" pattern (e.g., "null age 5%")
            re.search(r'^null\s+\w+\s+(\d+)%', text, re.I),
            re.search(r'빈\s*값?\s*(\d+)%|빈값\s*(\d+)%|비어?\s*있음?\s*(\d+)%|null\s*값?\s*(\d+)%|빈\s*(\d+)%|결측치\s*(\d+)%', text, re.I),
            re.search(r'blank\s*:?\s*(\d+)%', text, re.I),
            re.search(r'nullable\s*:?\s*(\d+)%', text, re.I),
            re.search(r'(?<!non-)null\s*:?\s*(\d+)%', text, re.I),
            re.search(r'missing\s*:?\s*(\d+)%', text, re.I),
            re.search(r'missing\s+\w+\s+(\d+)%', text, re.I),  # "missing age 20%" 패턴
            # 추가 패턴들
            re.search(r'(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\s+(\d{1,3})\s*%', text, re.I),
            re.search(r'(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\s+\w*\s*(\d{1,3})\s*%', text, re.I),
            re.search(r'(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\D{0,8}(\d{1,3})\s*%', text, re.I),
            re.search(r'(\d{1,3})\s*%\s*(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)', text, re.I),
            re.search(r'(허용|허용함)\s*(\d{1,3})\s*%', text, re.I),
            re.search(r'(\d{1,3})\s*%\s*(허용|허용함)', text, re.I),
            # 더 유연한 패턴들
            re.search(r'(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\s*(\d{1,3})', text, re.I),
            re.search(r'(\d{1,3})\s*(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)', text, re.I),
            re.search(r'(결측|결측치)\s*(\d{1,3})', text, re.I),
            re.search(r'(\d{1,3})\s*(결측|결측치)', text, re.I),
            re.search(r'(null\s*값이|null값이)\s*(\d{1,3})', text, re.I),
            re.search(r'(\d{1,3})\s*(null\s*값|null값)', text, re.I),
            # "이면" 패턴 추가
            re.search(r'(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)\s*(\d{1,3})\s*이면', text, re.I),
            re.search(r'(\d{1,3})\s*이면\s*(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)', text, re.I),
            # "이" 조사 패턴 추가
            re.search(r'(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)이\s*(\d{1,3})', text, re.I),
            re.search(r'(\d{1,3})\s*이면', text, re.I),
            # "은" 조사 패턴 추가
            re.search(r'(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)은\s*(\d{1,3})', text, re.I),
            re.search(r'(\d{1,3})\s*은\s*(nullable|null|빈값|결측|결측치|없어도|옵션|optional|missing)', text, re.I),
        ]
        for m in checks:
            if m:
                # 숫자만 있는 그룹을 찾기
                for val in m.groups():
                    if val and val.isdigit():
                        return max(0, min(100, int(val)))

        m_ko = re.search(r'(\d+)개?\s*중에?\s*(\d+)개?\s*빈\s*값?', text)
        if m_ko:
            total = int(m_ko.group(1)); nulls = int(m_ko.group(2))
            return 0 if total <= 0 else max(0, min(100, int(nulls/total*100)))

        m_en = re.search(r'(\d+)\s+out\s+of\s+(\d+)\s+null', text, re.I)
        if m_en:
            nulls = int(m_en.group(1)); total = int(m_en.group(2))
            return 0 if total <= 0 else max(0, min(100, int(nulls/total*100)))

        return 0