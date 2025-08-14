from typing import Dict, Any, Optional
from .base import ConstraintExtractor
from .email_address import EmailAddressConstraint


class EmailExtractor(ConstraintExtractor):
    """이메일 제약 조건 추출기"""
    
    def __init__(self):
        super().__init__()
        self.email_constraint = EmailAddressConstraint()
    
    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """한글 텍스트에서 이메일 제약 조건 추출"""
        return self.email_constraint.parse_korean_constraints(text)
    
    type_name = "email_address"
