import re
from typing import List, Dict, Any

class PIISanitizer:
    """
    Utility class to sanitize Personal Identifiable Information (PII) 
    before sending data to external AI models.
    """
    
    # Common PII Patterns
    PATTERNS = {
        "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "phone": r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b',
        "credit_card": r'\b(?:\d[ -]*?){13,16}\b',
        # Mexico specific patterns if applicable (RFC/CURP)
        "mx_rfc": r'\b[A-Z&]{3,4}\d{6}[A-Z0-9]{3}\b',
        "mx_curp": r'\b[A-Z][AEIOUX][A-Z]{2}\d{6}[HM][A-Z]{2}[B-DF-HJ-NP-TV-Z]{3}[A-Z\d]\d\b'
    }

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Replaces detected PII in text with placeholders.
        """
        if not text:
            return text
            
        sanitized = text
        for label, pattern in cls.PATTERNS.items():
            sanitized = re.sub(pattern, f"[PII:{label.upper()}]", sanitized)
            
        return sanitized

    @classmethod
    def sanitize_pages_data(cls, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sanitizes text_content in the pages_data list.
        """
        sanitized_data = []
        for page in pages_data:
            new_page = page.copy()
            if "text_content" in new_page:
                new_page["text_content"] = cls.sanitize_text(new_page["text_content"])
            sanitized_data.append(new_page)
        return sanitized_data
