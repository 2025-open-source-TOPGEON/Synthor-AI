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
        ]
        for m in checks:
            if m:
                val = next(filter(None, m.groups()))
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