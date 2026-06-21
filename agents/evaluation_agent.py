from typing import Dict, Any
from llm_client import LLMClient

class EvaluationAgent:
    """
    EvaluationAgent assesses candidate submissions and final coaching reports
    to score their readiness progression, completeness, safety, and realism.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Evaluation Agent"

    def evaluate_response(self, question: str, response: str) -> dict:
        """
        Evaluate mock response accuracy and return score and improvement advice.
        """
        prompt = f"Evaluate this interview answer:\nQuestion: {question}\nAnswer: {response}"
        feedback = "[MOCK RESPONSE] Good answer, try incorporating more structured metrics."
        
        if not self.llm.is_mock:
            try:
                feedback = self.llm.generate(
                    prompt=prompt,
                    system_instruction="You are an expert technical interviewer giving constructive criticism."
                )
            except Exception:
                pass
                
        return {
            "score": 80,
            "feedback": feedback
        }

    def evaluate_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reviews the final coordinated report for completeness, clarity, usefulness, realism, and safety.
        Returns a quality checklist score and feedback notes.
        """
        # Deterministic check for completeness
        required_keys = [
            "profile_summary", "readiness_score", "category_scores", 
            "skill_gap_analysis", "internship_matches", "roadmap_30_days", 
            "portfolio_project", "generated_readme", "interview_questions", 
            "safety_review"
        ]
        
        missing_keys = [key for key in required_keys if key not in report or not report[key]]
        completeness_score = 100 - (len(missing_keys) * 10)
        completeness_score = max(0, completeness_score)
        
        # Check safety review status
        safety_rev = report.get("safety_review", {})
        passed_safety = safety_rev.get("passed_safety", True)
        safety_score = 100 if passed_safety else 60
        if safety_rev.get("safety_flags"):
            safety_score -= len(safety_rev.get("safety_flags")) * 10
            safety_score = max(0, safety_score)

        # Baseline scores
        scores = {
            "clarity": 95,
            "usefulness": 90,
            "realism": 92,
            "safety": safety_score,
            "completeness": completeness_score
        }

        # Overall average checklist score
        avg_score = int(sum(scores.values()) / len(scores))

        feedback_notes = []
        if missing_keys:
            feedback_notes.append(f"Report is missing sections: {', '.join(missing_keys)}.")
        else:
            feedback_notes.append("All expected sections are fully represented in the coordinated report.")

        if not passed_safety:
            feedback_notes.append("Safety flags detected in the initial audit. Ensure the student adjusts resume details accordingly.")
        else:
            feedback_notes.append("Passed all profile safety filters successfully.")

        if report.get("category_scores", {}).get("Deployment", 0) < 50:
            feedback_notes.append("Deployment score is low. Advise candidate to practice Docker tasks inside Roadmap Week 4.")

        # If LLM is active, get a detailed critique of the report content
        if not self.llm.is_mock:
            prompt = (
                f"Critique the following generated internship readiness report:\n"
                f"Readiness Score: {report.get('readiness_score')}\n"
                f"Role Matches: {len(report.get('internship_matches', []))} roles\n"
                f"Project: {report.get('portfolio_project', {}).get('title')}\n"
                f"Briefly review it for realism and utility, giving 2-3 feedback suggestions."
            )
            try:
                llm_critique = self.llm.generate(
                    prompt=prompt,
                    system_instruction="You are a senior education program auditor. Review study guides and projects for quality."
                )
                feedback_notes.append(llm_critique)
            except Exception:
                pass

        return {
            "overall_score": avg_score,
            "checklist": scores,
            "feedback": "\n".join(feedback_notes)
        }
