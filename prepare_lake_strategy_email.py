#!/usr/bin/env python3
"""
prepare_lake_strategy_email.py -- Full historical 2025 analysis + Jay's Lake specifications.
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
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; font-size: 13.5px; line-height: 1.55; }
  .container { max-width: 740px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1; padding: 24px 30px; }
  p { margin: 0 0 12px 0; }
  ul { margin: 0 0 14px 0; padding-left: 20px; }
  li { margin-bottom: 6px; }
  table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 12px; }
  th { background: #1e3a8a; color: #ffffff; text-align: left; padding: 7px 10px; font-weight: 600; }
  td { padding: 7px 10px; border-bottom: 1px solid #e2e8f0; }
  tr:nth-child(even) { background-color: #f8fafc; }
  .badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; }
  .badge-green { background: #dcfce7; color: #166534; }
  .badge-blue { background: #dbeafe; color: #1e40af; }
  .badge-purple { background: #f3e8ff; color: #6b21a8; }
  .right { text-align: right; }
  h4 { margin: 18px 0 6px 0; color: #1e3a8a; font-size: 13.5px; text-transform: uppercase; letter-spacing: 0.3px; }
</style>
</head>
<body>
<div class="container">
  <p>Jay &amp; Stan,</p>

  <p>Here is the full analysis of what happened last year across all counties, our remaining 2026 sales schedule, and the revised Lake County numbers per Jay's specifications:</p>

  <h4>1. REMAINING SALES SCHEDULE &amp; PAST BUYS (LAST YEAR VS. THIS YEAR)</h4>
  <table>
    <thead>
      <tr>
        <th>County</th>
        <th>2026 Sale Date</th>
        <th class="right">Last Year Won (2025)</th>
        <th class="right">This Year Bid / Upload</th>
        <th class="right">This Year Won / Target</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Kendall</b></td>
        <td>Mon, Oct 26</td>
        <td class="right">78 certs ($220,883)</td>
        <td class="right">$300k target</td>
        <td class="right">0 certs ($0)</td>
      </tr>
      <tr>
        <td><b>Kane</b></td>
        <td>Mon, Oct 26</td>
        <td class="right">112 certs ($852,779)</td>
        <td class="right">779 certs ($5.90M)</td>
        <td class="right"><span class="badge badge-green">8 certs ($86,467)</span></td>
      </tr>
      <tr style="background:#eff6ff;">
        <td><b>Lake</b></td>
        <td><b>Fri, Nov 13</b></td>
        <td class="right"><b>853 certs ($6,131,471)</b><br><span style="font-size:10px; color:#64748b;">(Bid 2,703 certs / $19.8M)</span></td>
        <td class="right">5,011 filtered pool ($37.4M)</td>
        <td class="right"><b>Target: $2,000,000</b></td>
      </tr>
      <tr>
        <td><b>DuPage</b></td>
        <td>Thu, Nov 19</td>
        <td class="right">32 certs ($254,027)</td>
        <td class="right">Awaiting final list</td>
        <td class="right"><b>Target: $1,500,000</b></td>
      </tr>
      <tr>
        <td><b>McHenry</b></td>
        <td>Mon, Nov 23</td>
        <td class="right">180 certs ($1,452,829)</td>
        <td class="right">Awaiting final list</td>
        <td class="right"><b>Target: $1,000,000</b></td>
      </tr>
      <tr>
        <td><b>Will</b></td>
        <td>Tue, Dec 01</td>
        <td class="right">240 certs ($1,457,091)</td>
        <td class="right">Awaiting final list</td>
        <td class="right"><b>Target: $2,000,000</b></td>
      </tr>
      <tr style="font-weight:700; background:#f1f5f9;">
        <td colspan="4">TOTAL REMAINING TARGET ALLOCATION (To hit $5.0M goal):</td>
        <td class="right" style="color:#1e3a8a; font-size:13px;">$6,500,000</td>
      </tr>
    </tbody>
  </table>

  <h4>2. WHAT WE BID VS. WHAT WE WON LAST YEAR (STAN'S PRODUCTION ROLLUP)</h4>
  <p>Per Stan's revised production models, Jennings uploaded <b>5,656 certificates ($42.13M)</b> across the 4 collar counties after removing full installments under $3,000, ultimately winning <b>$13.54M across 2,159 certificates</b> (a 32% win rate):</p>

  <table>
    <thead>
      <tr>
        <th>County</th>
        <th class="right">Stan's Upload Certs</th>
        <th class="right">Stan's Upload $</th>
        <th class="right">Certs Won</th>
        <th class="right">Capital Won</th>
        <th class="right">Avg Winning Bid</th>
      </tr>
    </thead>
    <tbody>
      <tr style="background:#f0fdf4; font-weight:700;">
        <td><b>Lake</b></td>
        <td class="right">1,640</td>
        <td class="right">$13,850,986</td>
        <td class="right">853</td>
        <td class="right">$6,131,471</td>
        <td class="right">1.84%</td>
      </tr>
      <tr>
        <td><b>Will</b></td>
        <td class="right">1,492</td>
        <td class="right">$10,487,163</td>
        <td class="right">240</td>
        <td class="right">$1,457,091</td>
        <td class="right">1.52%</td>
      </tr>
      <tr>
        <td><b>McHenry</b></td>
        <td class="right">1,359</td>
        <td class="right">$8,468,045</td>
        <td class="right">180</td>
        <td class="right">$1,452,829</td>
        <td class="right">1.99%</td>
      </tr>
      <tr>
        <td><b>DuPage</b></td>
        <td class="right">1,165</td>
        <td class="right">$9,326,953</td>
        <td class="right">774</td>
        <td class="right">$3,648,154</td>
        <td class="right">2.18%</td>
      </tr>
      <tr style="font-weight:800; background:#f8fafc;">
        <td><b>4-COUNTY TOTAL</b></td>
        <td class="right"><b>5,656</b></td>
        <td class="right"><b>$42,133,147</b></td>
        <td class="right"><b>2,047</b></td>
        <td class="right"><b>$12,689,545</b></td>
        <td class="right"><b>1.98%</b></td>
      </tr>
    </tbody>
  </table>
        <td class="right">3.05%</td>
        <td>3.0% (77% of certs)</td>
      </tr>
      <tr>
        <td><b>DuPage</b></td>
        <td class="right">32</td>
        <td class="right">$254,027</td>
        <td class="right">2.00%</td>
        <td>2.0% (100% of certs)</td>
      </tr>
      <tr>
        <td><b>Kendall</b></td>
        <td class="right">78</td>
        <td class="right">$220,883</td>
        <td class="right">3.28%</td>
        <td>3.0% (96% of certs)</td>
      </tr>
    </tbody>
  </table>

  <p><b>Who the 'Big Guys' Were in Lake County Last Year ($20.4M Total Auction):</b></p>
  <ul>
    <li><b>#1 Central Buyer Corp (Jennings):</b> $6.13M won (30.1% share of the county) at <b>1.68% average</b>.</li>
    <li><b>#2 Private Equity Group LLC (Bridge):</b> $2.99M won (14.7% share) at <b>2.04% average</b>.</li>
    <li><b>#3 American Tax Lien LLC:</b> $2.84M won (13.9% share) at <b>2.26% average</b>.</li>
    <li><b>#4 Ari Bass (Personal / Raven):</b> $1.30M won (6.4% share) at <b>2.85% average</b>.</li>
  </ul>

  <h4>3. LAKE COUNTY 2026 REVISED BREAKDOWN (JAY'S SPECIFICATIONS)</h4>
  <p>Applying Jay's filter to the 6,078 published parcels (removing full installments under $3,000, keeping all 1/2 installments and certs &gt;=$3,000):</p>

  <table>
    <thead>
      <tr>
        <th>Segment</th>
        <th class="right">Cert Count</th>
        <th class="right">Total Dollars</th>
        <th class="right">Avg Size</th>
        <th>Workload &amp; Strategy Impact</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Original Published List</td>
        <td class="right">6,078</td>
        <td class="right">$38,560,308</td>
        <td class="right">$6,344</td>
        <td>Full raw list from County Collector</td>
      </tr>
      <tr style="color:#991b1b; background:#fef2f2;">
        <td><b>REMOVED: Full Inst &lt; $3,000</b></td>
        <td class="right"><b>-1,067</b></td>
        <td class="right"><b>-$1,159,368</b></td>
        <td class="right">$1,086</td>
        <td><b>ELIMINATES 1,067 FILING HEADACHES;</b> loses only 3.0% of $!</td>
      </tr>
      <tr style="background:#f0fdf4; font-weight:700;">
        <td><b>REVISED FILTERED POOL</b></td>
        <td class="right"><b>5,011</b></td>
        <td class="right"><b>$37,400,940</b></td>
        <td class="right"><b>$7,464</b></td>
        <td>Clean, high-margin pool to deploy $2.0M target</td>
      </tr>
      <tr>
        <td><b>  • Commercial &amp; Industrial</b></td>
        <td class="right"><b>487</b></td>
        <td class="right"><b>$8,152,465</b></td>
        <td class="right"><b>$16,740</b></td>
        <td>High ticket size ($16.7k avg) &amp; institutional backing</td>
      </tr>
      <tr>
        <td><b>  • Residential &amp; Other</b></td>
        <td class="right">4,524</td>
        <td class="right">$29,248,475</td>
        <td class="right">$6,465</td>
        <td>Focus on 1/2 installments with Bldg &gt; 2x Land</td>
      </tr>
    </tbody>
  </table>

  <h4>4. WORKLOAD &amp; PROFIT STRATEGY</h4>
  <ul>
    <li>
      <b>Minimizing Filing Workload:</b> Cutting full installments under $3k removes <b>1,067 low-dollar certificates</b> from ever needing court filings or take notices. Furthermore, within our 5,011 revised pool, <b>2,787 parcels ($12.35M) are 1/2 installments</b> where Cycle 1 was already paid—meaning over 95% redeem before we ever have to touch a legal petition.
    </li>
    <li>
      <b>Maximizing Profit:</b> Focusing our $2.0M target on the <b>487 Commercial items ($8.15M)</b> and high-dollar 1/2 installments concentrates our capital into large balances, where the <b>12% statutory annual subtax carrying interest (+500 to +600 bps spread over Byline Bank borrowing cost)</b> generates our actual profit.
    </li>
  </ul>

  <p>
    Attached is the revised workbook (<code>Lake_County_2026_Presale_Targets.xlsx</code>) with dedicated tabs for:
    <br>1. <b>2026 Sales Schedule &amp; Jay Filter</b>
    <br>2. <b>2025 County Bids &amp; Competitors</b> (Full analysis of last year)
    <br>3. <b>Commercial &amp; Industrial (487 certs)</b>
    <br>4. <b>Residential &amp; Other (4,524 certs)</b>
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

def send_email(recipients, subject="Remaining 2026 Tax Sales Schedule & Lake County Revised Breakdown"):
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
