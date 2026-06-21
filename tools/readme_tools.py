from typing import Dict, Any, List

def generate_project_readme(project_details: Dict[str, Any]) -> str:
    """
    Generates a structured, professional Markdown GitHub README based on project metadata.
    """
    name = project_details.get("name", "SkillBridge Recommended Project")
    description = project_details.get("description", "A portfolio booster project designed to cover specific skill gaps.")
    tech_stack = project_details.get("tech_stack", [])
    
    milestones = project_details.get("milestones", [
        "Initialize local project directories and specify setup configs.",
        "Implement core structural modules and business logic schemas.",
        "Establish comprehensive automated unit tests.",
        "Setup container deployment packages and write user manuals."
    ])
    
    setup_steps = project_details.get("setup_steps", [
        "Clone the repository to your local directory.",
        "Build a Python virtual environment: `python -m venv venv`.",
        "Install dependency packages: `pip install -r requirements.txt`.",
        "Start the application: `python main.py` or run container configurations."
    ])
    
    # Generate badges markdown list
    badges = []
    for tech in tech_stack:
        clean_tech = tech.replace(" ", "%20")
        badges.append(f"![{tech}](https://img.shields.io/badge/{clean_tech}-4F46E5.svg)")
        
    badge_header = " ".join(badges)
    
    readme_lines = [
        f"# {name}",
        "",
        badge_header if badge_header else "![Status](https://img.shields.io/badge/Status-Scaffolding-blue.svg)",
        "",
        "## 📝 Description",
        description,
        "",
        "## 💻 Tech Stack",
    ]
    
    for tech in tech_stack:
        readme_lines.append(f"- **{tech}**")
    readme_lines.append("")
    
    readme_lines.append("## 🎯 Key Milestones")
    for i, m in enumerate(milestones):
        readme_lines.append(f"{i+1}. **Phase {i+1}:** {m}")
    readme_lines.append("")
    
    readme_lines.append("## ⚙️ Setup & Getting Started")
    for i, step in enumerate(setup_steps):
        readme_lines.append(f"{i+1}. {step}")
    readme_lines.append("")
    
    readme_lines.append("## 📄 License")
    readme_lines.append("This project is licensed under the MIT License.")
    
    return "\n".join(readme_lines)

# Compatibility class stub
class ReadmeTools:
    @staticmethod
    def wrap_code_block(code: str, language: str = "markdown") -> str:
        return f"```{language}\n{code.strip()}\n```"

    @staticmethod
    def generate_badge_markdown(badge_type: str, color: str = "blue") -> str:
        clean_type = badge_type.replace(" ", "%20")
        return f"![{badge_type}](https://img.shields.io/badge/{clean_type}-{color}.svg)"
