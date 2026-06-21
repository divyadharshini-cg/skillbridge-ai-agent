from llm_client import LLMClient

class RoadmapAgent:
    """
    RoadmapAgent constructs a personalized 30-day day-by-day learning path
    aimed at mitigating identified skill gaps.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Roadmap Agent"

    def generate_roadmap(self, gaps: list, target_role: str) -> str:
        """
        Creates a markdown 30-day roadmap tailored to the target role and skill gaps.
        """
        prompt = f"Create a 30-day preparation roadmap to close these skill gaps: {gaps} for target role: {target_role}."
        return self.llm.generate(
            prompt=prompt,
            system_instruction="You are a professional technical career coach. Draft structural, day-by-day learning schedules."
        )
