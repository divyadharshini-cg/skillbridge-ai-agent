from typing import List, Dict, Any
from llm_client import LLMClient, is_llm_available, polish_text
from tools.roadmap_tools import create_30_day_plan, RoadmapTools

class RoadmapAgent:
    """
    RoadmapAgent constructs a personalized 30-day day-by-day learning path
    aimed at mitigating identified skill gaps.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Roadmap Agent"

    def generate_roadmap(self, gaps: List[str], target_role: str, hours_per_day: float = 2.0) -> dict:
        """
        Creates a structured dictionary and markdown 30-day roadmap tailored to the target role and skill gaps.
        """
        if not gaps:
            gaps = ["General software development best practices"]

        # Call roadmap tools to get basic plan
        plan_data = create_30_day_plan(gaps, target_role, hours_per_day)
        
        # Build weekly deliverables list
        deliverables = {
            1: "Completed local environment configuration, basic scripts, and syntax check.",
            2: "Refactored framework-based functional files and components.",
            3: "Integrated working API endpoints, data models, or service connectors.",
            4: "Written unit tests (pytest), Dockerized application, and published project documentation."
        }

        # Format markdown representation
        md_lines = [
            f"# 📅 30-Day Preparation Roadmap: {target_role}",
            f"**Daily Study Goal:** {hours_per_day} hours/day",
            f"**Total Preparation Commitment:** {plan_data['total_days'] * hours_per_day} hours total across {plan_data['total_days']} days",
            "",
            "This structured preparation plan is designed to address key skill gaps and bring you to internship readiness.",
            ""
        ]

        for w in plan_data["schedule"]:
            week_num = w["week"]
            focus = w["focus"]
            skills = w["skills"]
            days = w["days"]
            
            md_lines.append(f"## 🛠️ Week {week_num}: {focus}")
            md_lines.append(f"- **Weekly Goal:** Focus on mastering: {', '.join(skills)}")
            md_lines.append(f"- **Expected Deliverable:** {deliverables.get(week_num, 'Module completion check.')}")
            md_lines.append("- **Daily Schedule & Tasks:**")
            
            for day_info in days:
                md_lines.append(f"  - [ ] **Day {day_info['day']}:** {day_info['task']} (Estimate: {hours_per_day} hours)")
            md_lines.append("")

        markdown_roadmap = "\n".join(md_lines)

        # Enhance with LLM if API key is active
        if is_llm_available():
            prompt = (
                f"Generate a customized, professional 30-day learning roadmap for {target_role}.\n"
                f"Identify study goals, daily tasks, and weekly deliverables to bridge these gaps: {gaps}.\n"
                f"Daily study budget: {hours_per_day} hours.\n"
                f"Provide clean, markdown structure. Avoid any emojis in headers."
            )
            markdown_roadmap = polish_text(
                prompt=prompt,
                fallback_text=markdown_roadmap,
                system_instruction="You are a professional software development coach. Draft structural, day-by-day learning schedules."
            )

        return {
            "target_role": target_role,
            "hours_per_day": hours_per_day,
            "total_days": plan_data["total_days"],
            "schedule": plan_data["schedule"],
            "deliverables": deliverables,
            "markdown": markdown_roadmap
        }
