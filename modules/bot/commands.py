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
New session initialized.

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
    _context: ContextTypes.DEFAULT_TYPE
):
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if session_store.get_session(user_id):
        if not update.message:
            return
        await update.message.reply_text(
            "A session already exists."
        )
        return

    session_store.create_session(
        telegram_user_id=user_id
    )

    if not update.message:
        return

    await update.message.reply_text(
        WELCOME_MESSAGE
    )


async def handle_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id

    raw_text = update.message.text or ""

    # if the session is awaiting a modified email, accept this text as the
    # modified email body instead of interpreting it as JSON
    session = session_store.get_session(user_id)
    if session and session.state == "AWAITING_MODIFIED_EMAIL":
        modified_email = raw_text.strip()
        if not modified_email:
            await update.message.reply_text("Please send the modified email text.")
            return

        session_store.update_session(
            user_message=raw_text,
            telegram_user_id=user_id,
            state="EMAIL_GENERATED",
            generated_email=modified_email
        )

        await update.message.reply_text("Email text updated.")
        return
    
    if session and session.state == "SETTING_EMAIL_ADDRESS":
        modified_address = raw_text.strip()
        session_store.update_session(
            user_message=raw_text,
            telegram_user_id=user_id,
            state="EMAIL_ADDRESS_SET",
            recipient_email=modified_address
        )

        await update.message.reply_text("Email address updated.")
        return

    if not raw_text:
        await update.message.reply_text("Invalid JSON.")
        return

    try:
        payload = json.loads(raw_text)

    except json.JSONDecodeError:
        await update.message.reply_text("Invalid JSON.")
        return

    try:
        validator = ValidatePrompt(dict(payload))
        final_prompt = validator.build()

    except Exception as error:
        await update.message.reply_text(f"Validation error:\n{error}")
        return

    generated_email = GenerateAPI().generate(final_prompt)

    session_store.update_session(
        user_message=raw_text,
        telegram_user_id=user_id,
        state="EMAIL_GENERATED",
        raw_input_json=payload,
        final_prompt=final_prompt,
        generated_email=generated_email,
        recipient_email=payload.get("email"),
    )

    await update.message.reply_text(generated_email)


async def regenerate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.effective_user or not update.message:
        return

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

    if not session.final_prompt:
        validator = ValidatePrompt(dict(session.raw_input_json))
        final_prompt = validator.build()
    else:
        final_prompt = session.final_prompt

    generated_email = GenerateAPI().generate(final_prompt)

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
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id

    session = session_store.get_session(user_id)

    if not session:
        await update.message.reply_text("No active session.")
        return

    # set session state so the next plain-text message is treated as the
    # modified email body
    session_store.update_session(
        telegram_user_id=user_id,
        state="AWAITING_MODIFIED_EMAIL",
    )

    await update.message.reply_text("Please send the modified email text as a message.")


async def send_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.effective_user or not update.message:
        return

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

    recipient_email = None
    if session.recipient_email:
        recipient_email = session.recipient_email

    if not recipient_email:
        session_store.update_session(
            telegram_user_id=user_id,
            state="SETTING_EMAIL_ADDRESS",
        )

        await update.message.reply_text(
            "Recipient email not found in session data. Please enter the email or cancel the session."
        )
        return

    try:
        send_email(
            recipient_email=recipient_email,
            body=session.generated_email,
            subject=session.generated_email.split('\n', 1)[0]
        )

    except Exception as error:
        session_store.update_session(
            telegram_user_id=user_id,
            state="FAIL",
        )

        log_store.save_completed_request(
            session=session_store.get_session(user_id), error=f"{error}"
        )

        await update.message.reply_text(
            f"Send failed:\n{error}"
        )
        return
    
    session_store.update_session(
        telegram_user_id=user_id,
        state="SUCCESS",
    )

    log_store.save_completed_request(
        session=session_store.get_session(user_id), error=None
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
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id

    session_store.delete_session(
        user_id
    )

    await update.message.reply_text(
        "Session cancelled."
    )

async def see_email(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.effective_user or not update.message:
        return

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
            "No email has been generated for this session."
        )
        return
    
    current_email = session.generated_email
    await update.message.reply_text(
        f"{current_email}"
    )
