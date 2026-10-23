#!/usr/bin/env python3
"""
Official Gmail API Email Dispatcher for Jennings Realty.

Uses OAuth 2.0 with scope: https://www.googleapis.com/auth/gmail.send
Stores persistent refresh token in credentials/gmail_send_token.json
"""

import os
import sys
import base64
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDS_FILE = os.path.abspath("credentials/gmail_credentials.json")
TOKEN_FILE = os.path.abspath("credentials/gmail_send_token.json")
RECIPIENT_EMAIL = "louislapat@gmail.com"

def get_gmail_service():
    """Authenticates and returns the Google Gmail API service instance."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"[{time.strftime('%H:%M:%S')}] 🔄 Refreshing expired Gmail API OAuth token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                raise FileNotFoundError(f"OAuth credentials not found at {CREDS_FILE}")
            
            print(f"[{time.strftime('%H:%M:%S')}] 🌐 Opening browser for 1-time Google OAuth authorization...")
            print(f"👉 Please select your account ({RECIPIENT_EMAIL}) and grant Gmail send permission.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print(f"[{time.strftime('%H:%M:%S')}] ✅ Persistent Gmail token saved to {TOKEN_FILE}")

    return build("gmail", "v1", credentials=creds)

def send_executive_email_via_api():
    """Builds and sends the executive briefing email via the official Gmail API."""
    import send_executive_alert
    stats = send_executive_alert.get_executive_summary_stats()
    subject, text, html = send_executive_alert.generate_email_content(stats)

    service = get_gmail_service()

    message = MIMEMultipart("alternative")
    message["to"] = RECIPIENT_EMAIL
    message["subject"] = subject
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    body = {"raw": raw_message}

    print(f"[{time.strftime('%H:%M:%S')}] 🚀 Sending executive briefing to {RECIPIENT_EMAIL} via Gmail API...")
    sent = service.users().messages().send(userId="me", body=body).execute()
    msg_id = sent.get("id")

    print("=" * 80)
    print("✅ EMAIL SUCCESSFULLY DELIVERED VIA GMAIL API!")
    print(f"  Recipient:   {RECIPIENT_EMAIL}")
    print(f"  Subject:     {subject}")
    print(f"  Gmail ID:    {msg_id}")
    print(f"  Timestamp:   {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    return True

if __name__ == "__main__":
    send_executive_email_via_api()
