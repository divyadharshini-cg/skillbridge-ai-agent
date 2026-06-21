from llm_client import LLMClient

class SkillGapAgent:
    """
    SkillGapAgent compares target role requirements against student's existing profile
    to identify matching strengths and critical missing skill gaps.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Skill Gap Agent"

    def analyze_gaps(self, student_skills: list, target_role_requirements: list) -> dict:
        """
        Calculates intersecting strengths and missing capabilities.
        """
        strengths = [skill for skill in student_skills if skill in target_role_requirements]
        gaps = [skill for skill in target_role_requirements if skill not in student_skills]
        
        return {
            "strengths": strengths,
            "gaps": gaps,
            "gap_count": len(gaps)
        }
