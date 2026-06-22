from typing import List, Dict, Any
from llm_client import LLMClient, is_llm_available
from tools.quiz_tools import (
    load_question_bank,
    select_adaptive_questions,
    evaluate_mcq_answer,
    evaluate_text_answer,
    evaluate_coding_answer,
    calculate_quiz_score
)


class AdaptiveQuizAgent:
    """
    AdaptiveQuizAgent is responsible for:
    - Selecting personalized questions based on target role and skill gaps
    - Avoiding duplicate questions across sessions
    - Prioritizing missing-skill questions
    - Ensuring question diversity (coding, project-based, etc.)
    - Evaluating answers with feedback
    - Calculating quiz scores and identifying weak areas
    """
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Adaptive Quiz Agent"
    
    def generate_quiz(
        self,
        target_role: str,
        current_skills: List[str],
        missing_skills: List[str],
        preferred_language: str = "Python",
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """
        Generates a personalized quiz with adaptive questions.
        
        Args:
            target_role: The internship role to target
            current_skills: List of skills the candidate already has
            missing_skills: List of skill gaps to prioritize
            preferred_language: Preferred programming language (Python/Java/General)
            num_questions: Number of questions to generate (3, 5, or 7)
        
        Returns:
            Dictionary with quiz metadata and questions
        """
        # Validate inputs
        num_questions = max(3, min(7, num_questions))  # Clamp between 3-7
        
        # Select adaptive questions
        questions = select_adaptive_questions(
            target_role=target_role,
            current_skills=current_skills,
            missing_skills=missing_skills,
            preferred_language=preferred_language,
            count=num_questions
        )
        
        if not questions:
            return {
                "status": "error",
                "message": f"No questions found for role: {target_role}",
                "questions": []
            }
        
        return {
            "status": "success",
            "target_role": target_role,
            "quiz_id": f"quiz_{target_role.replace(' ', '_').lower()}",
            "num_questions": len(questions),
            "language": preferred_language,
            "questions": questions,
            "instructions": self._generate_quiz_instructions(target_role, preferred_language)
        }
    
    def evaluate_quiz_answers(
        self,
        questions: List[Dict[str, Any]],
        user_answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Evaluates all user answers and provides detailed feedback.
        
        Args:
            questions: List of quiz questions
            user_answers: Dictionary mapping question_id to user's answer
        
        Returns:
            Dictionary with detailed results, scores, and feedback
        """
        question_results = []
        
        for question in questions:
            question_id = question.get("id")
            user_answer = user_answers.get(question_id, "").strip()
            
            if not user_answer:
                # Unanswered question
                result = {
                    "question_id": question_id,
                    "score": 0,
                    "feedback": "This question was not answered.",
                    "is_correct": False,
                    "skill_tag": question.get("skill_tag"),
                    "difficulty": question.get("difficulty"),
                    "question_type": question.get("question_type")
                }
            else:
                # Evaluate based on question type
                question_type = question.get("question_type", "")
                
                if "MCQ" in question_type:
                    eval_result = evaluate_mcq_answer(
                        user_answer,
                        question.get("expected_answer", "")
                    )
                elif "Coding" in question_type:
                    eval_result = evaluate_coding_answer(
                        user_answer,
                        question.get("sample_test_cases", []),
                        question.get("language", "Python")
                    )
                else:  # Text or Project-based
                    eval_result = evaluate_text_answer(
                        user_answer,
                        question.get("rubric_points", [])
                    )
                
                result = {
                    "question_id": question_id,
                    "score": eval_result.get("score", 0),
                    "feedback": eval_result.get("feedback", ""),
                    "is_correct": eval_result.get("is_correct", False),
                    "skill_tag": question.get("skill_tag"),
                    "difficulty": question.get("difficulty"),
                    "question_type": question.get("question_type"),
                    "expected_answer": question.get("expected_answer", "")
                }
            
            question_results.append(result)
        
        # Calculate overall score
        quiz_score = calculate_quiz_score(question_results)
        
        # Generate next steps
        next_steps = self._generate_next_steps(quiz_score, question_results)
        
        return {
            "status": "success",
            "question_results": question_results,
            "quiz_score": quiz_score,
            "next_steps": next_steps
        }
    
    def _generate_quiz_instructions(self, target_role: str, preferred_language: str) -> str:
        """Generates personalized quiz instructions."""
        return (
            f"Welcome to your personalized {target_role} interview preparation quiz!\n"
            f"This quiz includes role-specific questions tailored to your skill gaps.\n"
            f"Language preference: {preferred_language}\n"
            f"Please provide thoughtful, complete answers. For coding questions, write clean, well-commented code.\n"
            f"Each question will be evaluated and you'll receive personalized feedback."
        )
    
    def _generate_next_steps(self, quiz_score: Dict[str, Any], question_results: List[Dict[str, Any]]) -> List[str]:
        """Generates personalized next steps based on quiz performance."""
        next_steps = []
        weak_skills = quiz_score.get("weak_skills", [])
        performance = quiz_score.get("performance_level", "")
        average_score = quiz_score.get("average_score", 0)
        
        if performance == "Excellent":
            next_steps.append(f"🎯 Great job! Your average score is {average_score}/10. You're well-prepared.")
            next_steps.append("📚 Challenge yourself with harder questions to further strengthen your skills.")
        elif performance == "Good":
            next_steps.append(f"✅ Good performance ({average_score}/10). Here are areas to focus on:")
            for skill in weak_skills[:2]:
                next_steps.append(f"   • Study {skill.replace('_', ' ').title()}")
            next_steps.append("📖 Review the topics mentioned in your feedback and retake the quiz.")
        else:
            next_steps.append(f"⚠️ Your score is {average_score}/10. Let's improve together!")
            for skill in weak_skills[:3]:
                next_steps.append(f"   • Practice: {skill.replace('_', ' ').title()}")
            next_steps.append("💪 Take more practice quizzes and review fundamentals.")
        
        next_steps.append("🔄 Retake the quiz to see your improvement!")
        
        return next_steps
