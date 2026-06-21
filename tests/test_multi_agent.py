import pytest
from agents.profile_analyzer_agent import ProfileAnalyzerAgent
from agents.skill_gap_agent import SkillGapAgent
from agents.internship_match_agent import InternshipMatchAgent
from agents.roadmap_agent import RoadmapAgent
from agents.portfolio_project_agent import PortfolioProjectAgent
from agents.readme_agent import ReadmeAgent
from agents.interview_agent import InterviewAgent
from agents.safety_agent import SafetyAgent
from agents.evaluation_agent import EvaluationAgent
from agents.coordinator_agent import CoordinatorAgent

def test_safety_agent_clean():
    agent = SafetyAgent()
    profile = "Name: Jane Doe\nTarget Role: AI/ML Intern\nSkills: Python, Git"
    res = agent.audit_profile(profile)
    assert res["passed_safety"]
    assert res["honesty_score"] == 100
    assert len(res["safety_flags"]) == 0
    assert "[REDACTED_EMAIL]" not in res["safe_profile_text"]

def test_safety_agent_unsafe():
    agent = SafetyAgent()
    profile = "Name: Jane Doe\nTarget Role: AI/ML Intern\nI want to lie on my resume and add fake experience. Also toxicword1 and test.user@example.com."
    res = agent.audit_profile(profile)
    assert not res["passed_safety"]
    assert "FAKE_CLAIMS_REQUEST" in res["safety_flags"]
    assert "PROFANITY_DETECTED" in res["safety_flags"]
    assert "[REDACTED_EMAIL]" in res["safe_profile_text"]
    assert "test.user@example.com" not in res["safe_profile_text"]

def test_profile_analyzer_dict():
    agent = ProfileAnalyzerAgent()
    student_data = {
        "name": "Jane Doe",
        "target_role": "AI/ML Intern",
        "current_skills": ["Python", "Git", "Linear Algebra"],
        "learning_time": 3.0,
        "deadline": 45
    }
    profile = agent.analyze(student_data)
    assert profile["name"] == "Jane Doe"
    assert profile["target_role"] == "AI/ML Intern"
    assert "Python" in profile["current_skills"]
    assert profile["learning_time"] == 3.0
    assert profile["deadline"] == 45

def test_profile_analyzer_text():
    agent = ProfileAnalyzerAgent()
    profile_text = (
        "Name: Alex Mercer\n"
        "Education: Bachelor of Engineering\n"
        "Branch: Information Technology\n"
        "Skills: Python, Git, SQLite\n"
        "Target Role: Python Developer Intern\n"
        "Hours per day: 1.5\n"
        "Deadline: 30"
    )
    profile = agent.analyze(profile_text)
    assert profile["name"] == "Alex Mercer"
    assert profile["education"] == "Bachelor of Engineering"
    assert profile["branch"] == "Information Technology"
    assert "Python" in profile["current_skills"]
    assert profile["target_role"] == "Python Developer Intern"
    assert profile["learning_time"] == 1.5
    assert profile["deadline"] == 30

def test_skill_gap_agent():
    agent = SkillGapAgent()
    student_skills = ["Python", "Git"]
    # AI/ML Intern required skills: ["Python", "NumPy", "Pandas", "Scikit-Learn", "Linear Algebra", "Git"]
    res = agent.analyze_gaps(student_skills, "AI/ML Intern")
    assert "python" in res["matching_skills"]
    assert "numpy" in [g["skill"].lower() for g in res["ranked_gaps"]]
    assert "linear algebra" in [g["skill"].lower() for g in res["ranked_gaps"]]
    assert len(res["missing_skills"]) > 0
    assert "Strengths" in res["explanation"]

def test_internship_match_agent():
    agent = InternshipMatchAgent()
    student_skills = ["Python", "Git", "SQL"]
    matches = agent.suggest_matches(student_skills)
    assert len(matches) > 0
    # The first item should be a dictionary with role_name and fit_level
    assert "role_name" in matches[0]
    assert "fit_level" in matches[0]
    assert "explanation" in matches[0]

def test_roadmap_agent():
    agent = RoadmapAgent()
    gaps = ["NumPy", "Pandas"]
    res = agent.generate_roadmap(gaps, "AI/ML Intern", hours_per_day=2.0)
    assert res["target_role"] == "AI/ML Intern"
    assert res["hours_per_day"] == 2.0
    assert len(res["schedule"]) == 4 # 4 weeks
    assert "# 📅 30-Day Preparation Roadmap: AI/ML Intern" in res["markdown"]

