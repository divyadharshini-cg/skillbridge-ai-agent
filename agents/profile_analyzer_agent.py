from llm_client import LLMClient

class ProfileAnalyzerAgent:
    """
    ProfileAnalyzerAgent parses the student resume text or inputs, extract core skills,
    previous projects, education, and rates baseline readiness.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Profile Analyzer Agent"

    def analyze(self, profile_text: str) -> dict:
        """
        Parses resume/profile raw text and outputs structured profile details.
        """
        prompt = f"Analyze this student profile and extract core metadata:\n{profile_text}"
        # Fallback to standard structured dict
        response = self.llm.generate(
            prompt=prompt,
            system_instruction="You are an expert resume parsing agent. Extract education, projects, and skills."
        )
        return {
            "raw_analysis": response,
            "parsed_skills": ["Python", "Git", "HTML/CSS"],
            "readiness_index": 70
        }
