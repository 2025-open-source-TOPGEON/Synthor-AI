from .base import ConstraintExtractor

class DefaultExtractor(ConstraintExtractor):
    type_name = "__default__"
    def extract(self, text: str) -> dict:
        return {}
