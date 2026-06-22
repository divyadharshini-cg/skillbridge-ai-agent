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
        lines = profile_text.splitlines()

        def normalize_text(text: str) -> str:
            return re.sub(r'^[\s\-\*•]+', '', text).strip()

        def append_field(field: str, value: str):
            if not value:
                return
            value = value.strip()
            if not value:
                return
            if extracted[field] in ("N/A", "", "Student Candidate", "Software Engineer Intern"):
                extracted[field] = value
            elif value not in extracted[field]:
                extracted[field] = f"{extracted[field]}, {value}"

        def set_field(field: str, value: str):
            if not value:
                return
            extracted[field] = value.strip()

        def parse_branch_from_degree(text: str) -> str:
            candidate = text.strip()
            candidate = re.sub(r'^(education|degree|program|course|qualification)[:\s\-]*', '', candidate, flags=re.I).strip()
            match = re.search(
                r'(?:(?:B\.?Tech|B\.?E\.?|BE|Bachelor(?: of(?: Science| Technology| Engineering)?)?|Bachelors?)(?:\s*(?:in|with))?)\s*(?P<branch>.+)$',
                candidate,
                flags=re.I
            )
            if match:
                branch_text = match.group('branch').strip()
                branch_text = re.sub(r'\b(?:\d+(?:st|nd|rd|th)|first|second|third|final)\s+year\b.*$', '', branch_text, flags=re.I).strip()
                branch_text = re.sub(r'\s*undergraduate\s*$', '', branch_text, flags=re.I).strip()
                return branch_text
            return ""

        def infer_branch_from_education(education_text: str) -> str:
            if not education_text or education_text in ("N/A", ""):
                return ""
            branch_text = parse_branch_from_degree(education_text)
            if branch_text:
                return branch_text
            year_start = re.match(r'^(?:\d+(?:st|nd|rd|th)|first|second|third|final)\s+year\s*(?:undergraduate)?\s*(?P<branch>.+)$', education_text, flags=re.I)
            if year_start:
                branch = year_start.group('branch').strip()
                return re.sub(r'\s*undergraduate\s*$', '', branch, flags=re.I).strip()
            branch_text = re.sub(r'\b(?:\d+(?:st|nd|rd|th)|first|second|third|final)\s+year\b.*$', '', education_text, flags=re.I).strip(' ,')
            branch_text = re.sub(r'\s*undergraduate\s*$', '', branch_text, flags=re.I).strip()
            if branch_text and branch_text.lower() != education_text.lower():
                return branch_text
            if re.fullmatch(r'[A-Za-z0-9&\s\.\-]{3,100}', education_text):
                return education_text.strip()
            return ""

        label_prefixes = [
            "name:", "student name:",
            "education:", "degree:", "university:", "course:", "program:", "qualification:",
            "branch:", "department:", "major:", "branch/major:",
            "skills:", "core skills:", "existing skills:",
            "projects:", "existing projects:",
            "target role:", "role:", "target:",
            "learning time:", "hours:", "hours per day:",
            "deadline:", "days:", "days left:"
        ]

        for idx, line in enumerate(lines):
            line_strip = normalize_text(line)
            if not line_strip:
                continue

            lower_line = line_strip.lower()

            if any(lower_line.startswith(p) for p in ["name:", "student name:"]):
                append_field("name", line_strip.split(':', 1)[1])
            elif any(lower_line.startswith(p) for p in ["education:", "degree:", "university:", "course:", "program:", "qualification:"]):
                value = line_strip.split(':', 1)[1].strip()
                if value:
                    append_field("education", value)
                else:
                    block_lines = []
                    for next_line in lines[idx + 1:]:
                        next_strip = normalize_text(next_line)
                        next_lower = next_strip.lower()
                        if not next_strip or any(next_lower.startswith(prefix) for prefix in label_prefixes):
                            break
                        block_lines.append(next_strip)
                    if block_lines:
                        append_field("education", " ".join(block_lines))
                if extracted["branch"] in ("N/A", ""):
                    branch_candidate = parse_branch_from_degree(value or (" ".join(block_lines) if value == "" else ""))
                    if branch_candidate:
                        extracted["branch"] = branch_candidate
            elif any(lower_line.startswith(p) for p in ["branch:", "department:", "major:", "branch/major:"]):
                set_field("branch", line_strip.split(':', 1)[1])
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
            elif re.search(r'\b(?:B\.?Tech|B\.?E\.?|BE|Bachelor(?: of(?: Science| Technology| Engineering)?)?|Bachelors?)\b', line_strip, flags=re.I):
                append_field("education", line_strip)
                if extracted["branch"] in ("N/A", ""):
                    branch_candidate = parse_branch_from_degree(line_strip)
                    if branch_candidate:
                        extracted["branch"] = branch_candidate
            elif re.search(r'\b(?:2nd|3rd|4th|final|second|third|first)\s+year\b', lower_line, flags=re.I):
                append_field("education", line_strip)

        if extracted["branch"] in ("N/A", "") and extracted["education"] not in ("N/A", ""):
            branch_candidate = infer_branch_from_education(extracted["education"])
            if branch_candidate and branch_candidate.lower() != extracted["education"].lower():
                extracted["branch"] = branch_candidate

        if not extracted["current_skills"]:
            extracted["current_skills"] = MatchingTools.extract_keywords(profile_text)

        return extracted
