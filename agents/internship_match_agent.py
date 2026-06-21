from llm_client import LLMClient

class InternshipMatchAgent:
    """
    InternshipMatchAgent assesses candidate compatibility with specific target
    internship listings, calculating fit index percentages.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Internship Match Agent"

    def evaluate_fit(self, student_profile: dict, job_listing: dict) -> dict:
        """
        Evaluate compatibility metrics and offer suitability commentary.
        """
        # Placeholder match logic
        return {
            "compatibility_percentage": 75.0,
            "fit_level": "Good Fit",
            "reasoning": "Candidate possesses basic matching requirements but is missing backend test coverage experience."
        }
