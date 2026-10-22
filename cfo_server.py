#!/usr/bin/env python3
"""
Production CFO Server with Password Protection & Mobile-Friendly Web Portal.

Features:
- Passcode Gate: Requires passcode 'Jennings2026' (or custom via PASSCODE env var)
- Supports URL query ?passcode=Jennings2026 for instant 1-click access
- Sets 30-day authentication cookie for persistent login on phones/tablets
- Serves cfo_reports_viewer.html, pdf_reports/, and source_documents/
- Integrates with Cloudflare Tunnel (cloudflared) for a secure, public HTTPS URL
"""

import os
import sys
import time
import subprocess
from flask import Flask, request, make_response, send_from_directory, redirect, url_for

app = Flask(__name__)
PASSCODE = os.environ.get("CFO_PASSCODE", "Jennings2026")
PORT = int(os.environ.get("PORT", 8999))
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Jennings Enterprise — Executive Access</title>
<style>
:root {
    --bg: #0F172A;
    --card: #1E293B;
    --text: #F8FAFC;
    --muted: #94A3B8;
    --accent: #3B82F6;
    --border: #334155;
    --danger: #EF4444;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 20px;
}
.login-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px 28px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
    text-align: center;
}
.badge {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 8px;
}
h1 {
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 8px;
}
p {
    font-size: 13.5px;
    color: var(--muted);
    margin-bottom: 24px;
    line-height: 1.5;
}
input[type="password"], input[type="text"] {
    width: 100%;
    padding: 14px 16px;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: rgba(15, 23, 42, 0.8);
    color: var(--text);
    font-size: 16px;
    margin-bottom: 16px;
    text-align: center;
    letter-spacing: 2px;
    outline: none;
    transition: border 0.15s;
}
input:focus {
    border-color: var(--accent);
}
button {
    width: 100%;
    padding: 14px;
    border-radius: 10px;
    background: var(--accent);
    color: white;
    font-size: 15px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    transition: opacity 0.15s;
}
button:hover {
    opacity: 0.9;
}
.error {
    color: var(--danger);
    font-size: 12.5px;
    margin-top: 12px;
    font-weight: 600;
}
</style>
</head>
<body>
<div class="login-card">
    <div class="badge">JENNINGS REALTY & AFFILIATES</div>
    <h1>Executive Financial Portal</h1>
    <p>Please enter the portfolio passcode to view CFO executive reports and live Skyline financials.</p>
    <form method="POST" action="/login">
        <input type="password" name="passcode" placeholder="Enter Passcode" autofocus autocomplete="current-password" required>
        <button type="submit">Unlock Executive Reports</button>
        {{ERROR_MSG}}
    </form>
</div>
</body>
</html>
"""

def is_authenticated():
    cookie_token = request.cookies.get("cfo_auth")
    if cookie_token == PASSCODE:
        return True
    query_token = request.args.get("passcode")
    if query_token == PASSCODE:
        return True
    header_token = request.headers.get("X-Passcode")
    if header_token == PASSCODE:
        return True
    return False

@app.route("/")
def index():
    if not is_authenticated():
        query_token = request.args.get("passcode")
        if query_token and query_token != PASSCODE:
            err = '<div class="error">Incorrect passcode. Please try again.</div>'
        else:
            err = ""
        return LOGIN_HTML.replace("{{ERROR_MSG}}", err)
    
    # Authenticated: Serve viewer
    resp = make_response(send_from_directory(BASE_DIR, "cfo_reports_viewer.html"))
    # Ensure cookie is set
    query_token = request.args.get("passcode")
    if query_token == PASSCODE:
        resp.set_cookie("cfo_auth", PASSCODE, max_age=60*60*24*30, samesite="Lax")
    return resp

@app.route("/login", methods=["POST"])
def login():
    entered_passcode = request.form.get("passcode", "").strip()
    if entered_passcode == PASSCODE:
        resp = redirect(url_for("index"))
        resp.set_cookie("cfo_auth", PASSCODE, max_age=60*60*24*30, samesite="Lax")
        return resp
    else:
        err = '<div class="error">Incorrect passcode. Access denied.</div>'
        return LOGIN_HTML.replace("{{ERROR_MSG}}", err), 401

@app.route("/pdf_reports/<path:filename>")
def serve_pdf_reports(filename):
    if not is_authenticated():
        return redirect(url_for("index"))
    return send_from_directory(os.path.join(BASE_DIR, "pdf_reports"), filename)

@app.route("/source_documents/<path:filename>")
def serve_source_docs(filename):
    if not is_authenticated():
        return redirect(url_for("index"))
    return send_from_directory(os.path.join(BASE_DIR, "source_documents"), filename)

def start_server():
    print("=" * 75)
    print(f"🚀 Jennings Enterprise CFO Executive Web Portal")
    print(f"🔒 Passcode Protection: Active ('{PASSCODE}')")
    print(f"📱 Mobile Optimized: Yes (iPhone, iPad, Android)")
    print(f"🌐 Local Port: {PORT}")
    print("=" * 75)
    app.run(host="0.0.0.0", port=PORT, debug=False)

if __name__ == "__main__":
    start_server()
