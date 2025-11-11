import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Email Configuration
SMTP_SERVER_HOST = "localhost"  # Change to your SMTP server
SMTP_SERVER_PORT = 1025  # Mailhog default port
SENDER_ADDRESS = "hospital@noreply.com"
SENDER_PASSWORD = ""


def send_email(to_address, subject, message, content="html", attachment_file=None):
    """Send email with optional attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = subject

        if content == "html":
            msg.attach(MIMEText(message, "html"))
        else:
            msg.attach(MIMEText(message, "plain"))

        if attachment_file and os.path.exists(attachment_file):
            with open(attachment_file, 'rb') as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            filename = os.path.basename(attachment_file)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

        s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
        s.login(SENDER_ADDRESS, SENDER_PASSWORD)
        s.send_message(msg)
        s.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
