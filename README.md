### A Newsletter Telegram Bot

The purpose of this Telegram bot is to generate personalized e-mails based on the target data received in JSON format in a message.

## Structure:

The project consists of three parts:
1. Telegram API (+ Telegram front-end for user interface).
2. Python backend (distinct modules for the Telegram interface, session management, JSON format validation, LLM calls, SMTP, data storage, and settings).
3. LLM provider (local or remote LLM server, + prepared prompts).
