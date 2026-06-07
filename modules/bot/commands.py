import json

from telegram import Update
from telegram.ext import ContextTypes

from modules.storage.session_store import SessionStore
from modules.storage.logging import Logging

from modules.provider.api_model import GenerateAPI
from modules.provider.prompts import ValidatePrompt
from modules.spam.sender import send_email


session_store = SessionStore()
log_store = Logging()


WELCOME_MESSAGE = """
Welcome.

Send your prompt in the following format:
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
"""


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    session_store.create_session(
        telegram_user_id=user_id
    )

    await update.message.reply_text(
        WELCOME_MESSAGE
    )


async def handle_json_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    raw_text = update.message.text

    try:
        payload = json.loads(raw_text)

    except json.JSONDecodeError:
        await update.message.reply_text(
            "Invalid JSON."
        )
        return

    try:
        validator = ValidatePrompt(payload)

        final_prompt = validator.build()

    except Exception as error:
        await update.message.reply_text(
            f"Validation error:\n{error}"
        )
        return

    generated_email = GenerateAPI.generate(final_prompt)

    session_store.update_session(
        telegram_user_id=user_id,
        state="EMAIL_GENERATED",
        raw_input_json=payload,
        generated_email=generated_email
    )

    await update.message.reply_text(
        generated_email
    )


async def regenerate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    session = session_store.get_session(
        user_id
    )

    if not session:
        await update.message.reply_text(
            "No active session."
        )
        return

    if not session.raw_input_json:
        await update.message.reply_text(
            "No previous input exists."
        )
        return

    validator = ValidatePrompt(
        session.raw_input_json
    )

    final_prompt = validator.build()

    generated_email = GenerateAPI.generate(
        final_prompt
    )

    session_store.update_session(
        telegram_user_id=user_id,
        generated_email=generated_email
    )

    await update.message.reply_text(
        generated_email
    )


async def change_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    session = session_store.get_session(
        user_id
    )

    if not session:
        await update.message.reply_text(
            "No active session."
        )
        return

    args = context.args

    if not args:
        await update.message.reply_text(
            "Provide modified email text."
        )
        return

    modified_email = " ".join(args)

    session_store.update_session(
        telegram_user_id=user_id,
        generated_email=modified_email
    )

    await update.message.reply_text(
        "Email updated."
    )


async def send_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    session = session_store.get_session(
        user_id
    )

    if not session:
        await update.message.reply_text(
            "No active session."
        )
        return

    if not session.generated_email:
        await update.message.reply_text(
            "No generated email exists."
        )
        return

    recipient_email = (
        session.raw_input_json["email"]
    )

    try:
        send_email(
            recipient_email=recipient_email,
            body=session.generated_email
        )

    except Exception as error:
        await update.message.reply_text(
            f"Send failed:\n{error}"
        )
        return

    log_store.save_completed_request(
        session
    )

    session_store.delete_session(
        user_id
    )

    await update.message.reply_text(
        "Email sent successfully."
    )


async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    session_store.delete_session(
        user_id
    )

    await update.message.reply_text(
        "Session cancelled."
    )
