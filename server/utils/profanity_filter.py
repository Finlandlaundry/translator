import re
from typing import List

# 기본 금칙어 목록 (확장 가능)
PROFANITY_WORDS = [
    "씨발", "병신", "개새끼", "미친놈", "미친년", "좆", "좁", "지랄", "닥쳐", "꺼져",
    "fuck", "shit", "damn", "bitch", "asshole"
]

class ProfanityFilter:
    def __init__(self, custom_words: List[str] = None):
        self.words = PROFANITY_WORDS.copy()
        if custom_words:
            self.words.extend(custom_words)
    
    def contains_profanity(self, text: str) -> bool:
        """텍스트에 금칙어가 포함되어 있는지 확인"""
        text_lower = text.lower()
        for word in self.words:
            if word.lower() in text_lower:
                return True
        return False
    
    def filter_text(self, text: str) -> str:
        """금칙어를 *로 치환"""
        filtered_text = text
        for word in self.words:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            filtered_text = pattern.sub('*' * len(word), filtered_text)
        return filtered_text
    
    def is_safe(self, text: str) -> bool:
        """텍스트가 안전한지 확인 (금칙어 없음)"""
        return not self.contains_profanity(text)

# 전역 인스턴스
profanity_filter = ProfanityFilter()