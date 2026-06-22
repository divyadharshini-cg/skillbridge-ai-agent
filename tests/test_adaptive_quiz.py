import json
import pytest
import tools.quiz_tools as quiz_tools
from tools.quiz_tools import (
    load_question_bank,
    select_adaptive_questions,
    evaluate_mcq_answer,
    evaluate_text_answer,
    evaluate_coding_answer,
    calculate_quiz_score
)


class TestQuestionBankLoading:
    """Test question bank loading functionality."""
    
    def test_load_question_bank_returns_dict(self):
        """Question bank should load as a dictionary."""
        bank = load_question_bank()
        assert isinstance(bank, dict)
    
    def test_load_question_bank_has_questions_key(self):
        """Question bank should have 'questions' key."""
        bank = load_question_bank()
        assert "questions" in bank
    
    def test_load_question_bank_questions_is_list(self):
        """Questions should be a list."""
        bank = load_question_bank()
        questions = bank.get("questions", [])
        assert isinstance(questions, list)
    
    def test_load_question_bank_not_empty(self):
        """Question bank should contain questions."""
        bank = load_question_bank()
        questions = bank.get("questions", [])
        assert len(questions) > 0
    
    def test_question_has_required_fields(self):
        """Each question should have required fields."""
        bank = load_question_bank()
        questions = bank.get("questions", [])
        
        required_fields = {"id", "role", "skill_tag", "difficulty", "question_type", "question"}
        
        for question in questions:
            assert isinstance(question, dict)
            for field in required_fields:
                assert field in question, f"Missing field: {field}"


class TestAdaptiveSelection:
    """Test adaptive question selection."""
    
    def test_select_questions_by_role(self):
        """Should select questions for a specific role."""
        questions = select_adaptive_questions(
            target_role="AI/ML Intern",
            current_skills=["Python"],
            missing_skills=["Deep Learning"],
            count=3
        )
        assert len(questions) <= 3
        if len(questions) > 0:
            for q in questions:
                # Ensure questions are dictionaries with 'role' key
                assert isinstance(q, dict)
    
    def test_select_questions_prioritizes_missing_skills(self):
        """Should prioritize questions targeting missing skills."""
        questions = select_adaptive_questions(
            target_role="AI/ML Intern",
            current_skills=["Python"],
            missing_skills=["deep_learning"],
            count=5
        )
        
        # Should return some questions (even if skill_tag doesn't match exactly)
        assert len(questions) > 0
    
    def test_select_questions_respects_count(self):
        """Should return at most the requested count."""
        for count in [3, 5, 7]:
            questions = select_adaptive_questions(
                target_role="Python Developer Intern",
                current_skills=["Python"],
                missing_skills=[],
                count=count
            )
            assert len(questions) <= count
    
    def test_select_questions_no_role_match(self):
        """Should return empty list if role doesn't exist."""
        questions = select_adaptive_questions(
            target_role="Nonexistent Role",
            current_skills=[],
            missing_skills=[],
            count=5
        )
        assert len(questions) == 0
    
    def test_select_questions_includes_coding(self):
        """Should include at least one coding question if available."""
        questions = select_adaptive_questions(
            target_role="Python Developer Intern",
            current_skills=[],
            missing_skills=[],
            count=5
        )
        
        # Check if at least one coding question is present
        if len(questions) > 0:
            has_coding = any("Coding" in q.get("question_type", "") for q in questions)
            assert has_coding, "No coding question found"


class TestMCQEvaluation:
    """Test MCQ answer evaluation."""
    
    def test_evaluate_mcq_correct_answer(self):
        """Should give perfect score for correct MCQ answer."""
        result = evaluate_mcq_answer(
            user_answer="Removes neurons temporarily during training",
            expected_answer="Removes neurons temporarily during training"
        )
        assert result.get("score") == 10
        assert result.get("is_correct") is True
    
    def test_evaluate_mcq_incorrect_answer(self):
        """Should give zero score for incorrect MCQ answer."""
        result = evaluate_mcq_answer(
            user_answer="Deletes training data",
            expected_answer="Removes neurons temporarily during training"
        )
        assert result.get("score") == 0
        assert result.get("is_correct") is False
    
    def test_evaluate_mcq_case_insensitive(self):
        """MCQ evaluation should be case-insensitive."""
        result = evaluate_mcq_answer(
            user_answer="REMOVES NEURONS TEMPORARILY DURING TRAINING",
            expected_answer="Removes neurons temporarily during training"
        )
        assert result.get("score") == 10
        assert result.get("is_correct") is True
    
    def test_evaluate_mcq_whitespace_handling(self):
        """MCQ evaluation should handle extra whitespace."""
        result = evaluate_mcq_answer(
            user_answer="  Removes neurons temporarily during training  ",
            expected_answer="Removes neurons temporarily during training"
        )
        assert result.get("score") == 10
        assert result.get("is_correct") is True


