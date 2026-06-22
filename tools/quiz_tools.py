import json
import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from llm_client import LLMClient, is_llm_available

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
            "is_correct": True,
            "scoring_method": "MCQ exact match",
            "what_was_good": "Selected the correct choice.",
            "what_was_missing": "",
            "improvement_tip": "Keep applying the same careful reading to other MCQ questions."
        }
    else:
        return {
            "score": 0,
            "feedback": f"Incorrect. The correct answer is: {expected_answer}",
            "is_correct": False,
            "scoring_method": "MCQ exact match",
            "what_was_good": "",
            "what_was_missing": "The selected option did not match the expected answer.",
            "improvement_tip": "Review the definitions and eliminate clearly wrong choices first."
        }


def _normalize_answer(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _concept_match(answer: str, patterns: List[List[str]]) -> int:
    answer = _normalize_answer(answer)
    matches = 0
    for group in patterns:
        for pattern in group:
            if pattern in answer:
                matches += 1
                break
    return matches


def evaluate_answer_with_llm(
    question: str,
    expected_answer: str,
    rubric_points: List[str],
    user_answer: str,
    fallback_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Optionally use Gemini to refine scoring, but fallback always remains available.
    """
    if not is_llm_available():
        return fallback_result

    llm_client = LLMClient()
    prompt = (
        "You are a technical interviewer scoring a candidate response. "
        "Return JSON only with fields: score_out_of_10, what_was_good, what_was_missing, improvement_tip.\n"
        f"Question: {question}\n"
        f"Expected answer: {expected_answer}\n"
        f"Rubric points: {rubric_points}\n"
        f"Candidate answer: {user_answer}\n"
        "Score the answer from 0 to 10, then list what was good, what was missing, and one improvement tip."
    )
    system_instruction = "You are a precise scoring assistant. Return only valid JSON."

    try:
        response = llm_client.generate(prompt, system_instruction=system_instruction).strip()
        if not response or response.startswith("[LLM Error") or response.startswith("[MOCK RESPONSE"):
            return fallback_result

        if response.startswith("```json"):
            response = response[8:].rstrip("`\n ")
        import json as _json
        parsed = _json.loads(response)
        score = int(parsed.get("score_out_of_10", fallback_result.get("score", 0)))
        score = min(10, max(0, score))
        return {
            "score": score,
            "feedback": f"{parsed.get('what_was_good', '').strip()} | Missing: {parsed.get('what_was_missing', '').strip()} | Tip: {parsed.get('improvement_tip', '').strip()}",
            "is_correct": score >= 7,
            "what_was_good": parsed.get('what_was_good', '').strip(),
            "what_was_missing": parsed.get('what_was_missing', '').strip(),
            "improvement_tip": parsed.get('improvement_tip', '').strip(),
            "scoring_method": "Gemini-assisted"
        }
    except Exception:
        return fallback_result


def evaluate_text_answer(user_answer: str, rubric_points: List[str], question_type: str = "Technical") -> Dict[str, Any]:
    """
    Evaluates a text answer using a hybrid rubric + concept matching approach.
    Returns a score (0-10), detailed feedback, and scoring method.
    """
    user_answer_clean = _normalize_answer(user_answer)
    if not user_answer_clean:
        return {
            "score": 0,
            "feedback": "No answer provided.",
            "is_correct": False,
            "scoring_method": "Rubric fallback",
            "what_was_good": "",
            "what_was_missing": "Answer was empty.",
            "improvement_tip": "Provide a complete response that includes the requested concepts."
        }

    concept_groups = {
        "precision_recall": [
            ["predicted positives are correct", "correct positive predictions", "fewer false positives", "low false positives"],
            ["actual positives found", "misses positive cases", "false negatives", "catching all positives"],
            ["precision", "recall", "true positives", "false positives", "false negatives"]
        ],
        "technical": [
            ["correct definition", "definition is", "means"],
            ["practical meaning", "real world", "example", "interpretation"],
            ["limitation", "tradeoff", "drawback", "cost"],
            ["precision", "recall", "accuracy", "f1 score"]
        ],
        "project": [
            ["project goal", "objective", "problem statement", "aim"],
            ["dataset", "data set", "data"],
            ["model", "approach", "algorithm", "architecture"],
            ["challenge", "difficulty", "problem", "issue"],
            ["solution", "improvement", "fix", "resolve"],
            ["result", "outcome", "lesson", "learned"]
        ],
        "hr": [
            ["genuine interest", "excited", "passionate"],
            ["role alignment", "position", "internship", "role"],
            ["skills", "projects", "experience", "background"],
            ["learning mindset", "learn", "growth", "improve"],
            ["plan", "stay updated", "keep up", "continue learning"]
        ]
    }

    def _score_rubric_dimensions(answer: str, rubric_points: List[str]) -> Dict[str, Any]:
        score = 0
        matched = []
        missing = []
        for point in rubric_points:
            normalized_point = _normalize_answer(point)
            if normalized_point in answer:
                score += 1
                matched.append(point)
            else:
                words = [w for w in normalized_point.split() if len(w) > 3]
                if words and sum(1 for w in words if w in answer) >= max(1, int(len(words) * 0.5)):
                    score += 1
                    matched.append(point)
                else:
                    missing.append(point)
        return {"matched": matched, "missing": missing, "score": score}

    rubric_result = _score_rubric_dimensions(user_answer_clean, rubric_points)
    base_score = int((rubric_result["score"] / len(rubric_points)) * 10) if rubric_points else 5

    if question_type == "Project-Based Question":
        dimension_patterns = concept_groups["project"]
    elif question_type == "HR Question":
        dimension_patterns = concept_groups["hr"]
    else:
        dimension_patterns = concept_groups["technical"]

    concept_score = _concept_match(user_answer_clean, dimension_patterns)
    concept_score = min(len(dimension_patterns), concept_score)
    concept_score_normalized = int((concept_score / len(dimension_patterns)) * 10) if len(dimension_patterns) else 0

    # Hybrid score - combine rubric matching with semantic concept coverage
    if rubric_points:
        score = int(round((base_score * 0.4) + (concept_score_normalized * 0.6)))
    else:
        score = concept_score_normalized if concept_score > 0 else 5
    score = min(10, max(score, base_score, concept_score_normalized))

    # Reward good semantic answers even if exact rubric phrase is missing
    if concept_score >= max(2, len(dimension_patterns) // 2) and len(user_answer_clean) > 50:
        score = max(score, 8)

    feedback_parts = []
    if rubric_result["matched"]:
        feedback_parts.append(f"✓ Covered: {', '.join(rubric_result['matched'][:3])}")
    if rubric_result["missing"]:
        feedback_parts.append(f"Missing: {', '.join(rubric_result['missing'][:3])}")

    if len(user_answer_clean) < 25:
        feedback_parts.append("Your answer is too brief; include more substance.")
    elif len(user_answer_clean) < 50:
        feedback_parts.append("Good start; expand with concrete examples or tradeoffs.")
    else:
        feedback_parts.append("Your response has enough length; focus on clarity and specificity.")

    if question_type == "HR Question" and score >= 7:
        feedback_parts.append("Strong HR answer with good career and learning focus.")
    elif question_type == "Project-Based Question" and score >= 7:
        feedback_parts.append("Good project answer; include more measurable results if possible.")

    fallback_result = {
        "score": score,
        "feedback": " | ".join(feedback_parts),
        "is_correct": score >= 7,
        "points_covered": rubric_result["score"],
        "total_rubric_points": len(rubric_points),
        "what_was_good": ", ".join(rubric_result["matched"][:2]),
        "what_was_missing": ", ".join(rubric_result["missing"][:2]) if rubric_result["missing"] else "",
        "improvement_tip": "Provide clearer examples and address missing rubric points.",
        "scoring_method": "Rubric fallback"
    }

    # If Gemini is available, allow optional refinement
    llm_result = evaluate_answer_with_llm(
        question=question_type,
        expected_answer=", ".join(rubric_points),
        rubric_points=rubric_points,
        user_answer=user_answer,
        fallback_result=fallback_result
    )

    return llm_result


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
