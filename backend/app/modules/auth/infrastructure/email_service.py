from __future__ import annotations

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.modules.auth.domain.interfaces import EmailMessage, EmailSender

logger = logging.getLogger("tsbl.auth.email")


class SMTPEmailSender(EmailSender):
    async def send(self, message: EmailMessage) -> None:
        if not settings.smtp_host:
            logger.warning(f"SMTP not configured. Skipping email to {message.to}: {message.subject}")
            return

        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["From"] = settings.smtp_from_email
        msg["To"] = message.to
        msg["Subject"] = message.subject

        msg.attach(MIMEText(message.body, "plain"))
        if message.html_body:
            msg.attach(MIMEText(message.html_body, "html"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user or None,
                password=settings.smtp_password or None,
                use_tls=settings.smtp_use_tls,
            )
            logger.info(f"Email sent to {message.to}: {message.subject}")
        except Exception as exc:
            logger.error(f"Failed to send email to {message.to}: {exc}")
            raise


class ConsoleEmailSender(EmailSender):
    async def send(self, message: EmailMessage) -> None:
        logger.info(f"[EMAIL] To: {message.to} | Subject: {message.subject} | Body: {message.body}")


def get_email_sender() -> EmailSender:
    if settings.smtp_host:
        return SMTPEmailSender()
    return ConsoleEmailSender()
