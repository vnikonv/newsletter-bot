from modules.provider.interface import GenerateResponse
from huggingface_hub import InferenceClient
from pathlib import Path
from dotenv import load_dotenv
from modules.config.settings import API_MODEL
import os

class GenerateAPI(GenerateResponse):
    def generate(self, prompt: str) -> str:

        config = Path(__file__).resolve().parent.parent / "config" / ".env"
        load_dotenv(dotenv_path=config)

        HF_TOKEN = os.getenv("TOKEN")
        MODEL_ID = API_MODEL

        client = InferenceClient(
            provider="auto",  # HuggingFace chooses available provider
            api_key=HF_TOKEN,
        )

        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise technical assistant."
                },
                {
                    "role": "user",
                    "content": f"{prompt}"
                }
            ],
            max_tokens=10,
            temperature=0.7,
        )

        return str(response.choices[0].message.content)
