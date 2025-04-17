import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the email details
sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")

try:
    # Create the message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Automated Email Subject"

    # Body of the email
    body = "Hello, this is an automated email sent using Python!"

    # Attach the email body to the email message
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the SMTP server and send the email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Secure the connection
    
    print("Attempting to log in with provided credentials...")
    print(f"Using email: {sender_email}")
    server.login(sender_email, password)  # Log in to your email account
    
    # Send the email
    server.sendmail(sender_email, receiver_email, msg.as_string())
    
    # Close the server connection
    server.quit()
    
    print("Email sent successfully!")

except smtplib.SMTPAuthenticationError:
    print("Authentication failed. Please check the following:")
    print("1. Make sure you're using an App Password (not your regular password)")
    print("2. Verify the App Password is correct and hasn't expired")
    print("3. Confirm that your Google account settings allow this connection")
    print("4. You can generate a new App Password at: https://myaccount.google.com/apppasswords")

except Exception as e:
    print(f"An error occurred: {e}")