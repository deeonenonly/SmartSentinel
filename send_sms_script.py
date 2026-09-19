import smtplib
import os

# Carrier gateways for email-to-SMS
CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com",
    "new_carrier": "@gateway.example.com"
}

def send_sms():
    """
    Sends an SMS via email-to-SMS gateway using Gmail's SMTP server.

    :param phone_number: The recipient's phone number (from environment variable)
    :param carrier: The recipient's carrier (from environment variable)
    :param message: The message to send (from environment variable)
    """
    # Get values from environment variables
    phone_number = os.getenv('PHONE_NUMBER')
    carrier = os.getenv('SMS_CARRIER')  # Default to 'verizon' if not set
    message = os.getenv('SMS_MESSAGE')  # Default message

    if not phone_number or carrier not in CARRIERS:
        print("Error: Missing or incorrect environment variables.")
        return False

    # Create recipient address using phone number and carrier gateway
    recipient = phone_number + CARRIERS[carrier]

    # Sender's email credentials from environment variables
    email = os.getenv('EMAIL_FROM')
    password = os.getenv('EMAIL_PASSWORD')

    if not email or not password:
        print("Error: Missing email credentials.")
        return False

    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(email, password)

            # Send the SMS (email to SMS gateway)
            server.sendmail(email, recipient, message)
            print("Message sent successfully!")
            print(f"Phone Number: {phone_number}")
            print(f"Carrier: {carrier}")
            print(f"Message: {message}")

    except Exception as e:
        print(f"Failed to send message: {e}")
        return False

    return True

if __name__ == "__main__":

    send_sms()