from llm_client import LLMClient

class PortfolioProjectAgent:
    """
    PortfolioProjectAgent designs and schedules high-impact portfolio projects
    specifically optimized to demonstrate missing skill requirements.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Portfolio Project Agent"

    def recommend_project(self, gaps: list, target_role: str) -> dict:
        """
        Recommends a portfolio project description and components.
        """
        prompt = f"Design a portfolio project covering these skill gaps: {gaps} for the role of {target_role}."
        raw_recommendation = self.llm.generate(
            prompt=prompt,
            system_instruction="You are a senior tech lead. Propose high-impact project suggestions with architectural complexity."
        )
        return {
            "project_name": "Dynamic Scheduler Service",
            "description": raw_recommendation,
            "complexity": "Intermediate"
        }
