"""
mailer/email_sender.py
Sends emails via SMTP with PDF/file attachments
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config import CONFIG

log = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.host = CONFIG["smtp_host"]
        self.port = CONFIG["smtp_port"]
        self.user = CONFIG["smtp_user"]
        self.password = CONFIG["smtp_password"]
        self.from_email = CONFIG["your_email"]

    def send(self, to_email: str, subject: str, body: str, attachments: list = None) -> bool:
        """
        Send an email with optional file attachments.
        Returns True on success, False on failure.
        """
        if not to_email:
            log.warning("  No recipient email — skipping send")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = f"{CONFIG['your_name']} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            # Email body (plain text)
            msg.attach(MIMEText(body, "plain"))

            # Attach files (resume, portfolio, etc.)
            if attachments:
                for filepath in attachments:
                    if not os.path.exists(filepath):
                        log.warning(f"  Attachment not found: {filepath} — skipping")
                        continue
                    self._attach_file(msg, filepath)
                    log.info(f"  📎 Attached: {os.path.basename(filepath)}")

            # Connect and send
            with smtplib.SMTP(self.host, self.port) as server:
                server.ehlo()
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            log.info(f"  ✅ Email sent to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            log.error("  ❌ SMTP auth failed — check your email/app password in config.py")
            return False
        except smtplib.SMTPException as e:
            log.error(f"  ❌ SMTP error: {e}")
            return False
        except Exception as e:
            log.error(f"  ❌ Unexpected error sending email: {e}")
            return False

    def _attach_file(self, msg: MIMEMultipart, filepath: str):
        """Attach a file to the email message."""
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={filename}"
        )
        msg.attach(part)