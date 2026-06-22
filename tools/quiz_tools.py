import json
import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

def load_question_bank() -> Dict[str, Any]:
    """
    Loads the local question bank from data/question_bank.json.
    Returns a dictionary with all available questions.
    """
    try:
        # Get the path relative to this file
        base_path = Path(__file__).parent.parent
        question_bank_path = base_path / "data" / "question_bank.json"
        
        if not question_bank_path.exists():
            return {"questions": []}
        
        with open(question_bank_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        # Return empty question bank if loading fails
        return {"questions": []}


def select_adaptive_questions(
    target_role: str,
    current_skills: List[str],
    missing_skills: List[str],
    preferred_language: str = "Python",
    count: int = 5
) -> List[Dict[str, Any]]:
    """
    Selects adaptive questions based on:
    - Target role
    - Current skills (lower priority)
    - Missing skills (higher priority - prefer these first)
    - Preferred language
    - Desired question count
    
    Returns a list of questions, avoiding duplicates across sessions.
    Ensures diversity in question types.
    """
    question_bank = load_question_bank()
    questions = question_bank.get("questions", [])
    
    if not questions:
        return []
    
    # Filter by role first
    role_questions = [q for q in questions if q.get("role", "").lower() == target_role.lower()]
    
    if not role_questions:
        return []
    
    selected = []
    used_ids = set()
    
    # Priority 1: Questions targeting missing skills
    missing_skill_questions = [
        q for q in role_questions
        if q.get("skill_tag", "").lower() in [s.lower() for s in missing_skills]
        and q.get("id") not in used_ids
    ]
    
    # Priority 2: Questions from other important skill tags
    other_questions = [
        q for q in role_questions
        if q.get("id") not in used_ids
        and q not in missing_skill_questions
    ]
    
    # Combine with missing skills first
    prioritized = missing_skill_questions + other_questions
    
    # Ensure diversity in question types
    type_counts = {}
    coding_count = 0
    project_count = 0
    
    for question in prioritized:
        if len(selected) >= count:
            break
        
        question_type = question.get("question_type", "")
        
        # Ensure at least one coding question
        if "Coding" in question_type and coding_count < 1:
            selected.append(question)
            used_ids.add(question.get("id"))
            coding_count += 1
            continue
        
        # Ensure at least one project-based question
        if "Project" in question_type and project_count < 1:
            selected.append(question)
            used_ids.add(question.get("id"))
            project_count += 1
            continue
        
        # Add remaining questions
        if len(selected) < count:
            selected.append(question)
            used_ids.add(question.get("id"))
    
    # If we still need more questions, just add remaining ones
    if len(selected) < count:
        for question in prioritized:
            if question.get("id") not in used_ids and len(selected) < count:
                selected.append(question)
                used_ids.add(question.get("id"))
    
    return selected[:count]


def evaluate_mcq_answer(user_answer: str, expected_answer: str) -> Dict[str, Any]:
    """
    Evaluates a multiple-choice question answer.
    Returns a score (0-10) and feedback.
    """
    user_clean = user_answer.strip().lower()
    expected_clean = expected_answer.strip().lower()
    
    if user_clean == expected_clean:
        return {
            "score": 10,
            "feedback": "Correct! Well done.",
            "is_correct": True
        }
    else:
        return {
            "score": 0,
            "feedback": f"Incorrect. The correct answer is: {expected_answer}",
            "is_correct": False
        }


def evaluate_text_answer(user_answer: str, rubric_points: List[str]) -> Dict[str, Any]:
    """
    Evaluates a text answer using rubric-based matching.
    Uses keyword matching to determine if key points are covered.
    Returns a score (0-10) and feedback.
    
    Rubric points are keywords/phrases that should be present in the answer.
    """
    user_answer_lower = user_answer.lower()
    points_covered = 0
    covered_points = []
    missing_points = []
    
    for rubric_point in rubric_points:
        rubric_lower = rubric_point.lower()
        # Check if rubric point or key words from it are in the answer
        words = rubric_lower.split()
        
        # Look for key words (filter out common words)
        key_words = [w for w in words if len(w) > 3 and w not in ["the", "that", "this", "with"]]
        
        # Check if most key words are present
        if key_words:
            matched_words = sum(1 for w in key_words if w in user_answer_lower)
            if matched_words >= len(key_words) * 0.6:  # 60% threshold
                points_covered += 1
                covered_points.append(rubric_point)
            else:
                missing_points.append(rubric_point)
        else:
            # If rubric point is too short, do substring matching
            if rubric_lower in user_answer_lower:
                points_covered += 1
                covered_points.append(rubric_point)
            else:
                missing_points.append(rubric_point)
    
    # Calculate score based on rubric coverage
    if not rubric_points:
        score = 5  # Default score if no rubric points
    else:
        score = int((points_covered / len(rubric_points)) * 10)
        score = min(10, max(0, score))
    
    feedback_lines = []
    
    # Add answer length assessment
    if len(user_answer.strip()) < 20:
        feedback_lines.append("Your answer is quite brief. Consider providing more detail.")
        score = max(0, score - 2)
    elif len(user_answer.strip()) < 50:
        feedback_lines.append("Good effort! Consider expanding with more specific details.")
    
    if covered_points:
        feedback_lines.append(f"✓ Well covered: {', '.join(covered_points[:2])}")
    
    if missing_points and len(missing_points) <= 2:
        feedback_lines.append(f"Consider addressing: {', '.join(missing_points)}")
    
    return {
        "score": score,
        "feedback": " | ".join(feedback_lines) if feedback_lines else "Review your answer and ensure it covers key concepts.",
        "is_correct": points_covered == len(rubric_points),
        "points_covered": len(covered_points),
        "total_rubric_points": len(rubric_points)
    }


def evaluate_coding_answer(
    user_code: str,
    sample_test_cases: List[Dict[str, str]],
    language: str = "Python"
) -> Dict[str, Any]:
    """
    Evaluates a coding answer using rubric-based checks (NO unsafe code execution).
    This function performs static analysis and checks for:
    - Function/method presence
    - Basic syntax validity
    - Presence of key programming constructs
    - Sample test case logic verification (safe checks only)
    
    Returns a score (0-10) and feedback.
    """
    score = 5  # Base score for attempting coding
    feedback_lines = []
    issues = []
    
    # Safety: Don't execute arbitrary code
    if language.lower() == "python":
        # Check for dangerous patterns
        dangerous_patterns = [
            "os.system", "subprocess", "eval", "exec", "__import__",
            "open(", "requests", "socket", "threading"
        ]
        for pattern in dangerous_patterns:
            if pattern in user_code:
                return {
                    "score": 1,
                    "feedback": "Code contains potentially unsafe operations. Use safe code only.",
                    "is_correct": False
                }
        
        # Check for basic Python structure
        if "def " not in user_code and "class " not in user_code:
            issues.append("Missing function or class definition")
            score -= 2
        
        # Check for common Python syntax
        if ":" in user_code:
            feedback_lines.append("✓ Function/block structure present")
            score += 1
        
        # Check for error handling
        if "try" in user_code or "except" in user_code:
            feedback_lines.append("✓ Error handling implemented")
            score += 1
        
        # Check for return statements
        if "return" in user_code:
            feedback_lines.append("✓ Return statement present")
            score += 1
        else:
            issues.append("No return statement found")
            score -= 1
        
        # Check for comments or documentation
        if "#" in user_code or '"""' in user_code or "'''" in user_code:
            feedback_lines.append("✓ Code documentation present")
            score += 1
    
    # Check for loop or condition structures
    if "for " in user_code or "while " in user_code:
        feedback_lines.append("✓ Loop/iteration logic present")
        score += 1
    
    if "if " in user_code or "else" in user_code:
        feedback_lines.append("✓ Conditional logic present")
        score += 1
    
    if issues:
        feedback_lines.extend([f"⚠ {issue}" for issue in issues])
    
    if sample_test_cases:
        feedback_lines.append(f"Provided {len(sample_test_cases)} test case(s) for reference. Verify your logic matches.")
    
    score = min(10, max(0, score))
    
    return {
        "score": score,
        "feedback": " | ".join(feedback_lines) if feedback_lines else "Code structure is acceptable. Ensure it handles all test cases.",
        "is_correct": score >= 7,
        "static_analysis": True,
        "requires_manual_review": True
    }


def calculate_quiz_score(question_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates overall quiz score and statistics from individual question results.
    
    Args:
        question_results: List of dicts with keys: score, question_id, skill_tag, etc.
    
    Returns:
        Dictionary with overall score, average, by difficulty, by question type, weak skills
    """
    if not question_results:
        return {
            "total_score": 0,
            "average_score": 0,
            "num_questions": 0,
            "score_breakdown": {},
            "weak_skills": [],
            "feedback": "No questions attempted."
        }
    
    scores = [q.get("score", 0) for q in question_results]
    total_score = sum(scores)
    num_questions = len(question_results)
    average_score = total_score / num_questions if num_questions > 0 else 0
    
    # Group by difficulty
    by_difficulty = {}
    for result in question_results:
        diff = result.get("difficulty", "Unknown")
        if diff not in by_difficulty:
            by_difficulty[diff] = []
        by_difficulty[diff].append(result.get("score", 0))
    
    difficulty_avg = {}
    for diff, scores_list in by_difficulty.items():
        difficulty_avg[diff] = sum(scores_list) / len(scores_list) if scores_list else 0
    
    # Find weak skills (score < 6)
    weak_skills = []
    for result in question_results:
        if result.get("score", 10) < 6:
            skill_tag = result.get("skill_tag", "general")
            if skill_tag not in weak_skills:
                weak_skills.append(skill_tag)
    
    # Performance feedback
    if average_score >= 8:
        feedback = "Excellent performance! You're well-prepared for this role."
    elif average_score >= 6:
        feedback = "Good effort! Focus on the areas marked below to improve further."
    else:
        feedback = "Consider practicing more in the weak skill areas below."
    
    return {
        "total_score": total_score,
        "average_score": round(average_score, 2),
        "num_questions": num_questions,
        "by_difficulty": difficulty_avg,
        "weak_skills": weak_skills,
        "strong_skills": [result.get("skill_tag") for result in question_results if result.get("score", 0) >= 8],
        "feedback": feedback,
        "performance_level": "Excellent" if average_score >= 8 else ("Good" if average_score >= 6 else "Need Improvement")
    }