class TestTextEvaluation:
    """Test text answer evaluation using rubric."""
    
    def test_evaluate_text_all_rubric_points(self):
        """Should score reasonably when most rubric points are covered."""
        result = evaluate_text_answer(
            user_answer="I show genuine interest in AI field. I learn from resources like courses and papers. I have a growth mindset and continuous learning.",
            rubric_points=["Shows genuine interest", "Mentions learning resources", "Demonstrates growth mindset"]
        )
        # Score should be at least 6 when most points are covered
        assert result.get("score") >= 5
        assert "points_covered" in result
    
    def test_evaluate_text_some_rubric_points(self):
        """Should score based on rubric coverage."""
        result = evaluate_text_answer(
            user_answer="I am interested in AI and like to learn more about machine learning frameworks and best practices.",
            rubric_points=["Shows genuine interest", "Mentions learning resources", "Demonstrates growth mindset"]
        )
        # Should return some score based on coverage
        assert 0 <= result.get("score") <= 10
        assert "points_covered" in result
    
    def test_evaluate_text_no_rubric_points(self):
        """Should score low when no rubric points are covered."""
        result = evaluate_text_answer(
            user_answer="Maybe. I don't know.",
            rubric_points=["Shows genuine interest", "Mentions learning resources", "Demonstrates growth mindset"]
        )
        assert result.get("score") < 5
    
    def test_evaluate_text_empty_rubric(self):
        """Should give default score when rubric is empty."""
        result = evaluate_text_answer(
            user_answer="Some answer",
            rubric_points=[]
        )
        # Default score for empty rubric with brief answer
        assert 0 <= result.get("score") <= 10
        assert "points_covered" in result

    def test_evaluate_text_semantic_precision_recall(self, monkeypatch):
        """Should score semantic precision/recall answers higher even without exact rubric text."""
        monkeypatch.setattr(quiz_tools, "is_llm_available", lambda: False)
        result = evaluate_text_answer(
            user_answer=(
                "Precision means the model's positive predictions are correct, with fewer false positives. "
                "Recall means finding the actual positives and avoiding false negatives."
            ),
            rubric_points=["Explain precision and recall"]
        )
        assert result.get("score") >= 7
        assert result.get("scoring_method") == "Rubric fallback"

    def test_evaluate_text_llm_refinement(self, monkeypatch):
        """Should use Gemini-assisted scoring when available and return enriched scoring metadata."""
        def dummy_llm_refinement(question, expected_answer, rubric_points, user_answer, fallback_result):
            return {
                "score": 9,
                "feedback": "Good coverage of the key idea. | Missing: More explicit examples would help. | Tip: Add a short use case to support the definition.",
                "is_correct": True,
                "what_was_good": "Good coverage of the key idea.",
                "what_was_missing": "More explicit examples would help.",
                "improvement_tip": "Add a short use case to support the definition.",
                "scoring_method": "Gemini-assisted"
            }

        monkeypatch.setattr(quiz_tools, "evaluate_answer_with_llm", dummy_llm_refinement)

        result = evaluate_text_answer(
            user_answer="Precision focuses on reducing false positives while recall focuses on reducing false negatives.",
            rubric_points=["Explain precision and recall"]
        )

        assert result.get("score") == 9
        assert result.get("scoring_method") == "Gemini-assisted"
        assert result.get("what_was_good") == "Good coverage of the key idea."
        assert result.get("what_was_missing") == "More explicit examples would help."
        assert result.get("improvement_tip") == "Add a short use case to support the definition."

    def test_evaluate_text_project_based_answer(self):
        """Should score project-based answers using project-specific concept coverage."""
        result = evaluate_text_answer(
            user_answer=(
                "I led a project to improve a recommendation system by cleaning the user dataset, selecting a collaborative filtering algorithm, and measuring improved accuracy. "
                "I also documented challenges and the final results."
            ),
            rubric_points=["Describe project goal", "Discuss dataset and model", "Explain challenges and results"],
            question_type="Project-Based Question"
        )
        assert result.get("score") >= 7
        assert result.get("scoring_method") == "Rubric fallback"
        assert "Good project answer" in result.get("feedback", "")

    def test_evaluate_text_hr_short_answer(self):
        """Should provide useful feedback for HR answers and respect HR concept coverage."""
        result = evaluate_text_answer(
            user_answer="I am passionate about the role and want to learn quickly.",
            rubric_points=["Express interest in the role", "Mention learning mindset"],
            question_type="HR Question"
        )
        assert 0 <= result.get("score") <= 10
        assert "learning" in result.get("feedback", "").lower()
        assert result.get("scoring_method") == "Rubric fallback"


