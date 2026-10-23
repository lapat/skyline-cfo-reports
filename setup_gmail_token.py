#!/usr/bin/env python3
"""
Standard Google OAuth Flow for Gmail API Send Permission.
Uses dynamic port=0 local server (same method as accounts payable/webapp/reauth_gmail.py).
"""

import os
import sys
import base64
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CREDS_FILE = os.path.abspath("credentials/gmail_credentials.json")
TOKEN_FILE = os.path.abspath("credentials/gmail_send_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
RECIPIENT_EMAIL = "louislapat@gmail.com"

def main():
    print("=" * 75)
    print("GMAIL API SETUP — JENNINGS REALTY")
    print("=" * 75)

    if not os.path.exists(CREDS_FILE):
        print(f"Error: {CREDS_FILE} not found!", file=sys.stderr)
        sys.exit(1)

    print("Initiating Google OAuth flow with port=0...")
    print("A browser window will open. Click Allow (or Advanced -> Go to ... unsafe).")
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True)

    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print(f"\n✅ Persistent OAuth token successfully saved to: {TOKEN_FILE}")
    print(f"Token Expiry: {creds.expiry}")

    # Build Gmail service and send the email right now!
    print(f"\nSending live executive briefing to {RECIPIENT_EMAIL} via Gmail API...")
    import send_executive_alert
    stats = send_executive_alert.get_executive_summary_stats()
    subject, text, html = send_executive_alert.generate_email_content(stats)

    service = build("gmail", "v1", credentials=creds)

    message = MIMEMultipart("alternative")
    message["to"] = RECIPIENT_EMAIL
    message["subject"] = subject
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    sent = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()

    print("=" * 75)
    print("🎉 EMAIL DELIVERED TO YOUR GMAIL INBOX VIA GMAIL API!")
    print(f"  Recipient: {RECIPIENT_EMAIL}")
    print(f"  Subject:   {subject}")
    print(f"  Gmail ID:  {sent.get('id')}")
    print("=" * 75)

if __name__ == "__main__":
    main()
