from typing import Union, List, Any
from llm_client import LLMClient, is_llm_available, polish_text
from tools.readme_tools import generate_project_readme, ReadmeTools

class ReadmeAgent:
    """
    ReadmeAgent drafts comprehensive, professional GitHub README.md templates
    for recommended student portfolio projects.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "README Agent"

    def generate_readme(self, project_data: Union[str, dict], tech_stack: List[str] = None) -> str:
        """
        Generates GitHub repository README.md layout.
        Supports both (project_name, tech_stack) string-based and dictionary-based project specifications.
        """
        if isinstance(project_data, str):
            # Signature backward compatibility
            project_name = project_data
            tech_stack_list = tech_stack or []
            project_details = {
                "name": project_name,
                "description": f"A professional portfolio booster project designed to showcase skill requirements using {', '.join(tech_stack_list)}.",
                "tech_stack": tech_stack_list,
                "milestones": [
                    "Initialize local files and package configuration settings.",
                    "Write core backend endpoints, components, and controllers.",
                    "Create automated test suite with pytest integration.",
                    "Deploy code packages inside Docker containers."
                ],
                "setup_steps": [
                    "Clone the repository to your local computer.",
                    "Create your virtual env and activate it: 'python -m venv venv'.",
                    "Install required package listings: 'pip install -r requirements.txt'.",
                    "Launch the code runner or web server: 'python main.py'."
                ]
            }
        else:
            # Dictionary input signature
            details = project_data or {}
            project_name = details.get("title") or details.get("project_name") or "SkillBridge Recommended Project"
            tech_stack_list = details.get("tech_stack") or []
            
            project_details = {
                "name": project_name,
                "description": details.get("problem") or details.get("description") or "A professional portfolio booster project.",
                "tech_stack": tech_stack_list,
                "milestones": details.get("features") or [
                    "Establish core architecture modules.",
                    "Implement business logic interfaces.",
                    "Achieve high test coverage."
                ],
                "setup_steps": details.get("setup_steps") or [
                    "Clone this repository.",
                    "Install environment libraries and project packages.",
                    "Run unit tests using pytest.",
                    "Execute deployment container options."
                ]
            }

        # Deterministic generation using tools
        readme_markdown = generate_project_readme(project_details)

        # LLM enrichment if key is active
        if is_llm_available():
            prompt = (
                f"Create a beautiful, detailed, professional GitHub README.md for a project named {project_name}.\n"
                f"Project Details:\n{project_details}\n"
                f"Include sections: Title, Description, Features, Tech Stack (with markdown badges), Getting Started, and License."
            )
            readme_markdown = polish_text(
                prompt=prompt,
                fallback_text=readme_markdown,
                system_instruction="You are an open-source contributor. Draft clean, structured GitHub repository readmes."
            )

        return readme_markdown
