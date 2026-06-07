import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from pathlib import Path


def send_email(*, recipient_email: str, body: str, subject: str):
    
    config = Path(__file__).resolve().parent.parent / "config" / ".env"
    load_dotenv(dotenv_path=config)

    host = os.getenv("SMTP_HOST")
    if not host:
        raise RuntimeError("SMTP_HOST not configured")

    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("SMTP_FROM")
    if not sender:
        raise RuntimeError("SMTP_FROM not configured")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.set_content(body)

    # choose TLS or plain connection depending on port
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port) as s:
                if user and password:
                    s.login(user, password)
                s.send_message(msg)
        else:
            with smtplib.SMTP(host, port) as s:
                s.starttls()
                if user and password:
                    s.login(user, password)
                s.send_message(msg)
    except Exception as e:
        raise
