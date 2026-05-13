import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from job_scraper_bot.config import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_USE_TLS,
    EMAIL_USERNAME,
    EMAIL_PASSWORD,
    EMAIL_FROM,
    EMAIL_TO,
    DIGEST_HTML_FILE,
    DIGEST_TEXT_FILE,
)


class EmailSender:
    @classmethod
    def can_send(cls):
        return bool(EMAIL_USERNAME and EMAIL_PASSWORD and EMAIL_TO)

    @classmethod
    def _build_message(cls):
        message = EmailMessage()
        message["Subject"] = f"Job Digest - {datetime.now().strftime('%Y-%m-%d')}"
        message["From"] = EMAIL_FROM or EMAIL_USERNAME
        message["To"] = EMAIL_TO

        body = cls._load_plain_text()
        message.set_content(body)

        html = cls._load_html()
        if html:
            message.add_alternative(html, subtype="html")

        return message

    @classmethod
    def _load_plain_text(cls):
        if os.path.exists(DIGEST_TEXT_FILE):
            with open(DIGEST_TEXT_FILE, "r", encoding="utf-8") as handle:
                return handle.read()
        return "No jobs available."

    @classmethod
    def _load_html(cls):
        if os.path.exists(DIGEST_HTML_FILE):
            with open(DIGEST_HTML_FILE, "r", encoding="utf-8") as handle:
                return handle.read()
        return None

    @classmethod
    def send_digest(cls):
        if not cls.can_send():
            raise RuntimeError("Email credentials are not configured.")

        message = cls._build_message()
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=60) as smtp:
            if EMAIL_USE_TLS:
                smtp.starttls()
            smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            smtp.send_message(message)
