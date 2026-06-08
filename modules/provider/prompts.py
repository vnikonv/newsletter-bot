from typing import List, Annotated
from pydantic import BaseModel, EmailStr, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)

Preference = Annotated[
    str,
    Field(min_length=1, max_length=30)
]

class PromptModel(BaseModel):
    full_name: str = Field(min_length=1, max_length=50)
    position: str = Field(min_length=1, max_length=30)
    email: EmailStr = Field(min_length=1)
    preferences: List[Preference] = Field(min_length=1, max_length=5)
    products: List[Product] = Field(min_length=1, max_length=3)
    language: str = Field(min_length=1, max_length=20)
    gender: str = Field(min_length=1, max_length=15)

class ValidatePrompt():
    def __init__(self, prompt: dict): # Validates and stores structured model
        self.prompt = PromptModel.model_validate(prompt)
    def build(self) -> str:
        # Convert preferences list into text
        preferences_text = ", ".join( self.prompt.preferences )
        # Convert products into readable text
        products_text = "\n".join( [ f"- {product.name}: {product.description}" for product in self.prompt.products ] )
        # Build final LLM prompt
        final_prompt = f"""You are sending a personalized newsletter for native integration/advertisement of products from the provided list. Data on your target: Full Name: {self.prompt.full_name} Position: {self.prompt.position} Interests: {preferences_text} Products: {products_text} Gender: {self.prompt.gender} Make a natural-sounding original short personal letter in {self.prompt.language}. Include the product's name in the letter. Show knowledge of target's personal/professional interests. Without preparations, begin generating the final text of the e-mail right away. Choose your sender's full name that corresponds to the target's cultural background and gender. Feel free to fill every field in the letter yourself."""
        return final_prompt.strip()
