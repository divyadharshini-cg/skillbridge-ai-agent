import os
from typing import Dict, Any, List
from llm_client import LLMClient

# Import all agents
from agents.profile_analyzer_agent import ProfileAnalyzerAgent
from agents.skill_gap_agent import SkillGapAgent
from agents.internship_match_agent import InternshipMatchAgent
from agents.roadmap_agent import RoadmapAgent
from agents.portfolio_project_agent import PortfolioProjectAgent
from agents.readme_agent import ReadmeAgent
from agents.interview_agent import InterviewAgent
from agents.safety_agent import SafetyAgent
from agents.evaluation_agent import EvaluationAgent

# Import scoring and database tools
from tools.scoring_tools import ScoringTools, calculate_category_scores
from tools.role_database import get_role_requirements

class CoordinatorAgent:
    """
    Coordinator Agent manages the execution lifecycle of all specialized coaching agents.
    It orchestrates safety filtering, profile parsing, capability assessment, roadmap
    generation, portfolio scoping, and interview preparation setup.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Coordinator Agent"

    def execute_pipeline(self, student_input: Any) -> dict:
        """
        Coordinates the execution of safety checks, profile analysis, gap analysis,
        roadmap generation, portfolio project design, and interview question setup.
        Returns a single unified structured report.
        """
        print(f"[{self.name}] Initiating coaching lifecycle...")
        agent_trace = []

        # 1. RUN SAFETY CHECK
        safety_agent = SafetyAgent(self.llm)
        profile_text = ""
        if isinstance(student_input, dict):
            profile_text = student_input.get("resume_text") or student_input.get("profile_text") or ""
            if not profile_text:
                # Construct composite text if missing
                skills_str = ", ".join(student_input.get("current_skills", [])) if isinstance(student_input.get("current_skills"), list) else student_input.get("current_skills", "")
                profile_text = (
                    f"Name: {student_input.get('name', 'Student')}\n"
                    f"Education: {student_input.get('education', 'College')}\n"
                    f"Skills: {skills_str}\n"
                    f"Target Role: {student_input.get('target_role', '')}"
                )
        else:
            profile_text = str(student_input)

        safety_review = safety_agent.audit_profile(profile_text)
        agent_trace.append({
            "agent": "SafetyAgent",
            "action": "Audited input text for credentials leakage, profanity, and fake claims. Masked PII and output safety flags."
        })

        # Use safe profile text from now on
        safe_profile_text = safety_review["safe_profile_text"]

        # 2. EXTRACT PROFILE SUMMARY
        analyzer_agent = ProfileAnalyzerAgent(self.llm)
        if isinstance(student_input, dict):
            # Pass dictionary down but with safe profile text
            dict_input = student_input.copy()
            dict_input["profile_text"] = safe_profile_text
            profile_summary = analyzer_agent.analyze(dict_input)
        else:
            profile_summary = analyzer_agent.analyze(safe_profile_text)
            
        agent_trace.append({
            "agent": "ProfileAnalyzerAgent",
            "action": "Parsed safe profile text and extracted student metadata: name, education, branch, skills, and target role."
        })

        # 3. RUN SKILL GAP ANALYSIS
        gap_agent = SkillGapAgent(self.llm)
        target_role = profile_summary["target_role"]
        current_skills = profile_summary["current_skills"]
        skill_gap_analysis = gap_agent.analyze_gaps(current_skills, target_role)
        
        agent_trace.append({
            "agent": "SkillGapAgent",
            "action": "Compared candidate skills against required database competencies to produce ranked gaps and descriptions."
        })

        # 4. SUGGEST INTERNSHIP MATCHES
        match_agent = InternshipMatchAgent(self.llm)
        internship_matches = match_agent.suggest_matches(current_skills)
        
        agent_trace.append({
            "agent": "InternshipMatchAgent",
            "action": "Evaluated and ranked candidate skills against all database roles, compiling fit levels and suitability explanations."
        })

        # 5. GENERATE PERSONALIZED ROADMAP
        roadmap_agent = RoadmapAgent(self.llm)
        learning_time = profile_summary["learning_time"]
        roadmap_30_days = roadmap_agent.generate_roadmap(
            gaps=skill_gap_analysis["missing_skills"],
            target_role=target_role,
            hours_per_day=learning_time
        )
        
        agent_trace.append({
            "agent": "RoadmapAgent",
            "action": "Constructed a personalized 30-day day-by-day learning plan detailing weekly targets and study hours."
        })

        # 6. RECOMMEND PORTFOLIO PROJECT
        project_agent = PortfolioProjectAgent(self.llm)
        portfolio_project = project_agent.recommend_project(
            gaps=skill_gap_analysis["missing_skills"],
            target_role=target_role
        )
        
        agent_trace.append({
            "agent": "PortfolioProjectAgent",
            "action": "Selected and configured a high-impact portfolio project designed to showcase missing capabilities."
        })

        # 7. GENERATE GITHUB README
        readme_agent = ReadmeAgent(self.llm)
        generated_readme = readme_agent.generate_readme(portfolio_project)
        
        agent_trace.append({
            "agent": "ReadmeAgent",
            "action": "Generated a complete GitHub-ready README.md layout documenting stack, setup steps, and milestones."
        })

        # 8. GENERATE INTERVIEW PREP QUESTIONS
        interview_agent = InterviewAgent(self.llm)
        interview_questions = interview_agent.generate_questions(
            target_role=target_role,
            gaps=skill_gap_analysis["missing_skills"],
            project_name=portfolio_project["project_name"]
        )
        
        agent_trace.append({
            "agent": "InterviewAgent",
            "action": "Drafted realistic categorized mock interview questions spanning Technical, Project-based, HR, and Coding areas."
        })

        # 9. COMPUTE READINESS SCORE AND CATEGORY SCORES
        role_reqs = get_role_requirements(target_role)
        required_skills = role_reqs.get("required_skills", [])
        
        match_percentage = ScoringTools.calculate_match_percentage(current_skills, required_skills)
        readiness_score = ScoringTools.compute_readiness_index(match_percentage, safety_review["honesty_score"])
        
        # Calculate categories
        category_scores = calculate_category_scores(
            current_skills=current_skills,
            role_name=target_role,
            projects=profile_summary.get("existing_projects")
        )

        # Assemble the report for evaluation
        report_draft = {
            "profile_summary": profile_summary,
            "readiness_score": readiness_score,
            "category_scores": category_scores,
            "skill_gap_analysis": skill_gap_analysis,
            "internship_matches": internship_matches,
            "roadmap_30_days": roadmap_30_days,
            "portfolio_project": portfolio_project,
            "generated_readme": generated_readme,
            "interview_questions": interview_questions,
            "safety_review": safety_review
        }

        # 10. EVALUATE FINAL REPORT QUALITY
        evaluation_agent = EvaluationAgent(self.llm)
        evaluation_summary = evaluation_agent.evaluate_report(report_draft)
        
        # Override agent_trace with a clean list of safe summaries only
        agent_trace_summaries = [
            "Safety Agent checked honesty and privacy",
            "Profile Analyzer Agent extracted student skills",
            "Skill Gap Agent compared target role requirements",
            "Internship Match Agent suggested suitable roles",
            "Roadmap Agent created a 30-day plan",
            "Portfolio Project Agent recommended project features",
            "Readme Agent generated GitHub README",
            "Interview Agent drafted mock questions",
            "Evaluation Agent checked final report quality"
        ]

        # Final assembly of structured coordinated report
        final_report = report_draft.copy()
        final_report["evaluation_summary"] = evaluation_summary
        final_report["agent_trace"] = agent_trace_summaries
        final_report["execution_trace"] = agent_trace_summaries

        return final_report
