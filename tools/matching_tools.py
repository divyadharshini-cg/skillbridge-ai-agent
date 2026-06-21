from typing import List, Dict, Any

def normalize_skills(skills: List[str]) -> List[str]:
    """
    Standardizes spelling and capitalization of a list of skills by
    stripping whitespace, lowercasing, and removing duplicates.
    """
    normalized = set()
    for s in skills:
        if isinstance(s, str):
            clean = s.strip().lower()
            if clean:
                normalized.add(clean)
    return sorted(list(normalized))

def match_skills_to_role(current_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
    """
    Compares the student's current skills against required role skills.
    Returns overlapping matches and missing gaps.
    """
    curr_norm = set(normalize_skills(current_skills))
    req_norm = set(normalize_skills(required_skills))
    
    matches = curr_norm.intersection(req_norm)
    missing = req_norm.difference(curr_norm)
    
    return {
        "matching_skills": sorted(list(matches)),
        "missing_skills": sorted(list(missing)),
        "match_count": len(matches),
        "missing_count": len(missing)
    }

def find_missing_skills(current_skills: List[str], required_skills: List[str]) -> List[str]:
    """
    Returns a sorted list of required skills that are not present in current_skills.
    """
    curr_norm = set(normalize_skills(current_skills))
    req_norm = set(normalize_skills(required_skills))
    return sorted(list(req_norm.difference(curr_norm)))

def rank_skill_gaps(missing_skills: List[str]) -> List[Dict[str, Any]]:
    """
    Ranks missing skills by hierarchy priority. Language and core database concepts
    are marked as High priority, frameworks as Medium, and optional container/pipeline tools as Low.
    """
    priority_map = {
        # Programming & Languages
        "python": (1, "High"),
        "javascript": (1, "High"),
        "html5": (2, "High"),
        "css3": (2, "High"),
        "linear algebra": (2, "High"),
        "sql": (2, "High"),
        # Core Libraries & Frameworks
        "pytorch": (3, "Medium"),
        "tensorflow": (3, "Medium"),
        "scikit-learn": (3, "Medium"),
        "react": (3, "Medium"),
        "numpy": (3, "Medium"),
        "pandas": (3, "Medium"),
        "rest apis": (3, "Medium"),
        "data visualization": (3, "Medium"),
        # Tooling & Environments
        "git": (4, "Medium"),
        "excel": (4, "Medium"),
        "docker": (5, "Low"),
        "langchain": (5, "Low"),
        "llm apis": (5, "Low"),
        "prompt engineering": (5, "Low"),
    }
    
    ranked = []
    for skill in missing_skills:
        clean = skill.strip().lower()
        priority_val, priority_label = priority_map.get(clean, (4, "Medium"))
        ranked.append({
            "skill": skill,
            "priority_rank": priority_val,
            "priority": priority_label
        })
        
    # Sort by priority rank number, then alphabetically by skill name
    ranked.sort(key=lambda x: (x["priority_rank"], x["skill"].lower()))
    return ranked

# Compatibility class stub
class MatchingTools:
    @staticmethod
    def get_match_level(score: float) -> str:
        if score >= 85.0:
            return "Strong Fit"
        elif score >= 60.0:
            return "Good Fit"
        elif score >= 40.0:
            return "Moderate Fit"
        else:
            return "Requires Work"

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        common_tech = ["python", "javascript", "react", "fastapi", "docker", "sql", "git", "aws"]
        found = []
        lowered = text.lower()
        for tech in common_tech:
            if tech in lowered:
                found.append(tech.capitalize())
        return found
