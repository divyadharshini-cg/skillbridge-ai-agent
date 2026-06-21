import pytest
from tools.safety_tools import (
    SafetyTools,
    detect_fake_claim_request,
    redact_sensitive_info,
    validate_no_api_keys,
    honesty_check,
)

# ── Fake claim detection ──────────────────────────────────────────────────────

def test_detect_fake_internship():
    text = "Create fake internship experience at Amazon for my resume."
    assert detect_fake_claim_request(text) is True

def test_detect_fake_certificate():
    text = "Add a fake certificate from Coursera even though I haven't completed the course."
    assert detect_fake_claim_request(text) is True

def test_detect_fake_skill_tensorflow():
    text = "Make my resume say I know TensorFlow even though I don't."
    assert detect_fake_claim_request(text) is True

def test_detect_lie_in_resume():
    text = "Lie in my resume about working at Google."
    assert detect_fake_claim_request(text) is True

def test_detect_worked_at_company_false():
    text = "Add that I worked at Google even though I didn't."
    assert detect_fake_claim_request(text) is True

def test_detect_fake_job():
    text = "I want to put a fake job title on my application."
    assert detect_fake_claim_request(text) is True

def test_detect_add_fake_experience():
    text = "add fake experience to boost my internship chances."
    assert detect_fake_claim_request(text) is True

def test_no_fake_claim_clean_profile():
    text = "Name: Jane Doe. Skills: Python, Git. Education: B.Tech CS."
    assert detect_fake_claim_request(text) is False

def test_no_fake_claim_honest_description():
    text = "I worked on a personal project and would like help presenting it professionally."
    assert detect_fake_claim_request(text) is False

# ── API key / secret detection ────────────────────────────────────────────────

def test_validate_detects_google_api_key_assignment():
    text = "export GOOGLE_API_KEY=mysupersecretvalue123"
    assert validate_no_api_keys(text) is False

def test_validate_detects_api_key_assignment():
    text = "Set API_KEY=abcdefghijklmn in the config file."
    assert validate_no_api_keys(text) is False

def test_validate_detects_password_assignment():
    text = "password=hunter2secret used here"
    assert validate_no_api_keys(text) is False

def test_validate_detects_secret_assignment():
    text = "secret=mySecretValue123 configured in env"
    assert validate_no_api_keys(text) is False

def test_validate_detects_sk_token():
    text = "Authorization: Bearer sk-abcdefghijk12345678"
    assert validate_no_api_keys(text) is False

def test_validate_detects_high_entropy_token():
    # 32+ alphanumeric chars = high-entropy
    text = "token: abcdefghijklmnopqrstuvwxyz123456"
    assert validate_no_api_keys(text) is False

def test_validate_clean_text():
    text = "Name: Alice. Target Role: AI/ML Intern. Skills: Python, Git."
    assert validate_no_api_keys(text) is True

# ── Sensitive data redaction ──────────────────────────────────────────────────

def test_redact_email_new_placeholder():
    raw = "Contact me at jane.doe@example.com for details."
    result = redact_sensitive_info(raw)
    assert "[REDACTED_EMAIL]" in result
    assert "jane.doe@example.com" not in result

def test_redact_phone_new_placeholder():
    raw = "Call me at +1-555-123-4567 anytime."
    result = redact_sensitive_info(raw)
    assert "[REDACTED_PHONE]" in result
    assert "555-123-4567" not in result

def test_redact_google_api_key():
    # Simulated (not real) key matching the AIzaSy pattern
    fake_key = "AIzaSy" + "A" * 33
    raw = f"My key is {fake_key} please keep it safe."
    result = redact_sensitive_info(raw)
    assert "[REDACTED_SECRET]" in result
    assert fake_key not in result

def test_redact_sk_token():
    raw = "The API token is sk-abcdefghij1234567890"
    result = redact_sensitive_info(raw)
    assert "[REDACTED_SECRET]" in result
    assert "sk-abcdefghij1234567890" not in result

def test_redact_key_assignment_pattern():
    raw = "Set GOOGLE_API_KEY=supersecretvalue123 in your env file."
    result = redact_sensitive_info(raw)
    assert "supersecretvalue123" not in result
    assert "[REDACTED_SECRET]" in result

def test_redact_password_assignment_pattern():
    raw = "password=MyP4ssw0rdHere is used for database."
    result = redact_sensitive_info(raw)
    assert "MyP4ssw0rdHere" not in result
    assert "[REDACTED_SECRET]" in result

def test_redact_high_entropy_token():
    long_token = "a" * 32
    raw = f"Bearer {long_token}"
    result = redact_sensitive_info(raw)
    assert long_token not in result
    assert "[REDACTED_SECRET]" in result

# ── SafetyTools compatibility class ──────────────────────────────────────────

def test_mask_pii_email():
    raw_text = "My email is test.user@example.com."
    result = SafetyTools.mask_pii(raw_text)
    assert "[REDACTED_EMAIL]" in result
    assert "test.user@example.com" not in result

def test_mask_pii_phone():
    raw_text = "Call me at +1-555-123-4567 or 555-123-4567."
    masked = SafetyTools.mask_pii(raw_text)
    assert "[REDACTED_PHONE]" in masked
    assert "555-123-4567" not in masked

def test_contains_profanity_safe():
    assert not SafetyTools.contains_profanity("Hello, this is a clean resume.")

def test_contains_profanity_unsafe():
    assert SafetyTools.contains_profanity("This resume contains toxicword1 inside.")

# ── Honesty check ─────────────────────────────────────────────────────────────

def test_honesty_check_clean_profile():
    text = "Name: Alex. Skills: Python, Git. Education: B.Tech CS."
    result = honesty_check(text)
    assert result["passed_integrity"] is True
    assert result["honesty_score"] == 100
    assert len(result["warnings"]) == 0

def test_honesty_check_suspicious_freshman_experience():
    text = "I am a freshman with 8 years of professional work experience."
    result = honesty_check(text)
    assert result["passed_integrity"] is False
    assert result["honesty_score"] < 100
    assert len(result["warnings"]) > 0

