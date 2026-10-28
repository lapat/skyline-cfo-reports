#!/usr/bin/env python3
"""
prepare_lake_strategy_email.py -- Exact Jay strategy + 4% bid and repeat redeemer upgrade.
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
from googleapiclient.discovery import build

TOKEN_FILE = os.path.abspath("credentials/gmail_send_token.json")
EXCEL_FILE = os.path.abspath("data/Lake_County_2026_Presale_Targets.xlsx")
PREVIEW_HTML = os.path.abspath("preview_lake_strategy_email.html")

def generate_email_html():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; font-size: 14px; line-height: 1.6; }
  .container { max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1; padding: 24px 30px; }
  p { margin: 0 0 14px 0; }
  ol { margin: 0 0 16px 0; padding-left: 20px; }
  li { margin-bottom: 10px; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 12.5px; }
  th { background: #1e3a8a; color: #ffffff; text-align: left; padding: 8px 10px; font-weight: 600; }
  td { padding: 8px 10px; border-bottom: 1px solid #e2e8f0; }
  tr:nth-child(even) { background-color: #f8fafc; }
  .badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 10.5px; font-weight: 700; }
  .badge-green { background: #dcfce7; color: #166534; }
  .badge-purple { background: #f3e8ff; color: #6b21a8; }
  .badge-blue { background: #dbeafe; color: #1e40af; }
  .right { text-align: right; }
</style>
</head>
<body>
<div class="container">
  <p>
    Following Jay’s strategy to target high-dollar amounts and 1/2 installments at the Lake County sale, we extracted every parcel on the list where Cycle 1 was already paid and added two specific tactical upgrades:
  </p>

  <ol>
    <li>
      <b>Bid 4% on parcels &ge; $25,000 (instead of 5%):</b> At 5%, we get forced into a random 50/50 coin-flip against Bridge in the tie-breaker. At 4%, we guarantee we win the ticket over Bridge 100% of the time. The 1% upfront discount is trivial compared to securing the asset and carrying the <b>12% statutory annual subtax</b> (+500 bps over Byline Bank borrowing cost, generating +$240k/yr on our $2.0M target).
    </li>
    <li>
      <b>Favor Proven Repeat Redeemers:</b> Instead of guessing whether an owner or bank will pay, we cross-referenced Lake County’s historical tax sale ledger to flag the <b>67 high-dollar parcels that have been sold multiple times previously and 100% fully redeemed every time</b>.
    </li>
  </ol>

  <p>
    <b>The Numbers:</b> We found <b>268 parcels over $10k totaling $5,119,825 in volume</b> that are 2nd installment only (&gt;95% redemption safety), giving us 2.5x the volume needed to hit our $2.0M allocation.
  </p>

  <p>Sample of top targets from the attached file:</p>

  <table>
    <thead>
      <tr>
        <th>PIN</th>
        <th>Taxpayer / Property</th>
        <th>City</th>
        <th class="right">Tax Due</th>
        <th class="right">Bldg Ratio</th>
        <th>Recommended Bid</th>
        <th>County History</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>07-25-308-009</code></td>
        <td><b>Fountain Square Hospitality</b></td>
        <td>Waukegan</td>
        <td class="right"><b>$169,504</b></td>
        <td class="right">3.2x</td>
        <td><span class="badge badge-green">4.0%</span></td>
        <td><span class="badge badge-purple">4x Redeemed</span></td>
      </tr>
      <tr>
        <td><code>04-18-400-041</code></td>
        <td><b>Enova Investment LLC</b></td>
        <td>Zion</td>
        <td class="right"><b>$141,304</b></td>
        <td class="right">5.9x</td>
        <td><span class="badge badge-green">4.0%</span></td>
        <td><span class="badge badge-purple">4x Redeemed</span></td>
      </tr>
      <tr>
        <td><code>08-21-423-005</code></td>
        <td><b>Karcher Artspace Lofts</b></td>
        <td>Waukegan</td>
        <td class="right"><b>$70,039</b></td>
        <td class="right">55.8x</td>
        <td><span class="badge badge-green">4.0%</span></td>
        <td><span class="badge badge-purple">2x Redeemed</span></td>
      </tr>
      <tr>
        <td><code>16-23-415-015</code></td>
        <td><b>Mark &amp; Julie Filler</b></td>
        <td>Highland Park</td>
        <td class="right"><b>$51,687</b></td>
        <td class="right">5.2x</td>
        <td><span class="badge badge-green">4.0%</span></td>
        <td><span class="badge badge-blue">1x Redeemed</span></td>
      </tr>
      <tr>
        <td><code>15-34-309-002</code></td>
        <td><b>100 Lexington Properties</b></td>
        <td>Buffalo Grove</td>
        <td class="right"><b>$36,361</b></td>
        <td class="right">3.5x</td>
        <td><span class="badge badge-green">4.0%</span></td>
        <td><span class="badge badge-purple">2x Redeemed</span></td>
      </tr>
    </tbody>
  </table>

  <p>
    Attached is the spreadsheet (<code>Lake_County_2026_Presale_Targets.xlsx</code>) with all 268 targets and recommended bids (4% on &ge; $25k, 5% on $10k–$25k) pre-scored and ready to upload into Stan's bidding software.
  </p>

  <p>Let me know what you think.</p>

  <p>
    Best,<br>
    <b>Louis</b>
  </p>
</div>
</body>
</html>"""
    return html

def preview_email():
    html = generate_email_html()
    with open(PREVIEW_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Generated local email HTML preview: {PREVIEW_HTML}")
    return html

def send_email(recipients, subject="Lake County Tax Sale (Nov 13) — $5.12M 1/2 Installment Target List & Bid Strategy"):
    if not os.path.exists(TOKEN_FILE):
        print(f"❌ Error: Gmail token not found at {TOKEN_FILE}")
        return False

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/gmail.send"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("gmail", "v1", credentials=creds)

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = "louislapat@gmail.com"
    msg["To"] = ", ".join(recipients) if isinstance(recipients, list) else recipients

    html_content = generate_email_html()
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    # Attach Excel
    if os.path.exists(EXCEL_FILE):
        with open(EXCEL_FILE, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(EXCEL_FILE))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(EXCEL_FILE)}"'
            msg.attach(part)

    raw_bytes = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    result = service.users().messages().send(userId="me", body={"raw": raw_bytes}).execute()
    print(f"✅ Dispatched email via Gmail API! Message ID: {result.get('id')}")
    return True

if __name__ == "__main__":
    preview_email()
