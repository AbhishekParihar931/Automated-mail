import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import time

# Load environment variables - works both locally with .env and in Streamlit Cloud
load_dotenv()

# Function to load email history
def load_history():
    if os.path.exists("email_history.json"):
        try:
            with open("email_history.json", "r") as f:
                return json.load(f)
        except:
            return []
    return []

# Function to save email history
def save_to_history(sender, recipients, subject, status, error=None):
    history = load_history()
    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sender": sender,
        "recipients": recipients,
        "subject": subject,
        "status": status,
        "error": error
    })
    with open("email_history.json", "w") as f:
        json.dump(history, f, indent=4)

# Set page config
st.set_page_config(
    page_title="Advanced Email Sender",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #4285F4, #34A853, #FBBC05, #EA4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .subheader {
        font-size: 1.2rem;
        color: #5F6368;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 0.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        color: #721c24;
        border-radius: 0.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    .warning-message {
        padding: 1rem;
        background-color: #fff3cd;
        color: #856404;
        border-radius: 0.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #4285F4;
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    .stProgress > div > div {
        background-color: #4285F4;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
        text-align: center;
    }
    .status-success {
        background-color: #d4edda;
        color: #155724;
    }
    .status-failed {
        background-color: #f8d7da;
        color: #721c24;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.image("https://ssl.gstatic.com/ui/v1/icons/mail/rfr/logo_gmail_lockup_default_1x_r5.png", width=200)
    st.markdown("---")
    
    # Navigation
    page = st.radio("Navigation", ["Send Email", "Email History", "Settings"])

# Main header
st.markdown("<h1 class='main-header'>Advanced Email Sender</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>A powerful tool for managing your email communications</p>", unsafe_allow_html=True)

# Get default values from environment variables or Streamlit secrets
# Try to get from Streamlit secrets first (for cloud deployment)
try:
    default_sender = st.secrets["SENDER_EMAIL"]
    default_receiver = st.secrets["RECEIVER_EMAIL"]
    default_password = st.secrets["EMAIL_PASSWORD"]
except:
    # Fall back to .env file (for local development)
    default_sender = os.getenv("SENDER_EMAIL", "")
    default_receiver = os.getenv("RECEIVER_EMAIL", "")
    default_password = os.getenv("EMAIL_PASSWORD", "")

# Send Email Page
if page == "Send Email":
    st.header("Send New Email")
    
    with st.form(key="email_form"):
        sender_email = st.text_input("From Email", value=default_sender)
        
        # Multiple recipients
        recipients_input = st.text_input(
            "To Email(s)", 
            value=default_receiver,
            help="You can enter multiple email addresses separated by commas"
        )
        
        cc_input = st.text_input(
            "CC", 
            value="",
            help="Carbon Copy recipients (optional)"
        )
        
        subject = st.text_input("Subject", "")
        
        # Email content with formatting options
        st.write("Message Content:")
        message_type = st.selectbox("Format", ["Plain Text", "HTML"], index=0)
        message = st.text_area("", "", height=200)
        
        # File attachment
        uploaded_file = st.file_uploader("Attach File (optional)", type=["pdf", "txt", "docx", "xlsx", "png", "jpg"])
        
        # Priority
        priority = st.select_slider(
            "Priority", 
            options=["Low", "Normal", "High"],
            value="Normal"
        )
        
        # Password
        col1, col2 = st.columns([3, 1])
        with col1:
            password = st.text_input("App Password", value=default_password, type="password")
        
        with col2:
            st.write("")
            st.write("")
            test_mode = st.checkbox("Test Mode", 
                                   help="In test mode, the email won't be sent but validation will be performed")
        
        submit_button = st.form_submit_button(label="Send Email")
    
    # Handle form submission
    if submit_button:
        # Validate inputs
        if not sender_email or not recipients_input or not subject or not message or not password:
            st.markdown("<div class='error-message'>Please fill in all required fields</div>", unsafe_allow_html=True)
        else:
            # Process recipients (split by commas and strip whitespace)
            recipients_list = [email.strip() for email in recipients_input.split(",")]
            cc_list = [email.strip() for email in cc_input.split(",")] if cc_input else []
            
            # Validate email format (basic check)
            invalid_emails = [email for email in recipients_list + cc_list if "@" not in email or "." not in email]
            
            if invalid_emails and invalid_emails != ['']: 
                st.markdown(f"<div class='error-message'>Invalid email format: {', '.join(invalid_emails)}</div>", unsafe_allow_html=True)
            else:
                if test_mode:
                    st.markdown("<div class='warning-message'>Test Mode: Email validation passed, but message was not sent.</div>", unsafe_allow_html=True)
                    # Save to history in test mode
                    save_to_history(sender_email, recipients_input, subject, "TEST", "Test mode - not actually sent")
                else:
                    try:
                        # Create the message
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = recipients_input
                        if cc_input:
                            msg['Cc'] = cc_input
                        msg['Subject'] = subject
                        
                        # Set priority header if needed
                        if priority == "High":
                            msg['X-Priority'] = '1'
                        elif priority == "Low":
                            msg['X-Priority'] = '5'
                        
                        # Body of the email
                        if message_type == "Plain Text":
                            msg.attach(MIMEText(message, 'plain'))
                        else:
                            msg.attach(MIMEText(message, 'html'))
                        
                        # Attach file if uploaded
                        if uploaded_file is not None:
                            attachment = MIMEApplication(uploaded_file.getvalue())
                            attachment.add_header(
                                'Content-Disposition', 
                                'attachment', 
                                filename=uploaded_file.name
                            )
                            msg.attach(attachment)
                        
                        # Setup progress indicators
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Connect to the SMTP server and send the email
                        status_text.text("Connecting to SMTP server...")
                        progress_bar.progress(20)
                        time.sleep(0.5)
                        
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        
                        status_text.text("Securing connection...")
                        progress_bar.progress(40)
                        time.sleep(0.5)
                        
                        server.starttls()
                        
                        status_text.text("Authenticating...")
                        progress_bar.progress(60)
                        time.sleep(0.5)
                        
                        server.login(sender_email, password)
                        
                        status_text.text("Sending email...")
                        progress_bar.progress(80)
                        time.sleep(0.5)
                        
                        all_recipients = recipients_list + cc_list
                        server.sendmail(sender_email, all_recipients, msg.as_string())
                        
                        status_text.text("Finishing up...")
                        progress_bar.progress(100)
                        time.sleep(0.5)
                        
                        # Close the server connection
                        server.quit()
                        
                        # Clear the status indicators
                        status_text.empty()
                        
                        st.markdown("<div class='success-message'>Email sent successfully!</div>", unsafe_allow_html=True)
                        
                        # Save to history
                        save_to_history(sender_email, recipients_input, subject, "SUCCESS")
                        
                    except smtplib.SMTPAuthenticationError:
                        st.markdown("<div class='error-message'>Authentication failed. Please check your email and password.</div>", unsafe_allow_html=True)
                        with st.expander("More Information"):
                            st.write("1. Make sure you're using an App Password (not your regular password)")
                            st.write("2. Verify the App Password is correct and hasn't expired")
                            st.write("3. Confirm that your Google account settings allow this connection")
                            st.write("4. You can generate a new App Password at: https://myaccount.google.com/apppasswords")
                        
                        # Save error to history
                        save_to_history(sender_email, recipients_input, subject, "FAILED", "Authentication error")
                        
                    except Exception as e:
                        st.markdown(f"<div class='error-message'>An error occurred: {e}</div>", unsafe_allow_html=True)
                        
                        # Save error to history
                        save_to_history(sender_email, recipients_input, subject, "FAILED", str(e))

# Email History Page
elif page == "Email History":
    st.header("Email History")
    
    history = load_history()
    
    if not history:
        st.info("No email history found. Start sending emails to build your history.")
    else:
        # Convert to DataFrame for display
        df = pd.DataFrame(history)
        
        # Add status badges
        def format_status(status):
            if status == "SUCCESS":
                return f"<span class='status-badge status-success'>Success</span>"
            elif status == "FAILED":
                return f"<span class='status-badge status-failed'>Failed</span>"
            elif status == "TEST":
                return f"<span class='status-badge' style='background-color:#e2e3e5;color:#383d41'>Test</span>"
            return status
        
        df['formatted_status'] = df['status'].apply(format_status)
        
        # Display filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=["SUCCESS", "FAILED", "TEST"],
                default=["SUCCESS", "FAILED", "TEST"]
            )
        
        with col2:
            if 'timestamp' in df.columns:
                dates = df['timestamp'].str.split(' ').str[0].unique().tolist()
                date_filter = st.multiselect(
                    "Filter by Date",
                    options=dates,
                    default=dates
                )
        
        # Apply filters
        filtered_df = df[df['status'].isin(status_filter)]
        if 'timestamp' in filtered_df.columns and date_filter:
            filtered_df = filtered_df[filtered_df['timestamp'].str.split(' ').str[0].isin(date_filter)]
        
        # Display the data
        if not filtered_df.empty:
            st.write(f"Showing {len(filtered_df)} records")
            
            # Custom display of data
            for i, row in filtered_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 3, 1])
                    with col1:
                        st.write(f"**Date:** {row['timestamp']}")
                        st.write(f"**From:** {row['sender']}")
                    with col2:
                        st.write(f"**Subject:** {row['subject']}")
                        st.write(f"**To:** {row['recipients']}")
                    with col3:
                        st.markdown(f"**Status:** {row['formatted_status']}", unsafe_allow_html=True)
                        if row['status'] == "FAILED" and row['error']:
                            with st.expander("Error Details"):
                                st.error(row['error'])
                    st.markdown("---")
            
            # Option to clear history
            if st.button("Clear History"):
                try:
                    os.remove("email_history.json")
                    st.success("History cleared successfully!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Failed to clear history: {e}")
        else:
            st.info("No records match the selected filters.")

