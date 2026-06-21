import pytest
from tools.scoring_tools import ScoringTools

def test_calculate_match_percentage():
    student_skills = ["Python", "Git", "HTML/CSS"]
    required_skills = ["Python", "Git", "FastAPI", "Docker", "pytest", "SQL"]
    
    # 2 matching skills (Python, Git) out of 6 required
    expected_score = (2 / 6) * 100.0
    actual_score = ScoringTools.calculate_match_percentage(student_skills, required_skills)
    
    assert actual_score == pytest.approx(expected_score, 0.01)

def test_calculate_match_percentage_empty():
    assert ScoringTools.calculate_match_percentage([], []) == 100.0
    assert ScoringTools.calculate_match_percentage(["Python"], []) == 100.0

def test_compute_readiness_index():
    match_percentage = 50.0
    honesty_score = 90
    
    # (50.0 * 0.7) + (90 * 0.3) = 35 + 27 = 62
    expected_readiness = 62
    actual_readiness = ScoringTools.compute_readiness_index(match_percentage, honesty_score)
    
    assert actual_readiness == expected_readiness
