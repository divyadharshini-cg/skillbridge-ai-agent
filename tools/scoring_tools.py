from typing import List, Dict, Any, Optional

def calculate_readiness_score(current_skills: List[str], required_skills: List[str]) -> int:
    """
    Calculates overall readiness index (0-100) based on overlapping required skills.
    If no required skills are defined, defaults to 100.
    """
    if not required_skills:
        return 100
        
    curr_norm = set(s.strip().lower() for s in current_skills)
    req_norm = set(r.strip().lower() for r in required_skills)
    
    matches = curr_norm.intersection(req_norm)
    score = (len(matches) / len(req_norm)) * 100.0
    return int(round(score))

def calculate_category_scores(
    current_skills: List[str], 
    role_name: str, 
    projects: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, int]:
    """
    Calculates category scores out of 100 representing readiness across key areas:
    Programming, Data/ML, Tools/GitHub, Projects, Interview Readiness, and Deployment.
    """
    curr_norm = set(s.strip().lower() for s in current_skills)
    
    # Skills maps
    prog_skills = {"python", "javascript", "react", "html5", "css3", "fastapi", "flask", "object-oriented programming (oop)", "rest apis", "restful api design standards"}
    data_ml_skills = {"numpy", "pandas", "scikit-learn", "pytorch", "tensorflow", "linear algebra", "sql", "statsmodels", "statistics", "langchain", "llm apis", "prompt engineering", "llamaindex", "vector databases", "rag", "chromadb"}
    tools_git_skills = {"git", "excel", "npm/yarn", "npm", "yarn", "webpack", "chrome devtools", "vs code", "figma", "github", "git/github"}
    deploy_skills = {"docker", "redis", "celery", "kubernetes", "aws", "gcp", "google cloud", "heroku", "github pages"}
    
    # Overlap computations
    prog_count = len(curr_norm.intersection(prog_skills))
    data_ml_count = len(curr_norm.intersection(data_ml_skills))
    tools_git_count = len(curr_norm.intersection(tools_git_skills))
    deploy_count = len(curr_norm.intersection(deploy_skills))
    
    # Base normalization multipliers
    programming_score = min(prog_count * 25, 100) if prog_count > 0 else 10
    data_ml_score = min(data_ml_count * 25, 100) if data_ml_count > 0 else 10
    tools_github_score = min(tools_git_count * 35, 100) if tools_git_count > 0 else 15
    deployment_score = min(deploy_count * 50, 100) if deploy_count > 0 else 0
    
    # Projects score
    if projects:
        projects_score = min(len(projects) * 50, 100)
    else:
        # Fallback to general skill indication
        projects_score = 40 if len(curr_norm) > 2 else 10
        
    # Interview readiness check
    readiness_keys = {"python", "javascript", "sql", "git"}
    readiness_hits = len(curr_norm.intersection(readiness_keys))
    interview_score = min(readiness_hits * 25, 100) if readiness_hits > 0 else 10
    
    return {
        "Programming": programming_score,
        "Data/ML": data_ml_score,
        "Tools/GitHub": tools_github_score,
        "Projects": projects_score,
        "Interview Readiness": interview_score,
        "Deployment": deployment_score
    }

# Compatibility class to maintain alignment with unit tests in test_scoring_tools.py
class ScoringTools:
    @staticmethod
    def calculate_match_percentage(student_skills: List[str], required_skills: List[str]) -> float:
        if not required_skills:
            return 100.0
        curr_norm = set(s.strip().lower() for s in student_skills)
        req_norm = set(r.strip().lower() for r in required_skills)
        matches = curr_norm.intersection(req_norm)
        return (len(matches) / len(req_norm)) * 100.0

    @staticmethod
    def compute_readiness_index(match_percentage: float, honesty_score: int) -> int:
        score = (match_percentage * 0.7) + (honesty_score * 0.3)
        return int(round(score))
