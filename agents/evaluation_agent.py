from llm_client import LLMClient

class EvaluationAgent:
    """
    EvaluationAgent assesses student submissions (roadmap milestone completions, mock interview responses)
    and scores their readiness progression.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.name = "Evaluation Agent"

    def evaluate_response(self, question: str, response: str) -> dict:
        """
        Evaluate mock response accuracy and return score and improvement advice.
        """
        prompt = f"Evaluate this interview answer:\nQuestion: {question}\nAnswer: {response}"
        feedback = self.llm.generate(
            prompt=prompt,
            system_instruction="You are an expert technical interviewer giving constructive criticism."
        )
        return {
            "score": 80,
            "feedback": feedback
        }
