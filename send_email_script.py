import smtplib
from email.mime.text import MIMEText
import os


os.environ["EMAIL_FROM"] = "your-email@example.com"
os.environ["EMAIL_TO"] = "recipient@example.com"
os.environ["EMAIL_PASSWORD"] = "your-password"



def send_email():
    """
    Sends an email using Gmail's SMTP server based on the 'send' flag.

    :param sender: Sender's email address
    :param recipient: Recipient's email address
    :param subject: Subject of the email
    :param content: Content of the email
    :param send: If True, the email is sent; if False, only a success message is printed
    """
    # Create the email message
    msg = MIMEText('Dear Sir/Madam,\n\n We have detected an health incident. Need your immediate attention.\n\n Please send help.\n\nRegards,\nSmart Sentinel Team')
    msg['Subject'] = 'Smart Sentinel: HIGH ALERT - Health Incident Detected. '
    msg['From'] = os.environ['EMAIL_FROM']
    msg['To'] = os.environ['EMAIL_TO']

    try:
        # Connect to Gmail SMTP server
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()  # Secure the connection
        # Use the environment variable for the password
        s.login(os.environ['EMAIL_FROM'], os.environ['EMAIL_PASSWORD'])
        s.sendmail(os.environ['EMAIL_FROM'], os.environ['EMAIL_TO'], msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        return True

