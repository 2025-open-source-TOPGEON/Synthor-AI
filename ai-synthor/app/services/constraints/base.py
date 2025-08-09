from abc import ABC, abstractmethod
from typing import Dict

class ConstraintExtractor(ABC):
    type_name: str

    @abstractmethod
    def extract(self, text: str) -> Dict:
        """해당 타입의 constraints 딕셔너리 반환(없으면 빈 dict).
           오류는 ValueError를 던진다."""
        ...
