import re
from .base import ConstraintExtractor

class AvatarExtractor(ConstraintExtractor):
    type_name = "avatar"

    def extract(self, text: str) -> dict:
        c = {}
        t = text

        #128x128 / 128 X 128 / 128*128 / 128×128 (+ optional units)
        m = re.search(
            r'(?<!\d)(\d+)\s*[xX\*×]\s*(\d+)\s*(?:px|픽셀|pixels?)?',
            t, re.I
        )

        #size: 128 x 128 / resolution 128x128
        if not m:
            m = re.search(
                r'(?:size|resolution|해상도)\s*[:=]?\s*(\d+)\s*[xX\*×]\s*(\d+)',
                t, re.I
            )

        #"128 by 128"
        if not m:
            m = re.search(
                r'(?<!\d)(\d+)\s*(?:by|x)\s*(\d+)\b',
                t, re.I
            )

        #"width 128 height 256" / "가로 128 세로 256" / "가로 0, 세로 0"
        if not m:
            m = re.search(
                r'(?:width|가로)\s*[:=]?\s*(\d+)\s*,?\s*(?:세로|height)\s*[:=]?\s*(\d+)',
                t, re.I
            )

        #"세로 256 가로 128" (순서 반대) / "세로 0, 가로 0"
        if not m:
            m = re.search(
                r'(?:height|세로)\s*[:=]?\s*(\d+)\s*,?\s*(?:가로|width)\s*[:=]?\s*(\d+)',
                t, re.I
            )

        #"정사각형 128", "square 128", "정방형 256", "128px square"
        if not m:
            m_sq = re.search(
                r'(?:정사각형|정방형|square)\s*(\d+)\s*(?:px|픽셀|pixels?)?'
                r'|(\d+)\s*(?:px|픽셀|pixels?)?\s*(?:정사각형|정방형|square)',
                t, re.I
            )
            if m_sq:
                n = next(filter(None, m_sq.groups()))
                c["size"] = f"{n}x{n}"

        #최종 size 지정
        if "size" not in c and m:
            w, h = m.group(1), m.group(2)
            c["size"] = f"{w}x{h}"

        # png, bmp, jpg만 허용
        fmt_map = {
            "png": r'\bpng\b|png\s*형식|png\s*포맷|png\s*로\s*저장|format\s*[:=]?\s*png|png\s*로',
            "bmp": r'\bbmp\b|bmp\s*형식|bmp\s*포맷|bmp\s*로\s*저장|format\s*[:=]?\s*bmp|bmp\s*로',
            "jpg": r'\bjpg\b|\bjpeg\b|jpe?g\s*형식|jpg\s*포맷|jpe?g\s*로\s*저장|format\s*[:=]?\s*(?:jpg|jpeg)|jpe?g\s*로',
        }

        # 여러 형식 찾기
        found_formats = []
        for norm_fmt, pat in fmt_map.items():
            for mfmt in re.finditer(pat, t, flags=re.I):
                if norm_fmt not in found_formats:
                    found_formats.append(norm_fmt)

        if found_formats:
            if len(found_formats) == 1:
                c["format"] = found_formats[0]
            else:
                # 순서를 맞추기 위해 정렬 (jpg, png, bmp 순서)
                format_order = {"jpg": 0, "png": 1, "bmp": 2}
                sorted_formats = sorted(found_formats, key=lambda x: format_order.get(x, 3))
                c["format"] = sorted_formats

        return c