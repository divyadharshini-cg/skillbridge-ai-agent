import os
import json
from typing import Dict, Any, Optional

def export_json_report(report: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Serializes a report dictionary to a JSON string format.
    Optionally writes to output_path if provided.
    """
    json_str = json.dumps(report, indent=2)
    if output_path:
        dir_name = os.path.dirname(os.path.abspath(output_path))
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)
    return json_str

def export_markdown_report(report: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Formats the evaluation results into a detailed Markdown report.
    Optionally writes to output_path if provided.
    """
    lines = [
        "# SkillBridge AI Coaching Report",
        "",
        f"**Target Role:** {report.get('role', 'N/A')}",
        f"**Readiness Match Score:** {report.get('match_score', 'N/A')}%",
        "",
        "## 👤 Candidate Details",
        f"- **Name:** {report.get('name', 'Student Candidate')}",
        f"- **Honesty Index Score:** {report.get('honesty_score', 'N/A')}/100",
        "",
        "## 🎯 Matching Skills",
    ]
    for skill in report.get("matching_skills", []):
        lines.append(f"- {skill}")
    lines.append("")
    
    lines.append("## ❌ Identified Skill Gaps")
    for gap in report.get("missing_skills", []):
        lines.append(f"- {gap}")
    lines.append("")
    
    lines.append("## 💻 Recommended Project")
    lines.append(f"**Project Name:** {report.get('project_name', 'N/A')}")
    lines.append(f"**Complexity:** {report.get('project_complexity', 'Intermediate')}")
    lines.append(f"**Description:** {report.get('project_description', 'N/A')}")
    lines.append("")
    
    lines.append("## 📅 Day-by-Day Preparation Plan Summary")
    lines.append(report.get("roadmap_summary", "No plan summary provided."))
    lines.append("")
    
    lines.append("## 📊 Subcategory Scores")
    for category, score in report.get("category_scores", {}).items():
        lines.append(f"- **{category}:** {score}/100")
    lines.append("")
    
    markdown_str = "\n".join(lines)
    
    if output_path:
        dir_name = os.path.dirname(os.path.abspath(output_path))
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_str)
            
    return markdown_str

# Compatibility wrapper class for earlier unit tests assertions
class ExportTools:
    @staticmethod
    def export_as_markdown(report_data: Dict[str, Any], output_path: str) -> bool:
        try:
            mapped_report = {
                "role": report_data.get("role", "N/A"),
                "match_score": report_data.get("match_score", 0.0),
                "project_name": report_data.get("project", "N/A"),
                "roadmap_summary": report_data.get("roadmap", "N/A")
            }
            export_markdown_report(mapped_report, output_path)
            return True
        except Exception as e:
            print(f"Export compatibility failed: {e}")
            return False