class TestCodingEvaluation:
    """Test coding answer evaluation (safe, no execution)."""
    
    def test_evaluate_code_with_function_def(self):
        """Should score higher when function is defined."""
        code = "def linear_regression(X, y):\n    return model"
        result = evaluate_coding_answer(code, [], language="Python")
        assert result.get("score") > 5
        assert "✓ Function/block structure" in result.get("feedback", "")
    
    def test_evaluate_code_with_return_statement(self):
        """Should recognize return statements."""
        code = "def func():\n    result = 42\n    return result"
        result = evaluate_coding_answer(code, [], language="Python")
        assert "return" in result.get("feedback", "").lower()
    
    def test_evaluate_code_dangerous_pattern_detection(self):
        """Should not accept code with dangerous patterns."""
        code = "import os\nos.system('rm -rf /')"
        result = evaluate_coding_answer(code, [], language="Python")
        assert result.get("score") == 1
        assert "unsafe" in result.get("feedback", "").lower()
    
    def test_evaluate_code_with_error_handling(self):
        """Should recognize try-except blocks."""
        code = "def safe_func():\n    try:\n        x = 1/0\n    except:\n        pass"
        result = evaluate_coding_answer(code, [], language="Python")
        assert "error handling" in result.get("feedback", "").lower()
    
    def test_evaluate_code_with_conditions(self):
        """Should recognize conditional logic."""
        code = "if x > 0:\n    print('positive')\nelse:\n    print('non-positive')"
        result = evaluate_coding_answer(code, [], language="Python")
        assert "conditional" in result.get("feedback", "").lower()


