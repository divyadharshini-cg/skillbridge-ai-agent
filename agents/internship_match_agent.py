from typing import List, Dict, Any
from llm_client import LLMClient
from tools.role_database import load_role_database
from tools.scoring_tools import ScoringTools
from tools.matching_tools import MatchingTools, match_skills_to_role

class InternshipMatchAgent:
    """
    InternshipMatchAgent assesses candidate compatibility with specific target
    internship listings, and recommends suitable matches from the role database.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Internship Match Agent"

    def evaluate_fit(self, student_profile: Dict[str, Any], job_listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate compatibility metrics and offer suitability commentary.
        """
        student_skills = student_profile.get("current_skills", [])
        required_skills = job_listing.get("required_skills", [])
        role_name = job_listing.get("role", "Target Role")
        
        score = ScoringTools.calculate_match_percentage(student_skills, required_skills)
        fit_level = MatchingTools.get_match_level(score)
        match_data = match_skills_to_role(student_skills, required_skills)
        
        reasoning = f"Candidate possesses {len(match_data['matching_skills'])} matching skills ({', '.join(match_data['matching_skills'])}) but is missing {len(match_data['missing_skills'])} requirements."
        
        if not self.llm.is_mock:
            prompt = (
                f"Evaluate fit for student targeting {role_name}:\n"
                f"Student Skills: {student_skills}\n"
                f"Job Requirements: {required_skills}\n"
                f"Matching: {match_data['matching_skills']}\n"
                f"Missing: {match_data['missing_skills']}\n"
                f"Provide a brief 2-sentence explanation of suitability."
            )
            try:
                reasoning = self.llm.generate(
                    prompt=prompt,
                    system_instruction="You are an internship recruiter assessing profile compatibility."
                )
            except Exception:
                pass
                
        return {
            "compatibility_percentage": score,
            "fit_level": fit_level,
            "reasoning": reasoning
        }

    def suggest_matches(self, student_skills: List[str]) -> List[Dict[str, Any]]:
        """
        Loads all roles from the database, computes compatibility scores,
        ranks them, and generates fit explanations.
        """
        role_db = load_role_database()
        matches = []
        
        for role_name, details in role_db.items():
            required_skills = details.get("required_skills", [])
            score = ScoringTools.calculate_match_percentage(student_skills, required_skills)
            fit_level = MatchingTools.get_match_level(score)
            match_data = match_skills_to_role(student_skills, required_skills)
            
            # Default explanation
            matching_str = ", ".join(match_data["matching_skills"]) if match_data["matching_skills"] else "None"
            explanation = (
                f"This role is a {fit_level} (Score: {score:.1f}%). "
                f"You already have {len(match_data['matching_skills'])} matching skills: {matching_str}."
            )
            
            if not self.llm.is_mock:
                prompt = (
                    f"Explain why the role {role_name} fits a student with these skills:\n"
                    f"Student skills: {student_skills}\n"
                    f"Role required skills: {required_skills}\n"
                    f"Role description details: {details.get('recommended_projects')}"
                )
                try:
                    explanation = self.llm.generate(
                        prompt=prompt,
                        system_instruction="You are a career counselor. Explain why this role matches or does not match the student's skills."
                    )
                except Exception:
                    pass
            
            matches.append({
                "role_name": role_name,
                "match_score": score,
                "fit_level": fit_level,
                "matching_skills": match_data["matching_skills"],
                "missing_skills": match_data["missing_skills"],
                "explanation": explanation
            })
            
        # Sort by match score in descending order
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches
