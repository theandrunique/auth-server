import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any

import jwt
from config import settings


class EmailTokenType(Enum):
    RECOVERY_PASSWORD = "recovery"
    VERIFY_EMAIL = "verify"


def send_email(
    email_to: str,
    subject: str,
    html_body: str,
) -> None:
    msg = MIMEMultipart()
    msg["From"] = f"{settings.EMAILS_FROM_NAME} {settings.EMAILS_FROM_EMAIL}"
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    server.send_message(msg=msg)
    server.quit()


def send_test_email() -> None:
    send_email(
        email_to=settings.EMAILS_FROM_EMAIL,
        subject=f"{settings.PROJECT_NAME} - Test email",
        html_body="<p>Test email message</p>",
    )


def send_reset_password_email(email_to: str) -> None:
    token = generate_email_token(email=email_to, type=EmailTokenType.RECOVERY_PASSWORD)
    send_email(
        email_to=email_to,
        subject=f"{settings.PROJECT_NAME} - Password recovery for user {email_to}",
        html_body=f"<p>Use the token to recovery your password: {token}</p>",
    )


def send_verify_email(email_to: str, username: str) -> None:
    token = generate_email_token(email=email_to, type=EmailTokenType.VERIFY_EMAIL)
    send_email(
        email_to=email_to,
        subject=f"{settings.PROJECT_NAME} - Verify email for user {username}",
        html_body=f"<p>Use the following token to verify email: {token}</p>",
    )


def generate_email_token(email: str, type: EmailTokenType) -> str:
    encoded_jwt = jwt.encode(
        {
            "exp": (
                datetime.utcnow()
                + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
            ),
            "sub": email,
            "type": type.value,
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_email_token(token: str, type: EmailTokenType) -> str | None:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload["type"] != type.value:
            raise jwt.exceptions.PyJWTError()
        if not isinstance(payload["sub"], str):
            raise ValueError("Invalid payload")
        return payload["sub"]
    except (jwt.exceptions.PyJWTError, KeyError):
        return None