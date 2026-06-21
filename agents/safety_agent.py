from llm_client import LLMClient
from tools.safety_tools import (
    detect_fake_claim_request,
    honesty_check,
    redact_sensitive_info,
    validate_no_api_keys,
    SafetyTools
)

class SafetyAgent:
    """
    SafetyAgent scans incoming resume text for inappropriate content,
    PII protection, and checks claims consistency to detect exaggeration.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Safety Agent"

    def audit_profile(self, profile_text: str) -> dict:
        """
        Scans for safety flags, claims consistency, API keys, and profanity.
        Redacts sensitive data and provides honest suggestions.
        """
        if not profile_text:
            profile_text = ""

        # Run safety and integrity tools
        is_fake_request = detect_fake_claim_request(profile_text)
        honesty_results = honesty_check(profile_text)
        has_profanity = SafetyTools.contains_profanity(profile_text)
        is_api_clean = validate_no_api_keys(profile_text)
        
        # Redact PII
        safe_text = redact_sensitive_info(profile_text)
        
        # Compile warnings and flags
        warnings = []
        safety_flags = []
        alternatives = []
        
        if is_fake_request:
            safety_flags.append("FAKE_CLAIMS_REQUEST")
            warnings.append("I can’t help add fake experience or false claims. I can help you describe your real projects and skills more professionally.")
            alternatives.append("I can’t help add fake experience or false claims. I can help you describe your real projects and skills more professionally.")
            
        if not honesty_results["passed_integrity"]:
            safety_flags.append("SUSPICIOUS_CLAIMS")
            warnings.extend(honesty_results["warnings"])
            alternatives.append("Align experience claims realistically with your current academic standing (e.g., Sophomore/Freshman).")
            
        if has_profanity:
            safety_flags.append("PROFANITY_DETECTED")
            warnings.append("Inappropriate or profane language detected.")
            alternatives.append("Adopt a professional and objective tone suitable for internship applications.")
            
        if not is_api_clean:
            safety_flags.append("API_KEY_LEAK")
            warnings.append("API key or secret-like credentials detected. The secret has been redacted for safety.")
            alternatives.append("Always redact passwords, API tokens, and private keys. Use environment variables in your code.")

        # If integrity checks pass but have lower level honesty warnings
        if honesty_results["passed_integrity"] and honesty_results["warnings"]:
            warnings.extend(honesty_results["warnings"])

        passed_safety = len(safety_flags) == 0
        honesty_score = honesty_results["honesty_score"]

        # Call LLM for enhanced explanation/alternatives if API is available
        if not self.llm.is_mock and profile_text:
            prompt = (
                f"Analyze this candidate profile for safety, honesty, and PII leaks.\n"
                f"Profile text:\n{profile_text}\n"
                f"Existing flags: {safety_flags}\n"
                f"Existing warnings: {warnings}\n"
                f"Please provide professional, constructive suggestions and honest alternatives."
            )
            llm_feedback = self.llm.generate(
                prompt=prompt,
                system_instruction="You are a career development safety inspector. Review candidate profiles for safety and offer constructive alternatives to dishonesty."
            )
            alternatives.append(llm_feedback)

        # Standard fallback alternatives if list is empty
        if not alternatives:
            alternatives.append("Maintain profile integrity. Leverage university career services or open-source contribution to fill gaps.")

        return {
            "passed_safety": passed_safety,
            "safety_flags": safety_flags,
            "honesty_score": honesty_score,
            "warnings": warnings,
            "safe_profile_text": safe_text,
            "honest_alternatives": alternatives
        }
