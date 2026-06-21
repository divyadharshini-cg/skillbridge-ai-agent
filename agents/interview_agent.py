from llm_client import LLMClient

class InterviewAgent:
    """
    InterviewAgent drafts mock technical/behavioral interview questions
    and simulates responses based on resume content and skill gaps.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Interview Agent"

    def generate_questions(self, target_role: str, gaps: list) -> list:
        """
        Drafts a list of target interview questions based on gaps.
        """
        prompt = f"Generate 3 mock interview questions for role: {target_role} addressing these gaps: {gaps}."
        raw_response = self.llm.generate(
            prompt=prompt,
            system_instruction="You are a tech interviewer. Create realistic screening questions."
        )
        # Fallback list representation
        return [
            f"How do you approach managing issues related to: {gaps[0] if gaps else 'software design'}?",
            "Can you discuss a time you resolved a technical challenge under strict constraints?",
            "Detail your experience or knowledge about modern API structures."
        ]
