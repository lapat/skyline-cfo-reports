#!/usr/bin/env python3
"""
Official Gmail API Email Dispatcher for Jennings Realty.

Uses OAuth 2.0 with scope: https://www.googleapis.com/auth/gmail.send
Stores persistent refresh token in credentials/gmail_send_token.json
Supports multipart/mixed with PDF attachments.
"""

import os
import sys
import base64
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDS_FILE = os.path.abspath("credentials/gmail_credentials.json")
TOKEN_FILE = os.path.abspath("credentials/gmail_send_token.json")
DEFAULT_RECIPIENT = "louislapat@gmail.com"

def get_gmail_service():
    """Authenticates and returns the Google Gmail API service instance."""
    creds = None
    import pickle

    # 1. Try active token.pickle from jim report viewer
    jim_pickle = "/Users/louislapat/vibe/jim report viewer/token.pickle"
    if os.path.exists(jim_pickle):
        try:
            with open(jim_pickle, "rb") as f:
                creds = pickle.load(f)
            if creds and creds.valid:
                return build("gmail", "v1", credentials=creds)
            elif creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(jim_pickle, "wb") as f:
                    pickle.dump(creds, f)
                return build("gmail", "v1", credentials=creds)
        except Exception:
            creds = None

    # 2. Try credentials/gmail_send_token.json
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            if creds and creds.valid:
                return build("gmail", "v1", credentials=creds)
            elif creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
                return build("gmail", "v1", credentials=creds)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if not os.path.exists(CREDS_FILE):
            raise FileNotFoundError(f"OAuth credentials not found at {CREDS_FILE}")
            
            print(f"[{time.strftime('%H:%M:%S')}] 🌐 Opening browser for 1-time Google OAuth authorization...")
            print(f"👉 Please select your account ({DEFAULT_RECIPIENT}) and grant Gmail send permission.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print(f"[{time.strftime('%H:%M:%S')}] ✅ Persistent Gmail token saved to {TOKEN_FILE}")

    return build("gmail", "v1", credentials=creds)

def send_executive_email_via_api(recipient=None, attach_pdf=True):
    """Builds and sends the executive briefing email via the official Gmail API."""
    import send_executive_alert
    target_email = recipient or DEFAULT_RECIPIENT
    recipient_name = "Jay" if any(k in target_email.lower() for k in ["jay", "jlapat"]) else "Louis"

    stats = send_executive_alert.get_executive_summary_stats()
    subject, text, html = send_executive_alert.generate_email_content(stats, recipient_name=recipient_name)

    service = get_gmail_service()

    # Create root message
    if attach_pdf:
        msg_root = MIMEMultipart("mixed")
        msg_root["to"] = target_email
        msg_root["subject"] = subject

        # Create alternative body part (text + html)
        msg_alt = MIMEMultipart("alternative")
        msg_alt.attach(MIMEText(text, "plain"))
        msg_alt.attach(MIMEText(html, "html"))
        msg_root.attach(msg_alt)

        # Attach PDF if available
        pdf_path = os.path.abspath("pdf_reports/00_DAILY_EXECUTIVE_CASH_STATEMENT.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_part = MIMEApplication(f.read(), _subtype="pdf")
                pdf_part.add_header("Content-Disposition", "attachment", filename=os.path.basename(pdf_path))
                msg_root.attach(pdf_part)
                print(f"[{time.strftime('%H:%M:%S')}] 📎 Attached {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path):,} bytes)")
        message = msg_root
    else:
        message = MIMEMultipart("alternative")
        message["to"] = target_email
        message["subject"] = subject
        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(html, "html"))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    body = {"raw": raw_message}

    print(f"[{time.strftime('%H:%M:%S')}] 🚀 Sending executive briefing to {target_email} via Gmail API...")
    sent = service.users().messages().send(userId="me", body=body).execute()
    msg_id = sent.get("id")

    print("=" * 80)
    print("✅ EMAIL SUCCESSFULLY DELIVERED VIA GMAIL API!")
    print(f"  Recipient:   {target_email}")
    print(f"  Subject:     {subject}")
    print(f"  Gmail ID:    {msg_id}")
    print(f"  Timestamp:   {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    send_executive_email_via_api(recipient=target)
