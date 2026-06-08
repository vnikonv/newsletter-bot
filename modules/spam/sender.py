import os
import ssl
import smtplib

from email.message import EmailMessage


def send_email(*, recipient_email: str, body: str, subject: str):

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

    tls_context = ssl.create_default_context()

    if port == 465:

        # implicit TLS
        with smtplib.SMTP_SSL(
            host,
            port,
            context=tls_context,
        ) as s:

            if user and password:
                s.login(user, password)

            s.send_message(msg)

    else:

        # explicit TLS via STARTTLS
        with smtplib.SMTP(host, port) as s:

            s.ehlo()

            s.starttls(context=tls_context)

            s.ehlo()

            if user and password:
                s.login(user, password)

            s.send_message(msg)