def test_portfolio_project_agent():
    agent = PortfolioProjectAgent()
    gaps = ["FastAPI", "Docker"]
    res = agent.recommend_project(gaps, "Python Developer Intern")
    assert "Asynchronous Task Queue API" in res["title"]
    assert "tech_stack" in res
    assert "folder_structure" in res
    assert "demo_plan" in res

def test_readme_agent():
    agent = ReadmeAgent()
    project_details = {
        "title": "Test Custom Project",
        "problem": "Demo problem desc.",
        "tech_stack": ["Python", "pytest"],
        "features": ["Feature A", "Feature B"],
        "demo_plan": "Run tests"
    }
    readme = agent.generate_readme(project_details)
    assert "# Test Custom Project" in readme
    assert "## 💻 Tech Stack" in readme
    assert "MIT License" in readme

def test_interview_agent():
    agent = InterviewAgent()
    gaps = ["Docker"]
    questions = agent.generate_questions("Python Developer Intern", gaps, "Asynchronous Task Queue API")
    assert len(questions) == 4
    categories = [q["category"] for q in questions]
    assert "Technical" in categories
    assert "Coding" in categories
    assert "Project-based" in categories
    assert "HR" in categories

def test_evaluation_agent():
    agent = EvaluationAgent()
    report = {
        "profile_summary": {"name": "Jane", "target_role": "AI/ML Intern", "current_skills": ["Python"]},
        "readiness_score": 50,
        "category_scores": {"Programming": 80},
        "skill_gap_analysis": {"matching_skills": [], "missing_skills": []},
        "internship_matches": [],
        "roadmap_30_days": {"markdown": ""},
        "portfolio_project": {"title": ""},
        "generated_readme": "Readme",
        "interview_questions": [],
        "safety_review": {"passed_safety": True, "honesty_score": 100}
    }
    res = agent.evaluate_report(report)
    assert "checklist" in res
    assert "overall_score" in res
    assert "feedback" in res

def test_coordinator_agent_pipeline():
    coordinator = CoordinatorAgent()
    student_input = {
        "name": "Alex Mercer",
        "target_role": "Python Developer Intern",
        "current_skills": ["Python", "Git", "SQLite"],
        "learning_time": 2.0,
        "deadline": 30
    }
    report = coordinator.execute_pipeline(student_input)
    
    # Assert correct structure
    assert "profile_summary" in report
    assert "readiness_score" in report
    assert "category_scores" in report
    assert "skill_gap_analysis" in report
    assert "internship_matches" in report
    assert "roadmap_30_days" in report
    assert "portfolio_project" in report
    assert "generated_readme" in report
    assert "interview_questions" in report
    assert "safety_review" in report
    assert "evaluation_summary" in report
    assert "agent_trace" in report
    
    # Check agent trace contents
    trace = report.get("agent_trace", [])
    assert any("Safety Agent" in t for t in trace)
    assert any("Profile Analyzer Agent" in t for t in trace)
    assert any("Evaluation Agent" in t for t in trace)

def test_llm_client_availability_fallback():
    from unittest.mock import patch
    from llm_client import is_llm_available, polish_text

    # If no valid API key is present, is_llm_available must be False
    with patch("llm_client.get_env_api_key", return_value=None):
        assert is_llm_available() is False
        assert polish_text("Polish this", "fallback") == "fallback"

    with patch("llm_client.get_env_api_key", return_value="your_gemini_api_key_here"):
        assert is_llm_available() is False
        assert polish_text("Polish this", "fallback") == "fallback"

    with patch("llm_client.get_env_api_key", return_value="   "):
        assert is_llm_available() is False
        assert polish_text("Polish this", "fallback") == "fallback"

def test_llm_client_available_success():
    from unittest.mock import patch
    from llm_client import polish_text, LLMClient

    # When available, try to generate
    with patch("llm_client.is_llm_available", return_value=True):
        with patch.object(LLMClient, "generate", return_value="Polished response"):
            assert polish_text("Polish this", "fallback") == "Polished response"

def test_llm_client_available_failure():
    from unittest.mock import patch
    from llm_client import polish_text, LLMClient

    # When available but fails (e.g. raises exception), it must return fallback
    with patch("llm_client.is_llm_available", return_value=True):
        with patch.object(LLMClient, "generate", side_effect=Exception("API Error")):
            assert polish_text("Polish this", "fallback") == "fallback"
        with patch.object(LLMClient, "generate", return_value="[LLM Error: API Error]"):
            assert polish_text("Polish this", "fallback") == "fallback"

