from modules.provider.interface import GenerateResponse
from modules.provider.prompts import ValidatePrompt
from modules.config.settings import LOCAL_MODEL
from typing import Optional

class GenerateLocal(GenerateResponse):
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or LOCAL_MODEL

    def _ensure_loaded(self):
        if not self.model_path:
            raise RuntimeError("LOCAL_MODEL is not set in settings; cannot load local model")

        try:
            from llama_cpp import Llama
        except Exception as e:
            raise RuntimeError(
                "llama-cpp-python is required for local model support: install with 'pip install -r requirements-local.txt'"
            ) from e

        self._client = Llama(model_path=self.model_path)

    def generate(self, prompt: dict) -> str:
        self._ensure_loaded()

        prompt_final = ValidatePrompt(prompt).build()

        response = self._client.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Write only the final e-mail text. Do not include reasoning, explanations, analysis, or commentary"
                    },
                    {
                        "role": "user",
                        "content": prompt_final
                    }
                ],
                max_tokens=500,
                temperature=0.65
            )
        
        return str(response).strip()
