from typing import Dict, Optional
from .base import ConstraintExtractor

class ConstraintRegistry:
    def __init__(self):
        self._by_type: Dict[str, ConstraintExtractor] = {}

    def register(self, extractor: ConstraintExtractor):
        self._by_type[extractor.type_name] = extractor

    def get(self, type_name: str) -> Optional[ConstraintExtractor]:
        return self._by_type.get(type_name)
