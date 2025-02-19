import smtplib, os, json
from email.message import EmailMessage
from dotenv import load_dotenv
from email.mime.text import MIMEText


load_dotenv()

async def send_email_verification_otp(message):
    try:
        receiver_address = message["email"]
        subject = message["subject"]
        body = message["body"]

        await send_email(receiver_address, subject, body)

        print("Signup OTP email sent!")
    except Exception as e:
        print(f"Failed to send OTP email: {e}")


async def send_password_reset_email(message):
    try:
        receiver_address = message["email"]
        subject = message["subject"]
        body = message["body"]

        await send_email(receiver_address, subject, body)

        print("Password reset email sent!")
    except Exception as e:
        print(f"Failed to send password reset email: {e}")


async def send_email(receiver_address, subject, body):
    sender_address = os.environ.get("GMAIL_ADDRESS")
    sender_password = os.environ.get("GMAIL_PASSWORD")

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_address, sender_password)

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_address
    msg['To'] = receiver_address

    server.sendmail(sender_address, receiver_address, msg.as_string())
    server.quit()

# async def notification(message):
#     try:
#         #message = json.loads(message)
#         receiver_address = message["email"]
#         subject = message["subject"]
#         body = message["body"]
        

#         sender_address = os.environ.get("GMAIL_ADDRESS")
#         sender_password = os.environ.get("GMAIL_PASSWORD")
        

#         # Gmail SMTP server settings
#         smtp_server = 'smtp.gmail.com'
#         smtp_port = 587

#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()
#         server.login(sender_address, sender_password)

#         # Compose the email message
#         msg = MIMEText(body)
#         msg['Subject'] = subject
#         msg['From'] = sender_address
#         msg['To'] = receiver_address

#         server.sendmail(sender_address, receiver_address, msg.as_string())
#         server.quit()

#         print("Mail Sent")
#     except Exception as e:
#         print(f"Failed to send email: {e}")