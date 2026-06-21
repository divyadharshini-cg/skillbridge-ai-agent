import os
import google.generativeai as genai
from dotenv import find_dotenv, dotenv_values

def get_env_api_key() -> str:
    """
    Reads the GOOGLE_API_KEY directly and strictly from the .env file.
    Does not read from general os.environ if it is not in the .env file.
    """
    try:
        env_file = find_dotenv()
        if env_file:
            config = dotenv_values(env_file)
            key = config.get("GOOGLE_API_KEY")
            if key:
                return key.strip()
    except Exception:
        pass
    return None

def is_llm_available() -> bool:
    """
    Returns True if a valid Google Gemini API key exists in the .env file.
    """
    key = get_env_api_key()
    if not key:
        return False
    key = key.strip()
    return key != "" and key != "your_gemini_api_key_here"


def polish_text(prompt: str, fallback_text: str, system_instruction: str = None) -> str:
    """
    Polishes the fallback text using Gemini if available.
    If Gemini is not available, or fails for any reason, returns the fallback text.
    Ensures the app never crashes and API keys are not exposed.
    """
    if not is_llm_available():
        return fallback_text
    
    try:
        client = LLMClient()
        polished = client.generate(prompt, system_instruction=system_instruction)
        
        # Check if the generated response is an error or mock indicator
        if not polished or "[LLM Error:" in polished or "[MOCK RESPONSE" in polished:
            return fallback_text
            
        return polished
    except Exception:
        # Never crash and do not expose API keys
        return fallback_text

class LLMClient:
    """
    Client for interacting with Google Gemini LLMs.
    Provides fallback mock mode if GOOGLE_API_KEY is missing.
    """
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.api_key = get_env_api_key()
        self.model_name = model_name
        self.is_mock = not is_llm_available()
        
        if not self.is_mock:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(model_name)
            except Exception as e:
                # Sanitize error message to prevent exposing the key
                err_msg = str(e)
                if self.api_key and self.api_key in err_msg:
                    err_msg = err_msg.replace(self.api_key, "REDACTED_API_KEY")
                print(f"Warning: Failed to initialize Gemini client: {err_msg}. Falling back to mock.")
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
            # Sanitize error message to prevent exposing the key
            err_msg = str(e)
            if self.api_key and self.api_key in err_msg:
                err_msg = err_msg.replace(self.api_key, "REDACTED_API_KEY")
            return f"[LLM Error: {err_msg} - Falling back to local model check or debug]"