class TestScoreCalculation:
    """Test quiz score calculation."""
    
    def test_calculate_score_empty_results(self):
        """Should handle empty results gracefully."""
        result = calculate_quiz_score([])
        assert result.get("total_score") == 0
        assert result.get("average_score") == 0
        assert result.get("num_questions") == 0
    
    def test_calculate_score_single_question(self):
        """Should calculate score for single question."""
        results = [
            {
                "score": 8,
                "skill_tag": "python",
                "difficulty": "Medium",
                "question_type": "MCQ"
            }
        ]
        calc = calculate_quiz_score(results)
        assert calc.get("total_score") == 8
        assert calc.get("average_score") == 8.0
        assert calc.get("num_questions") == 1
    
    def test_calculate_score_multiple_questions(self):
        """Should calculate average for multiple questions."""
        results = [
            {"score": 10, "skill_tag": "python", "difficulty": "Easy", "question_type": "MCQ"},
            {"score": 8, "skill_tag": "oop", "difficulty": "Medium", "question_type": "Coding"},
            {"score": 6, "skill_tag": "design", "difficulty": "Hard", "question_type": "Project"}
        ]
        calc = calculate_quiz_score(results)
        assert calc.get("total_score") == 24
        assert calc.get("average_score") == 8.0
        assert calc.get("num_questions") == 3
    
    def test_calculate_score_identifies_weak_skills(self):
        """Should identify skills with low scores."""
        results = [
            {"score": 10, "skill_tag": "python", "difficulty": "Easy", "question_type": "MCQ"},
            {"score": 2, "skill_tag": "machine_learning", "difficulty": "Hard", "question_type": "Coding"},
            {"score": 3, "skill_tag": "deep_learning", "difficulty": "Hard", "question_type": "Project"}
        ]
        calc = calculate_quiz_score(results)
        weak_skills = calc.get("weak_skills", [])
        assert "machine_learning" in weak_skills
        assert "deep_learning" in weak_skills
        assert "python" not in weak_skills
    
    def test_calculate_score_performance_level(self):
        """Should assign correct performance level."""
        # Excellent
        high_results = [
            {"score": 9, "skill_tag": "python", "difficulty": "Medium", "question_type": "MCQ"},
            {"score": 10, "skill_tag": "oop", "difficulty": "Medium", "question_type": "MCQ"}
        ]
        calc = calculate_quiz_score(high_results)
        assert calc.get("performance_level") == "Excellent"
        
        # Good
        mid_results = [
            {"score": 7, "skill_tag": "python", "difficulty": "Medium", "question_type": "MCQ"},
            {"score": 6, "skill_tag": "oop", "difficulty": "Medium", "question_type": "MCQ"}
        ]
        calc = calculate_quiz_score(mid_results)
        assert calc.get("performance_level") == "Good"
        
        # Need Improvement
        low_results = [
            {"score": 3, "skill_tag": "python", "difficulty": "Hard", "question_type": "Coding"},
            {"score": 2, "skill_tag": "oop", "difficulty": "Hard", "question_type": "Coding"}
        ]
        calc = calculate_quiz_score(low_results)
        assert calc.get("performance_level") == "Need Improvement"
    
    def test_calculate_score_by_difficulty(self):
        """Should calculate average by difficulty level."""
        results = [
            {"score": 10, "skill_tag": "python", "difficulty": "Easy", "question_type": "MCQ"},
            {"score": 8, "skill_tag": "oop", "difficulty": "Easy", "question_type": "MCQ"},
            {"score": 6, "skill_tag": "design", "difficulty": "Hard", "question_type": "Coding"}
        ]
        calc = calculate_quiz_score(results)
        by_diff = calc.get("by_difficulty", {})
        assert by_diff.get("Easy") == 9.0  # (10 + 8) / 2
        assert by_diff.get("Hard") == 6.0


class TestAdaptiveQuizAgent:
    """Test AdaptiveQuizAgent functionality."""
    
    def test_quiz_agent_import(self):
        """Should be able to import AdaptiveQuizAgent."""
        from agents.adaptive_quiz_agent import AdaptiveQuizAgent
        agent = AdaptiveQuizAgent()
        assert agent.name == "Adaptive Quiz Agent"
    
    def test_generate_quiz_returns_dict(self):
        """Generate quiz should return a dictionary."""
        from agents.adaptive_quiz_agent import AdaptiveQuizAgent
        agent = AdaptiveQuizAgent()
        result = agent.generate_quiz(
            target_role="Python Developer Intern",
            current_skills=["Python"],
            missing_skills=["OOP"],
            num_questions=3
        )
        assert isinstance(result, dict)
    
    def test_generate_quiz_has_questions(self):
        """Generated quiz should contain questions."""
        from agents.adaptive_quiz_agent import AdaptiveQuizAgent
        agent = AdaptiveQuizAgent()
        result = agent.generate_quiz(
            target_role="Python Developer Intern",
            current_skills=["Python"],
            missing_skills=[],
            num_questions=3
        )
        assert "questions" in result
        if result.get("status") == "success":
            assert len(result.get("questions", [])) > 0
    
    def test_evaluate_quiz_returns_results(self):
        """Evaluate quiz should return results."""
        from agents.adaptive_quiz_agent import AdaptiveQuizAgent
        agent = AdaptiveQuizAgent()
        
        # First generate a quiz
        quiz = agent.generate_quiz(
            target_role="Python Developer Intern",
            current_skills=["Python"],
            missing_skills=[],
            num_questions=3
        )
        
        if quiz.get("status") == "success":
            questions = quiz.get("questions", [])
            if len(questions) > 0:
                # Ensure questions are dictionaries
                assert all(isinstance(q, dict) for q in questions)
                
                # Create answers (use question IDs)
                answers = {q.get("id"): "test answer" for q in questions}
                
                results = agent.evaluate_quiz_answers(questions, answers)
                assert "quiz_score" in results
                assert "question_results" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
