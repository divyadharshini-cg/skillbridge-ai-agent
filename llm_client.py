import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMClient:
    """
    Client for interacting with Google Gemini LLMs.
    Provides fallback mock mode if GOOGLE_API_KEY is missing.
    """
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self.is_mock = not self.api_key or self.api_key == "your_gemini_api_key_here"
        
        if not self.is_mock:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(model_name)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}. Falling back to mock.")
                self.is_mock = True
                self.model = None
        else:
            self.model = None

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generate content using Gemini or a mock response if the API key is not configured.
        """
        if self.is_mock:
            mock_resp = f"[MOCK RESPONSE - GOOGLE_API_KEY not set]\n"
            mock_resp += f"System Instruction: {system_instruction}\n"
            mock_resp += f"Prompt: {prompt[:100]}..."
            return mock_resp
        
        try:
            if system_instruction:
                # Instantiate model with system instructions
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction
                )
            else:
                model = self.model if self.model else genai.GenerativeModel(self.model_name)
                
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[LLM Error: {str(e)} - Falling back to local model check or debug]"
