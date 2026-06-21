import re
from typing import Dict, Any, List

def detect_fake_claim_request(text: str) -> bool:
    """
    Checks if a candidate is asking to inject fake credentials, projects, or job history.
    """
    patterns = [
        "fake resume", "falsify", "lie on my resume", "exaggerate", "fake experience",
        "make up a project", "pretend i worked", "fake credential", "fake job", "lie about"
    ]
    lowered = text.lower()
    return any(p in lowered for p in patterns)

def honesty_check(text: str) -> Dict[str, Any]:
    """
    Checks for logical contradictions in resume or profile text.
    For example, junior/sophomore candidate profiles claiming 10+ years experience.
    """
    lowered = text.lower()
    warnings = []
    honesty_score = 100
    
    # Identify indicators of student level
    has_sophomore = "sophomore" in lowered or "second year" in lowered or "2nd year" in lowered
    has_freshman = "freshman" in lowered or "first year" in lowered or "1st year" in lowered
    
    # Regex search for experience claims
    exp_match = re.search(r'\b(\d+)\+?\s*years?\s*of?\s*(?:work|professional)?\s*experience', lowered)
    if exp_match:
        years = int(exp_match.group(1))
        if years > 5 and (has_freshman or has_sophomore):
            warnings.append(f"Suspicious claim: Freshman/Sophomore student status indicating {years}+ years of experience.")
            honesty_score -= 30
        elif years > 10:
            warnings.append(f"Suspicious claim: Student profile indicating {years}+ years of work experience.")
            honesty_score -= 20
            
    return {
        "passed_integrity": honesty_score >= 70,
        "honesty_score": max(honesty_score, 0),
        "warnings": warnings
    }

def redact_sensitive_info(text: str) -> str:
    """
    Masks common PII strings such as email addresses, phone numbers, and addresses.
    """
    # Redact email addresses (ensuring sentence dots are left outside)
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]*[a-zA-Z0-9-]'
    text = re.sub(email_pattern, "[EMAIL_MASKED]", text)
    
    # Redact telephone formats
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    text = re.sub(phone_pattern, "[PHONE_MASKED]", text)
    
    return text

def validate_no_api_keys(text: str) -> bool:
    """
    Checks if text leaks high-entropy credentials or secrets.
    Returns True if clean, False if secrets are detected.
    """
    google_key_pattern = r'\bAIzaSy[a-zA-Z0-9_-]{33}\b'
    aws_key_pattern = r'\bA[KS]IA[a-zA-Z0-9]{16}\b'
    secret_assignment = r'\b(?:api_key|secret_key|password|token)\s*=\s*["\'][a-zA-Z0-9_.-]{16,}["\']'
    
    if re.search(google_key_pattern, text) or re.search(aws_key_pattern, text):
        return False
        
    if re.search(secret_assignment, text, re.IGNORECASE):
        return False
        
    return True

# Compatibility class stub for unit tests
class SafetyTools:
    @staticmethod
    def mask_pii(text: str) -> str:
        return redact_sensitive_info(text)

    @staticmethod
    def contains_profanity(text: str) -> bool:
        blacklist = ["toxicword1", "inappropriatephrase"]
        lowered = text.lower()
        return any(w in lowered for w in blacklist)
