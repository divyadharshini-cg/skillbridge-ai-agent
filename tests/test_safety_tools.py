from tools.safety_tools import SafetyTools

def test_mask_pii_email():
    raw_text = "My email is test.user@example.com."
    expected = "My email is [EMAIL_MASKED]."
    assert SafetyTools.mask_pii(raw_text) == expected

def test_mask_pii_phone():
    raw_text = "Call me at +1-555-123-4567 or 555-123-4567."
    masked = SafetyTools.mask_pii(raw_text)
    assert "[PHONE_MASKED]" in masked
    assert "555-123-4567" not in masked

def test_contains_profanity_safe():
    assert not SafetyTools.contains_profanity("Hello, this is a clean resume.")

def test_contains_profanity_unsafe():
    assert SafetyTools.contains_profanity("This resume contains toxicword1 inside.")
