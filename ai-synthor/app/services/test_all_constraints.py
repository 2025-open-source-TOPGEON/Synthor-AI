#!/usr/bin/env python3
"""
Comprehensive test script for all constraint types
"""

from app.services.parser import Parser

def test_all_constraints():
    """Test all constraint types with various input patterns"""
    
    parser = Parser()
    
    # Test cases for all constraint types
    test_cases = [
        # Password constraints
        "비밀번호는 최소 10자 이상이어야 합니다.",
        "Password must be at least 10 characters long.",
        "비밀번호 minimum length 10 이상.",
        "비밀번호에 대문자가 포함되어야 합니다.",
        "Password must include at least one uppercase letter.",
        "비밀번호에 uppercase letter 포함 필수.",
        "비밀번호에 소문자가 포함되어야 합니다.",
        "Password must contain lowercase letters.",
        "비밀번호 must contain lowercase letter.",
        "비밀번호에 숫자가 포함되어야 합니다.",
        "Password must include numbers.",
        "비밀번호 include numbers.",
        "비밀번호에 특수문자가 포함되어야 합니다.",
        "Password must have special characters.",
        "비밀번호 must have special characters.",
        "비밀번호는 최소 10자 이상이며 대문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include uppercase letters.",
        "비밀번호는 minimum length 10, include uppercase letter.",
        "비밀번호는 최소 10자 이상이며 소문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include lowercase letters.",
        "비밀번호는 minimum length 10, include lowercase letter.",
        "비밀번호는 최소 10자 이상이며 숫자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include numbers.",
        "비밀번호는 minimum length 10, include numbers.",
        "비밀번호는 최소 10자 이상이며 특수문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include special characters.",
        "비밀번호는 minimum length 10, include special characters.",
        "비밀번호에 대문자와 소문자가 포함되어야 합니다.",
        "Password must include uppercase and lowercase letters.",
        "비밀번호 include uppercase and lowercase letters.",
        "비밀번호에 대문자와 숫자가 포함되어야 합니다.",
        "Password must include uppercase letters and numbers.",
        "비밀번호 include uppercase letters and numbers.",
        "비밀번호에 대문자와 특수문자가 포함되어야 합니다.",
        "Password must include uppercase letters and special characters.",
        "비밀번호 include uppercase letters and special characters.",
        "비밀번호에 소문자와 숫자가 포함되어야 합니다.",
        "Password must include lowercase letters and numbers.",
        "비밀번호 include lowercase letters and numbers.",
        "비밀번호에 소문자와 특수문자가 포함되어야 합니다.",
        "Password must include lowercase letters and special characters.",
        "비밀번호 include lowercase letters and special characters.",
        "비밀번호에 숫자와 특수문자가 포함되어야 합니다.",
        "Password must include numbers and special characters.",
        "비밀번호 include numbers and special characters.",
        "비밀번호는 최소 10자 이상이며 대문자와 소문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include uppercase and lowercase letters.",
        "비밀번호는 minimum length 10, include uppercase and lowercase letters.",
        "비밀번호는 최소 10자 이상이며 대문자와 숫자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include uppercase letters and numbers.",
        "비밀번호는 minimum length 10, include uppercase letters and numbers.",
        "비밀번호는 최소 10자 이상이며 대문자와 특수문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include uppercase letters and special characters.",
        "비밀번호는 minimum length 10, include uppercase letters and special characters.",
        "비밀번호는 최소 10자 이상이며 소문자와 숫자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include lowercase letters and numbers.",
        "비밀번호는 minimum length 10, include lowercase letters and numbers.",
        "비밀번호는 최소 10자 이상이며 소문자와 특수문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include lowercase letters and special characters.",
        "비밀번호는 minimum length 10, include lowercase letters and special characters.",
        "비밀번호는 최소 10자 이상이며 숫자와 특수문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include numbers and special characters.",
        "비밀번호는 minimum length 10, include numbers and special characters.",
        "비밀번호에 대문자, 소문자, 숫자가 포함되어야 합니다.",
        "Password must include uppercase, lowercase letters and numbers.",
        "비밀번호 include uppercase, lowercase letters and numbers.",
        "비밀번호에 대문자, 소문자, 특수문자가 포함되어야 합니다.",
        "Password must include uppercase, lowercase letters and special characters.",
        "비밀번호 include uppercase, lowercase letters and special characters.",
        "비밀번호에 대문자, 숫자, 특수문자가 포함되어야 합니다.",
        "Password must include uppercase letters, numbers and special characters.",
        "비밀번호 include uppercase letters, numbers and special characters.",
        "비밀번호에 소문자, 숫자, 특수문자가 포함되어야 합니다.",
        "Password must include lowercase letters, numbers and special characters.",
        "비밀번호 include lowercase letters, numbers and special characters.",
        "비밀번호는 최소 10자 이상이며 대문자, 소문자, 숫자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include uppercase, lowercase, and numbers.",
        "비밀번호는 minimum length 10, include uppercase/lowercase/numbers.",
        "비밀번호는 최소 10자 이상이며 대문자, 소문자, 특수문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include uppercase, lowercase, and special characters.",
        "비밀번호는 minimum length 10, include uppercase/lowercase/special characters.",
        "비밀번호는 최소 10자 이상이며 대문자, 숫자, 특수문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include uppercase, numbers, and special characters.",
        "비밀번호는 minimum length 10, include uppercase/numbers/special characters.",
        "비밀번호는 최소 10자 이상이며 소문자, 숫자, 특수문자가 포함되어야 합니다.",
        "Password must be at least 10 characters and include lowercase, numbers, and special characters.",
        "비밀번호는 minimum length 10, include lowercase/numbers/special characters.",
        "비밀번호에 대문자, 소문자, 숫자, 특수문자가 포함되어야 합니다.",
        "Password must include uppercase, lowercase, numbers, and special characters.",
        "비밀번호 include uppercase, lowercase, numbers, and special characters.",
        "비밀번호는 최소 10자 이상이며 대문자, 소문자, 숫자, 특수문자가 모두 포함되어야 합니다.",
        "Password must be at least 10 characters and contain uppercase, lowercase, numbers, and special characters.",
        "비밀번호는 minimum length 10, include uppercase, lowercase, numbers, and special characters. null은 10으로",

    ]
    
    print("Testing all constraint types...")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            result = parser.parse_field_constraint(test_case)
            print(f"## 입력: {test_case}")
            print(f"{result}")
            print()
        except Exception as e:
            print(f"## 입력: {test_case}")
            print(f"ERROR: {e}")
            print()

if __name__ == "__main__":
    test_all_constraints()