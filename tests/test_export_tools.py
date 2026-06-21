import os
import json
import tempfile
from tools.export_tools import ExportTools, export_json_report, export_markdown_report

# ── Legacy compatibility test ─────────────────────────────────────────────────

def test_export_as_markdown():
    report_data = {
        "role": "Software Engineer Intern",
        "match_score": 85.0,
        "project": "REST API Scheduler",
        "roadmap": "Day 1: Setup"
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "test_report.md")
        success = ExportTools.export_as_markdown(report_data, output_file)

        assert success
        assert os.path.exists(output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "# SkillBridge AI Coaching Report" in content
            assert "**Target Role:** Software Engineer Intern" in content
            assert "**Readiness Match Score:** 85.0%" in content
            assert "REST API Scheduler" in content

# ── Report safety: JSON export ────────────────────────────────────────────────

def test_json_export_redacts_email():
    report = {"candidate_email": "alice@secret.com", "notes": "Contact alice@secret.com"}
    result = export_json_report(report)
    assert "alice@secret.com" not in result
    assert "[REDACTED_EMAIL]" in result

def test_json_export_redacts_phone():
    report = {"contact": "Call at 555-123-4567 for details."}
    result = export_json_report(report)
    assert "555-123-4567" not in result
    assert "[REDACTED_PHONE]" in result

def test_json_export_redacts_api_key_assignment():
    report = {"config_note": "GOOGLE_API_KEY=mysecretkeyvalue123 is set here"}
    result = export_json_report(report)
    assert "mysecretkeyvalue123" not in result
    assert "[REDACTED_SECRET]" in result

def test_json_export_redacts_sk_token():
    report = {"auth": "token: sk-abcdefghij1234567890xyz"}
    result = export_json_report(report)
    assert "sk-abcdefghij1234567890xyz" not in result
    assert "[REDACTED_SECRET]" in result

def test_json_export_redacts_high_entropy_token():
    long_token = "z" * 32
    report = {"auth_token": long_token}
    result = export_json_report(report)
    assert long_token not in result
    assert "[REDACTED_SECRET]" in result

def test_json_export_does_not_modify_clean_report():
    report = {"name": "Alice", "role": "AI/ML Intern", "score": 85}
    result = export_json_report(report)
    parsed = json.loads(result)
    assert parsed["name"] == "Alice"
    assert parsed["role"] == "AI/ML Intern"

# ── Report safety: Markdown export ───────────────────────────────────────────

def test_markdown_export_redacts_email():
    report = {
        "role": "AI/ML Intern",
        "match_score": 70,
        "name": "alice@secret.com"
    }
    result = export_markdown_report(report)
    assert "alice@secret.com" not in result
    assert "[REDACTED_EMAIL]" in result

def test_markdown_export_redacts_api_key():
    report = {
        "role": "GenAI Intern",
        "match_score": 80,
        "roadmap_summary": "Set GOOGLE_API_KEY=leakedvalue123 in your profile"
    }
    result = export_markdown_report(report)
    assert "leakedvalue123" not in result
    assert "[REDACTED_SECRET]" in result

def test_markdown_export_to_file_is_safe():
    report = {
        "role": "Data Analyst Intern",
        "match_score": 60,
        "name": "Bob",
        "project_name": "Dashboard",
        "roadmap_summary": "Contact bob@company.com for more info"
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "safe_report.md")
        content = export_markdown_report(report, output_path=output_file)
        with open(output_file, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert "bob@company.com" not in file_content
        assert "[REDACTED_EMAIL]" in file_content

