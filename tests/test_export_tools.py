import os
import tempfile
from tools.export_tools import ExportTools

def test_export_as_markdown():
    report_data = {
        "role": "Software Engineer Intern",
        "match_score": 85.0,
        "project": "REST API Scheduler",
        "roadmap": "Day 1: Setup"
    }
    
    # Use temporary file to avoid writing to workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "test_report.md")
        success = ExportTools.export_as_markdown(report_data, output_file)
        
        assert success
        assert os.path.exists(output_file)
        
        with open(output_file, "r") as f:
            content = f.read()
            assert "# SkillBridge AI Coaching Report" in content
            assert "**Target Role:** Software Engineer Intern" in content
            assert "**Readiness Match Score:** 85.0%" in content
            assert "REST API Scheduler" in content
