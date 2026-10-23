#!/usr/bin/env python3
"""
Interactive 1-Click Gmail API OAuth Authenticator & Dispatcher.
Opens Google authorization in your browser and saves persistent refresh token.
"""

import os
import sys
import time
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import InstalledAppFlow

CREDS_FILE = os.path.abspath("credentials/gmail_credentials.json")
TOKEN_FILE = os.path.abspath("credentials/gmail_send_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
PORT = 8080
REDIRECT_URI = f"http://localhost:{PORT}/"

auth_code = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = parse_qs(urlparse(self.path).query)
        if "code" in query:
            auth_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            success_html = """
            <html>
            <body style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0F172A; color: #F8FAFC; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0;">
                <div style="background: #1E293B; padding: 40px; border-radius: 12px; text-align: center; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                    <div style="font-size: 48px; margin-bottom: 16px;">✅</div>
                    <h2 style="margin: 0 0 12px 0; color: #10B981;">Gmail API Authorization Successful!</h2>
                    <p style="color: #94A3B8; margin: 0;">You can now close this tab. The executive briefing email is being delivered to your inbox.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed or missing code.")

    def log_message(self, format, *args):
        pass # Silence server logs

def authenticate_and_send():
    global auth_code

    if not os.path.exists(CREDS_FILE):
        print(f"❌ Credentials not found at {CREDS_FILE}")
        return False

    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES, redirect_uri=REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

    print("=" * 80)
    print("GMAIL API 1-CLICK AUTHENTICATION")
    print("=" * 80)
    print(f"Opening browser for Google authorization...")
    print(f"If browser does not open automatically, visit:")
    print(f"\n{auth_url}\n")
    print("=" * 80)

    # Launch browser explicitly
    subprocess.run(["open", auth_url])

    # Run local server to catch callback
    server = HTTPServer(("localhost", PORT), OAuthCallbackHandler)
    server.timeout = 120 # Wait up to 2 minutes

    print(f"Waiting for authorization callback on port {PORT}...")
    while auth_code is None:
        server.handle_request()

    server.server_close()

    if not auth_code:
        print("❌ Authorization was not completed.")
        return False

    print("✅ Authorization code received! Exchanging for persistent refresh token...")
    flow.fetch_token(code=auth_code)
    creds = flow.credentials

    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    print(f"✅ Saved persistent token to {TOKEN_FILE}")

    # Immediately send the email via Gmail API!
    print("\nSending live email via official Gmail API...")
    import send_via_gmail_api
    send_via_gmail_api.send_executive_email_via_api()
    return True

if __name__ == "__main__":
    authenticate_and_send()
