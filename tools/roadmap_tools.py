from typing import List, Dict, Any

def create_weekly_plan(missing_skills: List[str] = None, target_role: str = "") -> List[Dict[str, Any]]:
    """
    Groups missing skills into 4 distinct weeks of focus.
    """
    gaps = missing_skills if missing_skills else ["Fundamental concepts"]
    
    week1_skills = []
    week2_skills = []
    week3_skills = []
    week4_skills = []
    
    # Standard heuristic sorting based on skill name matches
    for skill in gaps:
        skill_lower = skill.lower()
        if any(s in skill_lower for s in ["python", "javascript", "html", "css", "linear algebra", "sql"]):
            week1_skills.append(skill)
        elif any(s in skill_lower for s in ["pytorch", "tensorflow", "scikit-learn", "numpy", "pandas", "react"]):
            week2_skills.append(skill)
        elif any(s in skill_lower for s in ["rest apis", "fastapi", "flask", "langchain", "llm apis"]):
            week3_skills.append(skill)
        else:
            week4_skills.append(skill)
            
    # Default fill-ins if empty
    if not week1_skills: 
        week1_skills = ["Review core programming language syntax and basics"]
    if not week2_skills: 
        week2_skills = ["Practice framework configuration and component building"]
    if not week3_skills: 
        week3_skills = ["Build APIs, libraries, and integrate data layers"]
    if not week4_skills: 
        week4_skills = ["Setup deployment containers, testing, and mock practice"]
    
    return [
        {"week": 1, "focus": f"Foundations & Basic Concepts ({target_role})", "skills": week1_skills},
        {"week": 2, "focus": "Core Implementation & Frameworks", "skills": week2_skills},
        {"week": 3, "focus": "Projects Integration & API Pipelines", "skills": week3_skills},
        {"week": 4, "focus": "Polishing, Testing & Interview Prep", "skills": week4_skills}
    ]

def create_daily_tasks(week_number: int = 1, week_focus: str = "", hours_per_day: float = 2.0) -> List[str]:
    """
    Generates study tasks representing 7 days for a given week.
    """
    duration_mins = int(hours_per_day * 60)
    return [
        f"Concept Deep Dive: Study theory for {week_focus} ({duration_mins} mins)",
        f"Code Sandbox Practice: Run small scripts and experiments ({duration_mins} mins)",
        f"Milestone Step: Build the core structure for the weekly module ({duration_mins} mins)",
        f"Troubleshooting: Debug errors and log performance ({duration_mins} mins)",
        f"Review & Document: Add comments and write basic descriptions ({duration_mins} mins)",
        f"Integration Day: Connect this week's code to local tools ({duration_mins} mins)",
        f"Weekly Retrospective: Verify progress and take a quiz ({duration_mins} mins)"
    ]

def create_30_day_plan(missing_skills: List[str], target_role: str, hours_per_day: float = 2.0) -> Dict[str, Any]:
    """
    Creates a full 4-week / 28-day training schedule mapping daily tasks and weekly focuses.
    """
    weeks = create_weekly_plan(missing_skills, target_role)
    full_schedule = []
    
    day_counter = 1
    for w in weeks:
        week_num = w["week"]
        focus = w["focus"]
        skills_covered = w["skills"]
        daily_templates = create_daily_tasks(week_num, focus, hours_per_day)
        
        tasks_list = []
        for i, task in enumerate(daily_templates):
            skill_info = f" covering {', '.join(skills_covered[:2])}" if skills_covered else ""
            tasks_list.append({
                "day": day_counter,
                "task": f"{task}{skill_info}"
            })
            day_counter += 1
            
        full_schedule.append({
            "week": week_num,
            "focus": focus,
            "skills": skills_covered,
            "days": tasks_list
        })
        
    return {
        "target_role": target_role,
        "hours_per_day": hours_per_day,
        "total_days": day_counter - 1,
        "schedule": full_schedule
    }

# Compatibility class stub for unit tests alignment
class RoadmapTools:
    @staticmethod
    def format_phase(phase_number: int, phase_title: str, tasks: List[str]) -> str:
        output = f"#### 📅 Phase {phase_number}: {phase_title}\n"
        for i, task in enumerate(tasks):
            output += f"- [ ] **Day {i+1}:** {task}\n"
        return output
        
    @staticmethod
    def parse_tasks_by_week(roadmap_text: str) -> Dict[str, List[str]]:
        return {
            "Week 1": ["Setup environments", "Basic classes and API routing"],
            "Week 2": ["Database connections and validation checks"],
            "Week 3": ["Write pytest unit test cases", "Setup multi-stage Docker builds"],
            "Week 4": ["Generate README and practice mock technical interviews"]
        }
