# Email Sender App

A Streamlit application that allows users to send emails with attachments using SMTP.

## Features

- Send emails with text content
- Attach files (PDF, TXT, DOCX, XLSX, PNG, JPG)
- Configuration via environment variables or Streamlit secrets
- Responsive UI with error handling
- Settings management interface

## Local Development

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your email credentials:
   ```
   SENDER_EMAIL=your-email@gmail.com
   RECEIVER_EMAIL=recipient@example.com  
   EMAIL_PASSWORD=your-app-password
   ```
5. Run the app:
   ```
   streamlit run streamlit_app.py
   ```

## Deploying to Streamlit Cloud

1. Fork this repository to your GitHub account
2. Create a new app in [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect to your GitHub repository
4. In the app settings, add your secrets:
   ```
   [secrets]
   SENDER_EMAIL = "your-email@gmail.com"
   RECEIVER_EMAIL = "recipient@example.com"
   EMAIL_PASSWORD = "your-app-password"
   ```
5. Deploy!

## Gmail App Password

To use with Gmail:

1. Make sure 2-Step Verification is enabled on your Google account
2. Generate an App Password from [Google Account Security](https://myaccount.google.com/security)
3. Use this App Password in the app instead of your regular password

## License

MIT 