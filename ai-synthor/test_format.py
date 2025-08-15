#!/usr/bin/env python3

from app.services.system_prompt_processor import SystemPromptProcessor

def test_format():
    processor = SystemPromptProcessor()
    
    # 사용자가 제공한 테스트 케이스
    test_input = "온라인 교육 플랫폼 회원가입: 이름, 이메일(gmail.com만), 비밀번호(최소 10자 대문자 1개 소문자 1개 숫자 1개), 프로필 이미지(300x300 png), 나이(15 이상 70 이하), nullable 10%"
    
    print("## 입력:")
    print(test_input)
    print()
    
    try:
        result = processor.process_system_prompt(test_input)
        print("## 결과:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_format()
