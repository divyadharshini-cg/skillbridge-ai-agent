import json
import re
from typing import Union, Dict, Any
from llm_client import LLMClient
from tools.matching_tools import MatchingTools

class ProfileAnalyzerAgent:
    """
    ProfileAnalyzerAgent parses the student resume text or inputs, extracts core metadata
    like name, education, branch, current skills, projects, target role, learning time,
    and deadline, and returns a structured dictionary.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Profile Analyzer Agent"

    def analyze(self, profile_data: Union[str, dict]) -> dict:
        """
        Parses resume/profile raw text or dictionary inputs and outputs structured profile details.
        """
        # If input is a dictionary, extract and apply defaults
        if isinstance(profile_data, dict):
            # Try to get raw profile_text if present for logging or backup
            raw_text = profile_data.get("profile_text") or profile_data.get("resume_text") or ""
            if not raw_text:
                # build dummy string for backup
                raw_text = f"Name: {profile_data.get('name')}\nTarget Role: {profile_data.get('target_role')}"
            
            # Standardize skills to list
            skills = profile_data.get("current_skills") or profile_data.get("skills") or []
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(",") if s.strip()]
                
            projects = profile_data.get("existing_projects") or profile_data.get("projects") or []
            if isinstance(projects, str):
                projects = [p.strip() for p in projects.split(",") if p.strip()]

            # Return normalized dictionary
            return {
                "name": profile_data.get("name") or "Student Candidate",
                "education": profile_data.get("education") or "N/A",
                "branch": profile_data.get("branch") or "N/A",
                "current_skills": skills,
                "existing_projects": projects,
                "target_role": profile_data.get("target_role") or "Software Engineer Intern",
                "resume_text": raw_text,
                "learning_time": float(profile_data.get("learning_time") or profile_data.get("hours_per_day") or 2.0),
                "deadline": int(profile_data.get("deadline") or profile_data.get("days_left") or 30)
            }

        # Otherwise, if input is a string, use LLM or fallback deterministic regex parsing
        profile_text = profile_data or ""
        
        extracted = {
            "name": "Student Candidate",
            "education": "N/A",
            "branch": "N/A",
            "current_skills": [],
            "existing_projects": [],
            "target_role": "Software Engineer Intern",
            "resume_text": profile_text,
            "learning_time": 2.0,
            "deadline": 30
        }

        # Try LLM first if not in mock mode
        if not self.llm.is_mock:
            prompt = (
                "Parse the following resume/profile text and extract these fields in valid JSON format:\n"
                "- name\n- education\n- branch\n- current_skills (JSON array of strings)\n"
                "- existing_projects (JSON array of strings)\n- target_role\n"
                "- learning_time (float, default 2.0)\n- deadline (integer, default 30)\n\n"
                f"Profile Text:\n{profile_text}"
            )
            try:
                response = self.llm.generate(
                    prompt=prompt,
                    system_instruction="You are an expert resume parsing assistant. Return ONLY a valid JSON object matching the requested schema."
                )
                # Clean markdown JSON block tags if any
                clean_json = response.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()
                
                parsed = json.loads(clean_json)
                extracted.update(parsed)
                return extracted
            except Exception:
                # LLM extraction failed, fallback to deterministic parser below
                pass

        # Deterministic Fallback Parser
        # Look for explicit field labels in the text
        for line in profile_text.splitlines():
            line_strip = line.strip()
            if not line_strip:
                continue
                
            # Lowercase for check, but extract original value
            lower_line = line_strip.lower()
            
            if any(lower_line.startswith(p) for p in ["name:", "student name:"]):
                extracted["name"] = line_strip.split(':', 1)[1].strip()
            elif any(lower_line.startswith(p) for p in ["education:", "degree:", "university:"]):
                extracted["education"] = line_strip.split(':', 1)[1].strip()
            elif any(lower_line.startswith(p) for p in ["branch:", "department:", "major:"]):
                extracted["branch"] = line_strip.split(':', 1)[1].strip()
            elif any(lower_line.startswith(p) for p in ["skills:", "core skills:", "existing skills:"]):
                val = line_strip.split(':', 1)[1].strip()
                extracted["current_skills"] = [s.strip() for s in val.split(",") if s.strip()]
            elif any(lower_line.startswith(p) for p in ["projects:", "existing projects:"]):
                val = line_strip.split(':', 1)[1].strip()
                extracted["existing_projects"] = [p.strip() for p in val.split(",") if p.strip()]
            elif any(lower_line.startswith(p) for p in ["target role:", "role:", "target:"]):
                extracted["target_role"] = line_strip.split(':', 1)[1].strip()
            elif any(lower_line.startswith(p) for p in ["learning time:", "hours:", "hours per day:"]):
                try:
                    val = line_strip.split(':', 1)[1].strip()
                    extracted["learning_time"] = float(re.search(r'[\d.]+', val).group())
                except Exception:
                    pass
            elif any(lower_line.startswith(p) for p in ["deadline:", "days:", "days left:"]):
                try:
                    val = line_strip.split(':', 1)[1].strip()
                    extracted["deadline"] = int(re.search(r'\d+', val).group())
                except Exception:
                    pass

        # If no skills were explicitly parsed, search the entire text for common keywords
        if not extracted["current_skills"]:
            extracted["current_skills"] = MatchingTools.extract_keywords(profile_text)

        return extracted
