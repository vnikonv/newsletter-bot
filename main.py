from modules.provider.api_model import GenerateAPI

provider = GenerateAPI()

prompt = {
    "full_name": "Василий Олегович Баснецев",
    "position": "HR Manager",
    "email": "alice@example.com",
    "preferences": [
        "career growth"
    ],
    "products": [
        {
            "name": "Analytics Suite",
            "description": "Cloud-based reporting platform"
        }
    ],
    "language": "Russian",
    "gender": "masculine"
}

print(provider.generate(prompt))