# Settings Page
elif page == "Settings":
    st.header("App Settings")
    
    tabs = st.tabs(["Account Settings", "App Password Help", "About"])
    
    with tabs[0]:
        st.subheader("Email Account Settings")
        
        with st.form(key="settings_form"):
            new_sender = st.text_input("Sender Email", value=default_sender)
            new_receiver = st.text_input("Default Receiver Email", value=default_receiver)
            new_password = st.text_input("App Password", value=default_password, type="password")
            
            save_button = st.form_submit_button(label="Save Settings")
        
        if save_button:
            try:
                with open(".env", "w") as f:
                    f.write(f"SENDER_EMAIL={new_sender}\n")
                    f.write(f"RECEIVER_EMAIL={new_receiver}\n")
                    f.write(f"EMAIL_PASSWORD={new_password}\n")
                st.markdown("<div class='success-message'>Settings saved successfully!</div>", unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"<div class='error-message'>Failed to save settings: {e}</div>", unsafe_allow_html=True)
        
        # Show settings explanation for Streamlit Cloud
        st.subheader("Deploying to Streamlit Cloud")
        st.write("""
        When deploying to Streamlit Cloud:
        
        1. Don't upload your .env file (add it to .gitignore)
        2. Instead, add your credentials as Secrets in the Streamlit Cloud dashboard:
            - Go to your app settings in Streamlit Cloud
            - Find the "Secrets" section
            - Add your credentials in this format:
        """)
        
        st.code("""
        [secrets]
        SENDER_EMAIL = "your-email@gmail.com"
        RECEIVER_EMAIL = "recipient@example.com"
        EMAIL_PASSWORD = "your-app-password"
        """)
    
    with tabs[1]:
        st.subheader("How to Get a Gmail App Password")
        
        st.write("""
        ### Steps to create an App Password:
        
        1. Go to your [Google Account Security Settings](https://myaccount.google.com/security)
        2. Make sure 2-Step Verification is enabled
        3. Scroll down and select "App passwords"
        4. Click "Select app" and choose "Mail"
        5. Click "Select device" and choose "Other"
        6. Enter a name (e.g., "Python Email App")
        7. Click "Generate"
        8. Copy the 16-character password that appears
        9. Paste this password in the app settings (not your regular Gmail password)
        
        **Note:** You will only see the App password once, so make sure to save it securely.
        """)
        
        st.image("https://miro.medium.com/max/1400/1*mRFMPQTduQGDTxLADtIPAg.png", 
                caption="Example of Gmail App Password page")
    
    with tabs[2]:
        st.subheader("About This App")
        
        st.write("""
        This Advanced Email Sender app was created with Streamlit and Python.
        
        ### Features:
        - Send emails to multiple recipients
        - Add CC recipients
        - HTML or plain text formatting
        - File attachments
        - Email priority settings
        - Email history tracking
        - Test mode for validation without sending
        
        ### Technology Stack:
        - Python
        - Streamlit
        - smtplib for email sending
        - pandas for data handling
        - dotenv for environment variable management
        """)
        
        st.write("Version 1.0.0")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>Created with ❤️ using Streamlit</p>", unsafe_allow_html=True) 

#abhisek