from llm_client import LLMClient

class ReadmeAgent:
    """
    ReadmeAgent drafts comprehensive, professional GitHub README.md templates
    for recommended student portfolio projects.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "README Agent"

    def generate_readme(self, project_name: str, tech_stack: list) -> str:
        """
        Generates GitHub repository README.md layout.
        """
        prompt = f"Write a professional GitHub README for a project named {project_name} using: {tech_stack}."
        return self.llm.generate(
            prompt=prompt,
            system_instruction="You are an open-source contributor. Draft clean, structured GitHub repository readmes."
        )
