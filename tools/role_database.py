import os
import json
from typing import Dict, List, Any

def load_role_database() -> Dict[str, Any]:
    """
    Loads the complete role requirements JSON database.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "role_requirements.json")
    
    if not os.path.exists(data_path):
        return {}
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading role requirements database: {e}")
        return {}

def get_role_requirements(role_name: str) -> Dict[str, Any]:
    """
    Returns the requirements dictionary for a specific role.
    If the role is not found, returns a standard empty requirements schema.
    """
    db = load_role_database()
    return db.get(role_name, {
        "required_skills": [],
        "optional_skills": [],
        "recommended_projects": [],
        "interview_topics": [],
        "tools_to_learn": []
    })

def list_available_roles() -> List[str]:
    """
    Returns a list of all role names stored in the database.
    """
    db = load_role_database()
    return list(db.keys())

# Class-based wrapper to ensure backward compatibility with earlier imports
class RoleDatabase:
    def __init__(self, data_path: str = None) -> None:
        self.data_path = data_path

    def load_requirements(self) -> Dict[str, Any]:
        return load_role_database()

    def get_role_details(self, role_name: str) -> Dict[str, Any]:
        return get_role_requirements(role_name)
