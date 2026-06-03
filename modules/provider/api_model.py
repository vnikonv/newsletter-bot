from modules.provider.interface import GenerateResponse
from modules.provider.prompts import ValidatePrompt
from huggingface_hub import InferenceClient
from pathlib import Path
from dotenv import load_dotenv
from modules.config.settings import API_MODEL, IS_COMPLETIONS, API_PROVIDER
import os

class GenerateAPI(GenerateResponse):
    def generate(self, prompt: dict) -> str:

        config = Path(__file__).resolve().parent.parent / "config" / ".env"
        load_dotenv(dotenv_path=config)

        HF_TOKEN = os.getenv("TOKEN")
        MODEL_ID = API_MODEL
        provider = API_PROVIDER if API_PROVIDER != "" else "auto"

        prompt_final = ValidatePrompt(prompt).build()

        client = InferenceClient(
            provider=provider,
            api_key=HF_TOKEN,
        )

        if IS_COMPLETIONS:
            response = client.chat.completions.create(
                model=MODEL_ID,
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
                temperature=0.65,
                stop=["<think>", "</think>"],
            )

            return str(response.choices[0].message.content)
        else:
            response = client.text_generation(
                        model=MODEL_ID,
                        prompt=prompt_final,
                        max_new_tokens=500,
                        temperature=0.65,
                        stop=["<think>", "</think>"],
            )
            
            return str(response)
