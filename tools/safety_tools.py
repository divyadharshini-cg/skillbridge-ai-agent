import re
from typing import Dict, Any, List

def detect_fake_claim_request(text: str) -> bool:
    """
    Checks if a candidate is asking to inject fake credentials, projects, or job history.
    Supports detecting fake internship, fake certificate, fake skill, and lie-in-resume requests.
    """
    lowered = text.lower()
    
    # Specific list keywords
    patterns = [
        "fake resume", "falsify", "lie on my resume", "exaggerate", "fake experience",
        "make up a project", "pretend i worked", "fake credential", "fake job", "lie about",
        "lie in my resume", "fake internship", "fake certificate", "lie on resume", "fake claim"
    ]
    if any(p in lowered for p in patterns):
        return True
        
    # Check for "worked at ... even though ... didn't"
    if re.search(r"worked\s+at\s+\w+\s+even\s+though\s+(?:i\s+)?did(?:n't|\s+not)", lowered):
        return True
        
    # Check for skill fake claim like "say I know TensorFlow though I don't"
    if re.search(r"say\s+(?:i\s+)?know\s+\w+\s+though\s+(?:i\s+)?did(?:n't|\s+not|\s+have|'t)", lowered) or \
       re.search(r"say\s+(?:i\s+)?know\s+\w+\s+even\s+though\s+(?:i\s+)?did(?:n't|\s+not|\s+have|'t)", lowered) or \
       re.search(r"know\s+\w+\s+though\s+i\s+don't", lowered) or \
       re.search(r"know\s+\w+\s+even\s+though\s+i\s+don't", lowered):
        return True
        
    # Check for general "create/add fake..."
    if re.search(r"(?:create|add|generate|make)\s+fake\s+(?:experience|internship|certificate|claim|project|job|skill)", lowered):
        return True
        
    return False

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
    
    # Regex search for experience claims — broad pattern catches:
    # "8 years experience", "8 years of experience", "8 years of work experience",
    # "8 years of professional work experience", "8+ years professional experience"
    exp_match = re.search(
        r'\b(\d+)\+?\s*years?\s*(?:of\s+)?(?:(?:professional|work|industry|hands-on)\s+)*experience',
        lowered
    )
    if exp_match:
        years = int(exp_match.group(1))
        if years > 5 and (has_freshman or has_sophomore):
            warnings.append(f"Suspicious claim: Freshman/Sophomore student status indicating {years}+ years of experience.")
            honesty_score -= 30
        elif years > 10:
            warnings.append(f"Suspicious claim: Student profile indicating {years}+ years of work experience.")
            honesty_score -= 20
            
    return {
        "passed_integrity": honesty_score > 70,
        "honesty_score": max(honesty_score, 0),
        "warnings": warnings
    }

def redact_sensitive_info(text: str) -> str:
    """
    Masks common PII strings such as email addresses, phone numbers, passwords, and API keys.
    Uses safe placeholders [REDACTED_EMAIL], [REDACTED_PHONE], [REDACTED_SECRET].
    """
    if not text:
        return ""
        
    # Redact email addresses
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]*[a-zA-Z0-9-]'
    text = re.sub(email_pattern, "[REDACTED_EMAIL]", text)
    
    # Redact telephone formats
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    text = re.sub(phone_pattern, "[REDACTED_PHONE]", text)
    
    # Redact secrets, keys, and credentials
    # sk- keys
    text = re.sub(r'\bsk-[a-zA-Z0-9_-]{12,}\b', "[REDACTED_SECRET]", text)
    # Google API keys
    text = re.sub(r'\bAIzaSy[a-zA-Z0-9_-]{33}\b', "[REDACTED_SECRET]", text)
    # AWS access keys
    text = re.sub(r'\bA[KS]IA[a-zA-Z0-9]{16}\b', "[REDACTED_SECRET]", text)
    
    # Assignment patterns: api_key=..., GOOGLE_API_KEY=..., password=..., secret=...
    text = re.sub(
        r'\b(GOOGLE_API_KEY|API_KEY|password|secret|secret_key|api_key|token)\s*=\s*(["\']?)[a-zA-Z0-9_.-]{4,}\2',
        r'\1=[REDACTED_SECRET]',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'\b(GOOGLE_API_KEY|API_KEY|password|secret|secret_key|api_key|token)\s*:\s*(["\']?)[a-zA-Z0-9_.-]{4,}\2',
        r'\1: [REDACTED_SECRET]',
        text,
        flags=re.IGNORECASE
    )
    
    # High-entropy standalone tokens (alphanumeric length 32+)
    text = re.sub(r'\b[a-zA-Z0-9_-]{32,}\b', "[REDACTED_SECRET]", text)
    
    return text

def validate_no_api_keys(text: str) -> bool:
    """
    Checks if text leaks high-entropy credentials or secrets.
    Returns True if clean, False if secrets are detected.
    """
    if not text:
        return True
        
    lowered = text.lower()
    
    # Detect text patterns like GOOGLE_API_KEY=, API_KEY=, password=, secret=, sk-
    patterns = ["google_api_key=", "api_key=", "password=", "secret=", "sk-"]
    if any(p in lowered for p in patterns):
        return False
        
    google_key_pattern = r'\bAIzaSy[a-zA-Z0-9_-]{33}\b'
    aws_key_pattern = r'\bA[KS]IA[a-zA-Z0-9]{16}\b'
    sk_pattern = r'\bsk-[a-zA-Z0-9_-]{12,}\b'
    secret_assignment = r'\b(?:api_key|secret_key|password|token)\s*=\s*["\']?[a-zA-Z0-9_.-]{4,}["\']?'
    
    if re.search(google_key_pattern, text) or re.search(aws_key_pattern, text) or re.search(sk_pattern, text):
        return False
        
    if re.search(secret_assignment, text, re.IGNORECASE):
        return False
        
    # Long high-entropy tokens: alphanumeric words of length 32+
    if re.search(r'\b[a-zA-Z0-9_-]{32,}\b', text):
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

