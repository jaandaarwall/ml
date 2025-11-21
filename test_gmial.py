import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SMTP_SERVER_HOST = "smtp.gmail.com"
SMTP_SERVER_PORT = 587
SENDER_ADDRESS = "rivisia47@gmail.com"
SENDER_PASSWORD = "glsq rmah ooxz itej"   # 16-character Gmail App Password

def send_email(to_address, subject, message, content="html", attachment_file=None):
    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject

    # Email body
    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    # Attachment handling
    if attachment_file:
        with open(attachment_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={attachment_file}")
        msg.attach(part)

    # Gmail SMTP connection
    server = smtplib.SMTP(SMTP_SERVER_HOST, SMTP_SERVER_PORT)
    server.starttls()  # Required by Gmail
    server.login(SENDER_ADDRESS, SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()

    return True


send_email(
    to_address="23f1003066@ds.study.iitm.ac.in",
    subject="Test Email",
    message="<h1>Hello from Python!</h1>",
    content="html"
)
