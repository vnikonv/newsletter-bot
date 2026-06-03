from modules.provider.api_model import GenerateAPI
from modules.provider.local_model import GenerateLocal

provider = GenerateAPI()
provider2 = GenerateLocal()

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
print()
print(provider2.generate(prompt))
