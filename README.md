## A Newsletter Telegram Bot

The purpose of this Telegram bot is to generate personalized e-mails based on the target data received in JSON format in a message.

## Structure:

The project consists of three parts:
1. Telegram API (+ Telegram front-end for user interface).
2. Python backend (distinct modules for the Telegram interface, session management, JSON format validation, LLM calls, SMTP, data storage, settings, etc.).
3. LLM provider (local or remote LLM server, + prepared prompts).

## JSON Template (for input):
```python
{
    "full_name": "",
    "position": "",
    "email": "",
    "preferences": [
        "",
        ""
    ],
    "products": [
        {
            "name": "",
            "description": ""
        }
    ],
    "language": "",
    "gender": ""
}
```

## JSON Template (for logging):
```python
{
    "request_id": "",
    "created_at": "",
    "user_message": "",
    "recipient": {
        "full_name": "",
        "email": "",
        "position": "",
        "gender": ""
    },
    "preferences": [
        "",
        ""
    ],
    "selected_products": [
        ""
    ],
    "language": "",
    "generated_email": "",
    "status": "",
    "error": null
}
```

## A hint on running locally:
Install dependencies from requirements-local.txt. Beforehand, run the following command if you want to compile llama-cpp with NVIDIA GPU support:
```bash
export CMAKE_ARGS="-DGGML_CUDA=on"
```