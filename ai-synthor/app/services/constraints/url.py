from .base import ConstraintExtractor

class UrlExtractor(ConstraintExtractor):
    type_name = "url"

    def extract(self, text: str) -> dict:
        low = text.lower()
        c = {}
        if "protocol" in low or "프로토콜" in text: c["protocol"] = "True"
        if "host" in low or "호스트" in text:       c["host"] = "True"
        if "path" in low or "경로" in text:          c["path"] = "True"
        if "query" in low or "쿼리" in text:        c["query string"] = "True"
        return c
