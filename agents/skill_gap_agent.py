from typing import List, Union, Any
from llm_client import LLMClient
from tools.role_database import get_role_requirements
from tools.matching_tools import match_skills_to_role, rank_skill_gaps

class SkillGapAgent:
    """
    SkillGapAgent compares target role requirements against student's existing profile
    to identify matching strengths and critical missing skill gaps.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Skill Gap Agent"

    def analyze_gaps(self, student_skills: List[str], target_role: Union[str, List[str]]) -> dict:
        """
        Calculates intersecting strengths, missing capabilities, priority ranks the gaps,
        and provides a technical gap analysis summary.
        """
        if not student_skills:
            student_skills = []

        # Load requirements from role database if target_role is string, otherwise treat as skill list
        if isinstance(target_role, str):
            role_name = target_role
            role_reqs = get_role_requirements(target_role)
            required_skills = role_reqs.get("required_skills", [])
        else:
            role_name = "Target Role"
            required_skills = target_role if isinstance(target_role, list) else []

        # Use matching tools to compare
        match_data = match_skills_to_role(student_skills, required_skills)
        matching_skills = match_data["matching_skills"]
        missing_skills = match_data["missing_skills"]
        
        # Rank missing skills
        ranked_gaps = rank_skill_gaps(missing_skills)

        # Build default explanation
        high_gaps = [g["skill"] for g in ranked_gaps if g["priority"] == "High"]
        med_gaps = [g["skill"] for g in ranked_gaps if g["priority"] == "Medium"]
        low_gaps = [g["skill"] for g in ranked_gaps if g["priority"] == "Low"]

        explanation_lines = [
            f"Skill Gap Analysis for target role: **{role_name}**.",
            f"You possess {len(matching_skills)} of the {len(required_skills)} required skills.",
            ""
        ]

        if matching_skills:
            explanation_lines.append(f"**Strengths:** {', '.join(matching_skills)}")
        else:
            explanation_lines.append("**Strengths:** None identified yet for this role.")

        if missing_skills:
            explanation_lines.append(f"**Identified Gaps ({len(missing_skills)} missing):**")
            if high_gaps:
                explanation_lines.append(f"- *High Priority (Immediate Focus):* {', '.join(high_gaps)}")
            if med_gaps:
                explanation_lines.append(f"- *Medium Priority (Core Frameworks):* {', '.join(med_gaps)}")
            if low_gaps:
                explanation_lines.append(f"- *Low Priority (Tooling/Pipelines):* {', '.join(low_gaps)}")
        else:
            explanation_lines.append("Excellent! You match all required skills for this role.")

        explanation = "\n".join(explanation_lines)

        # Enhance with LLM if API is active
        if not self.llm.is_mock and required_skills:
            prompt = (
                f"Evaluate this skill gap analysis for a student targeting {role_name}:\n"
                f"Current Skills: {student_skills}\n"
                f"Required Skills: {required_skills}\n"
                f"Matching Skills: {matching_skills}\n"
                f"Missing Skills: {missing_skills}\n"
                f"Ranked Gaps: {ranked_gaps}\n"
                f"Write a concise technical coaching review detailing where they stand and how they should prioritize learning."
            )
            try:
                llm_explanation = self.llm.generate(
                    prompt=prompt,
                    system_instruction="You are an expert technical recruiter and career coach. Review skill gaps and offer prioritizing advice."
                )
                explanation = llm_explanation
            except Exception:
                pass

        return {
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "ranked_gaps": ranked_gaps,
            "explanation": explanation
        }
