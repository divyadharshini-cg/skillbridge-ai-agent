from typing import List, Dict, Any
from llm_client import LLMClient, is_llm_available, polish_text
from tools.role_database import get_role_requirements

class InterviewAgent:
    """
    InterviewAgent drafts mock technical/behavioral interview questions
    based on target role requirements, student projects, and identified skill gaps.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Interview Agent"

    def generate_questions(self, target_role: str, gaps: List[str], project_name: str = "Portfolio Project") -> List[Dict[str, str]]:
        """
        Drafts a list of categorized mock interview questions (Technical, Project-based, HR, Coding).
        """
        role_reqs = get_role_requirements(target_role)
        topics = role_reqs.get("interview_topics", [])
        
        # Build category-specific fallbacks
        tech_question = "Explain how you manage dependency versioning and environments in your projects."
        if topics:
            tech_question = f"Explain the core principles of: '{topics[0]}'. How do you handle common issues associated with it?"
        elif gaps:
            tech_question = f"How do you approach learning and managing issues related to: {gaps[0]}?"

        project_question = f"Walk us through the architecture of your '{project_name}' project. What were the main technical challenges you faced, and how did you resolve them?"
        
        hr_question = f"Why are you interested in a '{target_role}' internship, and how do your current skills align with our company's needs?"
        
        # Select role-based coding question
        coding_question = "Coding Task: Write a Python function to check if a string is a valid palindrome, ignoring case and spacing."
        role_lower = target_role.lower()
        if "data analyst" in role_lower:
            coding_question = "Coding Task: Write a SQL query using window functions to calculate the month-over-month sales growth from a transactions table."
        elif "web developer" in role_lower or "ux" in role_lower:
            coding_question = "Coding Task: Write a JavaScript/React component that renders an input box filtering a list of names as the user types."
        elif "python" in role_lower or "ai" in role_lower or "ml" in role_lower or "scientist" in role_lower:
            coding_question = "Coding Task: Write a Python generator function that reads a large file line by line and yields lines matching a regex pattern, minimizing memory utilization."

        questions = [
            {"category": "Technical", "question": tech_question},
            {"category": "Project-based", "question": project_question},
            {"category": "HR", "question": hr_question},
            {"category": "Coding", "question": coding_question}
        ]

        # Use LLM to customize and write unique questions if API is active
        if is_llm_available():
            import json
            prompt = (
                f"Draft exactly 4 realistic mock interview questions for a student applying for {target_role}.\n"
                f"The candidate is missing these skills: {gaps}.\n"
                f"The candidate is building a portfolio project named: {project_name}.\n"
                f"Topics to cover: {topics}.\n"
                f"Draft one question for each category: Technical, Project-based, HR, and Coding.\n"
                f"Return as a JSON list of objects with keys 'category' and 'question'."
            )
            fallback_json = json.dumps(questions)
            response = polish_text(
                prompt=prompt,
                fallback_text=fallback_json,
                system_instruction="You are a professional technical interviewer. Return ONLY a valid JSON list of objects."
            )
            try:
                clean_json = response.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()
                
                parsed = json.loads(clean_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    questions = parsed
            except Exception:
                pass

        return questions
