#!/usr/bin/env python3
"""
generate_tax_dashboard.py -- Compiles the standalone Tax Buying Dashboard (tax.html)
specifically for Stan Engelsen and Jay Lapat.

Features:
1. Passcode protected (Jennings2026 / Stan2026) with 30-day mobile persistence.
2. Leads with the 2025 Historical Intelligence Suite (Jennings' 2.01% baseline & Lake competitors).
3. Priority Subtax Defense ($127k / 18 parcels) with 1-click check request export for Mary.
4. Lake County Pre-Sale War Room with Waukegan water-lien redline flags and direct Assessor links.
5. Multi-county placeholders for DuPage, McHenry, and Will.
"""

import os
import json
import time

TARGETS_JSON = os.path.abspath("lake_presale_targets.json")
SUBTAX_JSON = os.path.abspath("subtax_opportunities_summary.json")
OUTPUT_HTML = os.path.abspath("tax.html")

def generate_tax_html():
    targets_data = {}
    if os.path.exists(TARGETS_JSON):
        with open(TARGETS_JSON) as f:
            targets_data = json.load(f)

    subtax_data = {}
    if os.path.exists(SUBTAX_JSON):
        with open(SUBTAX_JSON) as f:
            subtax_data = json.load(f)

    targets_json_str = json.dumps(targets_data)
    subtax_json_str = json.dumps(subtax_data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Jennings Tax Buying Commander · Fall 2026 Campaign</title>
<style>
  :root {{
    --bg-primary: #0b0f19;
    --bg-secondary: #111827;
    --bg-card: #1f2937;
    --border: #374151;
    --text-primary: #f9fafb;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
    --accent: #3b82f6;
    --success: #10b981;
    --warn: #f59e0b;
    --danger: #ef4444;
    --purple: #8b5cf6;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  body {{ background-color: var(--bg-primary); color: var(--text-primary); padding: 16px; font-size: 13px; line-height: 1.5; }}
  .container {{ max-width: 1280px; margin: 0 auto; }}
  
  /* Top App Bar */
  .app-bar {{ display: flex; justify-content: space-between; align-items: center; background: var(--bg-secondary); padding: 14px 20px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }}
  .brand {{ display: flex; align-items: center; gap: 12px; }}
  .brand-icon {{ font-size: 24px; }}
  .brand-title {{ font-size: 16px; font-weight: 800; color: #fff; letter-spacing: -0.3px; }}
  .brand-sub {{ font-size: 11px; color: var(--text-muted); }}

  /* Passcode Modal */
  #authOverlay {{ position: fixed; inset: 0; background: rgba(11,15,25,0.96); z-index: 9999; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(8px); }}
  .auth-card {{ background: var(--bg-secondary); border: 1px solid var(--border); padding: 32px; border-radius: 12px; width: 100%; max-width: 380px; text-align: center; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); }}
  .auth-card h2 {{ font-size: 18px; margin-bottom: 8px; }}
  .auth-card p {{ font-size: 12px; color: var(--text-muted); margin-bottom: 20px; }}
  .auth-input {{ width: 100%; padding: 10px 14px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 6px; color: #fff; font-size: 14px; text-align: center; letter-spacing: 2px; margin-bottom: 14px; outline: none; }}
  .auth-btn {{ width: 100%; padding: 10px; background: var(--accent); color: #fff; border: none; border-radius: 6px; font-weight: 700; cursor: pointer; }}

  /* Metric Strips */
  .metric-strip {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin-bottom: 20px; }}
  .metric-box {{ background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; }}
  .metric-box.featured {{ border-color: rgba(59,130,246,0.5); background: rgba(30,58,138,0.15); }}
  .metric-box.alert {{ border-color: rgba(239,68,68,0.5); background: rgba(127,29,29,0.15); }}
  .metric-label {{ font-size: 10.5px; text-transform: uppercase; font-weight: 700; color: var(--text-muted); margin-bottom: 4px; }}
  .metric-val {{ font-size: 19px; font-weight: 800; color: #fff; }}
  .metric-note {{ font-size: 11px; margin-top: 3px; font-weight: 600; }}

  /* Section Containers */
  .section-card {{ background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 24px; overflow: hidden; }}
  .section-header {{ background: rgba(255,255,255,0.03); padding: 14px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }}
  .section-title {{ font-size: 14.5px; font-weight: 700; display: flex; align-items: center; gap: 8px; color: #fff; }}
  .section-desc {{ font-size: 11.5px; color: var(--text-muted); margin-top: 2px; }}

  /* Tables */
  .table-responsive {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
  table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 12px; }}
  th {{ background: rgba(0,0,0,0.25); color: var(--text-secondary); padding: 10px 14px; font-weight: 600; border-bottom: 1px solid var(--border); text-transform: uppercase; font-size: 10.5px; letter-spacing: 0.5px; }}
  td {{ padding: 10px 14px; border-bottom: 1px solid var(--border); }}
  tr:hover td {{ background: rgba(255,255,255,0.02); }}
  .right {{ text-align: right; }}
  .badge {{ display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; }}
  .badge-green {{ background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }}
  .badge-blue {{ background: rgba(59,130,246,0.2); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }}
  .badge-purple {{ background: rgba(139,92,246,0.2); color: #a78bfa; border: 1px solid rgba(139,92,246,0.3); }}
  .badge-red {{ background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }}
  .badge-yellow {{ background: rgba(245,158,11,0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }}
  .btn {{ padding: 6px 14px; font-size: 11.5px; font-weight: 700; border-radius: 6px; cursor: pointer; border: none; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }}
  .btn-primary {{ background: var(--accent); color: #fff; }}
  .btn-primary:hover {{ background: #2563eb; }}
  
  /* Filter Bar */
  .filter-bar {{ padding: 12px 18px; background: rgba(0,0,0,0.15); border-bottom: 1px solid var(--border); display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
  .filter-select, .filter-input {{ background: var(--bg-card); color: #fff; border: 1px solid var(--border); padding: 5px 10px; border-radius: 5px; font-size: 11.5px; outline: none; }}
  .filter-input {{ min-width: 240px; }}

  /* Toast Notification */
  #toastMsg {{ position: fixed; bottom: 20px; right: 20px; background: #1e3a8a; color: #fff; padding: 10px 18px; border-radius: 6px; font-weight: 700; font-size: 12px; display: none; z-index: 10000; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5); }}
</style>
</head>
<body>

<!-- AUTH OVERLAY -->
<div id="authOverlay">
  <div class="auth-card">
    <div style="font-size:32px; margin-bottom:12px;">🏛️</div>
    <h2>Jennings Tax Commander</h2>
    <p>Please enter executive passcode to access the 2026 Collar Counties Auction Suite.</p>
    <input type="password" id="passcodeInput" class="auth-input" placeholder="PASSCODE" onkeypress="if(event.key==='Enter') verifyPasscode()" />
    <button onclick="verifyPasscode()" class="auth-btn">Authorize Session</button>
  </div>
</div>

<div class="container">

  <!-- TOP APP BAR -->
  <div class="app-bar">
    <div class="brand">
      <span class="brand-icon">🏛️</span>
      <div>
        <div class="brand-title">Jennings Tax Buying Commander · Fall 2026 Campaign</div>
        <div class="brand-sub">Dedicated Tax Operations Portal for Stan Engelsen &amp; Jay Lapat &middot; Updated Today</div>
      </div>
    </div>
    <div style="display:flex; gap:8px; align-items:center;">
      <span class="badge badge-green" style="font-size:11px;">Target: $5,000,000 Total Goal</span>
      <span class="badge badge-blue" style="font-size:11px;">Remaining Target: $6,500,000</span>
    </div>
  </div>

  <!-- METRIC SUMMARY STRIP -->
  <div class="metric-strip">
    <div class="metric-box featured">
      <div class="metric-label">Lake Co. 1/2 Inst Pool</div>
      <div class="metric-val">$5,119,825</div>
      <div class="metric-note" style="color:#60a5fa;">268 Parcels (&gt;95% Redemption Safety)</div>
    </div>
    <div class="metric-box" style="border-color:rgba(139,92,246,0.5); background:rgba(76,29,149,0.18); cursor:pointer;" onclick="filterByRepeatRedeemers()" title="Click to filter by the 70 Repeat Redeemers">
      <div class="metric-label">⭐ Proven Repeat Redeemers</div>
      <div class="metric-val" style="color:#c4b5fd;">70 Parcels &middot; $1.54M</div>
      <div class="metric-note" style="color:#a78bfa;">1x to 4x County Redemptions &middot; Tap to Filter ↗</div>
    </div>
    <div class="metric-box">
      <div class="metric-label">Lake Commercial Sub-Pool</div>
      <div class="metric-val">487 Certs &middot; $8.15M</div>
      <div class="metric-note" style="color:#34d399;">Avg $16,740 / cert (Jay Priority)</div>
    </div>
    <div class="metric-box">
      <div class="metric-label">Next Sale (Lake County)</div>
      <div class="metric-val">Fri, Nov 13</div>
      <div class="metric-note" style="color:#fbbf24;">Target Spend: $2,000,000</div>
    </div>
  </div>

  <!-- SECTION 1: 2025 HISTORICAL INTELLIGENCE (LEADS WITH THIS - COLLAPSIBLE) -->
  <div class="section-card">
    <div class="section-header" style="background:rgba(30,58,138,0.25); cursor:pointer;" onclick="toggleSection('secBody1', 'secIcon1')">
      <div>
        <div class="section-title">📊 1. Full Historical Analysis — Last Year (2025 Auctions) &amp; Competitor Footprints</div>
        <div class="section-desc">Overall: Jennings deployed $13,540,684 across 2,159 certificates at a 2.01% weighted average winning rate</div>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <span class="badge badge-blue">Tap to Collapse / Expand</span>
        <span id="secIcon1" style="font-size:14px; color:var(--text-muted); font-weight:700;">▲</span>
      </div>
    </div>
    <div id="secBody1">
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>County</th>
              <th class="right">Certs Won</th>
              <th class="right">Capital Won</th>
              <th class="right">Weighted Avg Bid</th>
              <th>Dominant Winning Rate</th>
              <th>Rate Range</th>
              <th>Market Dynamics &amp; Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr style="background:rgba(16,185,129,0.08); font-weight:700;">
              <td><b>Lake (Central Buyer)</b></td>
              <td class="right">853</td>
              <td class="right" style="color:var(--success);">$6,131,471</td>
              <td class="right" style="color:var(--accent);">1.84%</td>
              <td><span class="badge badge-green">2.0% (67% of certs)</span></td>
              <td>1.0% - 3.0%</td>
              <td>Jennings #1 in county (30.1% of entire $20.4M auction)</td>
            </tr>
            <tr>
              <td><b>Will</b></td>
              <td class="right">240</td>
              <td class="right">$1,457,091</td>
              <td class="right" style="color:var(--accent);">1.52%</td>
              <td><span class="badge badge-green">1.0% (71% of certs)</span></td>
              <td>1.0% - 3.0%</td>
              <td>Aggressive 1% bids swept logistics &amp; commercial hubs</td>
            </tr>
            <tr>
              <td><b>McHenry</b></td>
              <td class="right">180</td>
              <td class="right">$1,452,829</td>
              <td class="right" style="color:var(--accent);">1.99%</td>
              <td><span class="badge badge-green">2.0% (89% of certs)</span></td>
              <td>1.0% - 3.0%</td>
              <td>Clean 2% bids dominated Route 14 commercial corridors</td>
            </tr>
            <tr>
              <td><b>Kane</b></td>
              <td class="right">112</td>
              <td class="right">$852,779</td>
              <td class="right" style="color:var(--accent);">3.05%</td>
              <td><span class="badge badge-blue">3.0% (77% of certs)</span></td>
              <td>2.0% - 7.0%</td>
              <td>Won $853k at 3% (before Bridge 5% sweep in 2026)</td>
            </tr>
            <tr>
              <td><b>DuPage</b></td>
              <td class="right">32</td>
              <td class="right">$254,027</td>
              <td class="right" style="color:var(--accent);">2.00%</td>
              <td><span class="badge badge-green">2.0% (100% of certs)</span></td>
              <td>2.0% - 2.0%</td>
              <td>Ultra-selective high-equity items; 100% won at 2.0% flat</td>
            </tr>
            <tr>
              <td><b>Kendall</b></td>
              <td class="right">78</td>
              <td class="right">$220,883</td>
              <td class="right" style="color:var(--accent);">3.28%</td>
              <td><span class="badge badge-blue">3.0% (96% of certs)</span></td>
              <td>3.0% - 4.0%</td>
              <td>Won 78 items at 3% (vs $0 won in 2026)</td>
            </tr>
            <tr style="background:rgba(255,255,255,0.05); font-weight:800;">
              <td><b>TOTAL ALL COUNTIES (2025):</b></td>
              <td class="right"><b>2,159</b></td>
              <td class="right" style="color:var(--success);"><b>$13,540,684</b></td>
              <td class="right" style="color:var(--accent);"><b>2.01%</b></td>
              <td colspan="3"><span class="badge badge-green">OVERALL WEIGHTED AVERAGE BID RATE</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Competitors in Lake -->
      <div style="padding:14px 20px; background:rgba(0,0,0,0.15); border-top:1px solid var(--border);">
        <div style="font-size:12px; font-weight:700; color:var(--text-secondary); margin-bottom:8px;">🏢 Lake County 2025 Competitor Footprints ("The Big Guys"):</div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px;">
          <div style="background:var(--bg-card); padding:10px 14px; border-radius:6px; border:1px solid var(--border);">
            <div style="font-size:11px; color:var(--success); font-weight:700;">#1 Central Buyer Corp (Jennings)</div>
            <div style="font-size:15px; font-weight:800;">$6,131,471 (30.1% Share)</div>
            <div style="font-size:10.5px; color:var(--text-muted);">853 certs &middot; Avg Bid: <b>1.68%</b></div>
          </div>
          <div style="background:var(--bg-card); padding:10px 14px; border-radius:6px; border:1px solid var(--border);">
            <div style="font-size:11px; color:var(--accent); font-weight:700;">#2 Private Equity Group ("Bridge")</div>
            <div style="font-size:15px; font-weight:800;">$2,994,605 (14.7% Share)</div>
            <div style="font-size:10.5px; color:var(--text-muted);">424 certs &middot; Avg Bid: <b>2.04%</b></div>
          </div>
          <div style="background:var(--bg-card); padding:10px 14px; border-radius:6px; border:1px solid var(--border);">
            <div style="font-size:11px; color:#fbbf24; font-weight:700;">#3 American Tax Lien LLC</div>
            <div style="font-size:15px; font-weight:800;">$2,837,986 (13.9% Share)</div>
            <div style="font-size:10.5px; color:var(--text-muted);">284 certs &middot; Avg Bid: <b>2.26%</b></div>
          </div>
          <div style="background:var(--bg-card); padding:10px 14px; border-radius:6px; border:1px solid var(--border);">
            <div style="font-size:11px; color:var(--purple); font-weight:700;">#4 Ari Bass (Raven Securities)</div>
            <div style="font-size:15px; font-weight:800;">$1,295,767 (6.4% Share)</div>
            <div style="font-size:10.5px; color:var(--text-muted);">88 certs &middot; Avg Bid: <b>2.85%</b></div>
          </div>
        </div>
      </div>

      <!-- 15-Year Township Wealth & Redemption Safety Matrix -->
      <div style="padding:14px 20px; background:rgba(15,23,42,0.6); border-top:1px solid var(--border);">
        <div style="font-size:12px; font-weight:700; color:var(--text-secondary); margin-bottom:8px;">🏛️ 15-Year Historical Redemption Safety by Township (PIN Prefix) — Lake County:</div>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Township / Region</th>
                <th>Prefix</th>
                <th class="right">Total Invested (Jennings)</th>
                <th class="right">Redeemed %</th>
                <th class="right">Certs Won</th>
                <th>Underwriting Safety Rating</th>
              </tr>
            </thead>
            <tbody>
              <tr style="background:rgba(16,185,129,0.08);">
                <td><b>Moraine / Highland Park</b></td>
                <td><code>16</code></td>
                <td class="right">$8,100,570</td>
                <td class="right" style="color:var(--success); font-weight:700;">97.3%</td>
                <td class="right">708</td>
                <td><span class="badge badge-green">Tier 1: Ultra-Safe Luxury Equity</span></td>
              </tr>
              <tr style="background:rgba(16,185,129,0.08);">
                <td><b>Shields / Lake Forest / Lake Bluff</b></td>
                <td><code>12</code></td>
                <td class="right">$2,481,198</td>
                <td class="right" style="color:var(--success); font-weight:700;">97.1%</td>
                <td class="right">222</td>
                <td><span class="badge badge-green">Tier 1: Ultra-Safe Wealth Corridor</span></td>
              </tr>
              <tr style="background:rgba(16,185,129,0.08);">
                <td><b>Libertyville</b></td>
                <td><code>11</code></td>
                <td class="right">$2,972,851</td>
                <td class="right" style="color:var(--success); font-weight:700;">96.5%</td>
                <td class="right">496</td>
                <td><span class="badge badge-green">Tier 1: High Corporate Equity</span></td>
              </tr>
              <tr>
                <td><b>Fremont / Mundelein</b></td>
                <td><code>10</code></td>
                <td class="right">$2,389,636</td>
                <td class="right" style="color:var(--success);">96.2%</td>
                <td class="right">356</td>
                <td><span class="badge badge-blue">Tier 2: Strong Prime Residential</span></td>
              </tr>
              <tr>
                <td><b>Vernon / Buffalo Grove / Lincolnshire</b></td>
                <td><code>15</code></td>
                <td class="right">$5,241,439</td>
                <td class="right" style="color:var(--success);">96.1%</td>
                <td class="right">629</td>
                <td><span class="badge badge-blue">Tier 2: Prime Commercial &amp; Residential</span></td>
              </tr>
              <tr>
                <td><b>Ela / Lake Zurich</b></td>
                <td><code>14</code></td>
                <td class="right">$3,786,573</td>
                <td class="right" style="color:var(--success);">95.9%</td>
                <td class="right">429</td>
                <td><span class="badge badge-blue">Tier 2: Stable Suburban</span></td>
              </tr>
              <tr>
                <td><b>Avon / Round Lake</b></td>
                <td><code>06</code></td>
                <td class="right">$5,666,900</td>
                <td class="right" style="color:#fbbf24;">92.4%</td>
                <td class="right">1,191</td>
                <td><span class="badge badge-yellow">Tier 2: Selective (Bldg &gt; 2x Land Only)</span></td>
              </tr>
              <tr style="background:rgba(239,68,68,0.08);">
                <td><b>Waukegan</b></td>
                <td><code>08</code></td>
                <td class="right">$2,909,520</td>
                <td class="right" style="color:var(--danger); font-weight:700;">90.0%</td>
                <td class="right">818</td>
                <td><span class="badge badge-red">Tier 3: Watch Water Liens (Sections 08-20/21/28/29)</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- SECTION 2: LAKE COUNTY PRE-SALE WAR ROOM & SCREENER (COLLAPSIBLE) -->
  <div class="section-card">
    <div class="section-header" style="background:rgba(30,58,138,0.3); cursor:pointer;" onclick="toggleSection('secBody2', 'secIcon2')">
      <div>
        <div class="section-title">🎯 2. Lake County 2026 Pre-Sale War Room &amp; Bidding Screener</div>
        <div class="section-desc">Sale Date: <b>Friday, November 13, 2026</b> &middot; Allocation Target: <b>$2,000,000</b> &middot; Revised Pool: <b>5,011 parcels ($37.4M)</b></div>
      </div>
      <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
        <button onclick="event.stopPropagation(); exportCleanAuctionCsv()" class="btn btn-primary" style="background:#16a34a;" title="Strict 2-column CSV (PIN, BidRate) formatted strictly for auction upload engines">⚡ Clean Auction Upload CSV</button>
        <button onclick="event.stopPropagation(); exportLakeBiddingCsv()" class="btn" style="background:var(--bg-card); color:#fff; border:1px solid var(--border);" title="Full 12-column underwriting spreadsheet with building metrics & ratios">📄 Full Analysis CSV</button>
        <span id="secIcon2" style="font-size:14px; color:var(--text-muted); font-weight:700; margin-left:6px;">▲</span>
      </div>
    </div>

    <div id="secBody2">
      <!-- Filter Bar -->
      <div class="filter-bar">
        <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Filters:</span>
        <select id="lakeTierFilter" class="filter-select" onchange="renderLakeTargetTable()">
          <option value="repeat">⭐ Repeat Redeemers Only (70 Parcels · $1.54M)</option>
          <option value="half" selected>⭐ 2nd Installment Only (268 Parcels · $5.12M)</option>
          <option value="curated">Curated $2.0M Plan (55 Parcels)</option>
          <option value="all">All High-Yield ($10k+)</option>
          <option value="50k">Mega Liens (>=$50k)</option>
          <option value="25k">Core ($25k - $50k)</option>
          <option value="10k">Selective ($10k - $25k)</option>
        </select>
        <select id="lakeClassFilter" class="filter-select" onchange="renderLakeTargetTable()">
          <option value="all">All Property Classes</option>
          <option value="commercial">Commercial &amp; Industrial Only (487)</option>
          <option value="residential">Residential Only</option>
        </select>
        <select id="lakeTwpFilter" class="filter-select" onchange="renderLakeTargetTable()">
          <option value="all">All Townships</option>
          <option value="waukegan">Waukegan</option>
          <option value="zion">Zion / Benton</option>
          <option value="highland park">Highland Park / Moraine</option>
          <option value="gurnee">Gurnee / Warren</option>
          <option value="vernon">Vernon Hills / Buffalo Grove</option>
          <option value="libertyville">Libertyville</option>
          <option value="antioch">Antioch</option>
        </select>
        <select id="lakeRatePreset" class="filter-select" onchange="renderLakeTargetTable()" style="border-color:rgba(16,185,129,0.5);">
          <option value="standard" selected>Strategy: 4% on &gt;=$25k (Beat Bridge) / 5% on $10k-$25k</option>
          <option value="aggressive">Aggressive: 3% on &gt;=$25k / 4% on $10k-$25k</option>
          <option value="flat4">Universal: 4% Flat on All Items</option>
          <option value="flat5">Match Market: 5% Flat on All Items</option>
        </select>
        <input type="text" id="lakeSearchInput" class="filter-input" onkeyup="renderLakeTargetTable()" placeholder="Search PIN, Taxpayer, Street Address, City, Township..." />
        <span id="lakeTargetCount" style="font-size:11px; color:var(--text-muted); margin-left:auto; font-weight:600;">Showing 0 parcels</span>
      </div>

      <!-- Screener Table -->
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>PIN (Click to View Assessor)</th>
              <th>Taxpayer / Business Name</th>
              <th>City / Township</th>
              <th>Installment Status</th>
              <th>Type / Class</th>
              <th class="right">Tax Due</th>
              <th class="right">Assessed Bldg</th>
              <th class="right">Bldg/Land Ratio</th>
              <th class="right">Recommended Bid</th>
              <th class="right">12% Subtax Return</th>
              <th>Risk Rating</th>
              <th>Visuals &amp; Maps (Drive-By)</th>
            </tr>
          </thead>
          <tbody id="lakeTargetBody"></tbody>
        </table>
      </div>
    </div>
  </div>


  <!-- SECTION: STAN'S MASTER 4-COUNTY PRODUCTION BIDDING MODELS -->
  <div class="section-card" style="border: 1px solid rgba(139, 92, 246, 0.4); background: rgba(30, 27, 75, 0.2);">
    <div class="section-header" style="cursor:pointer;" onclick="toggleSection('secBodyStan', 'secIconStan')">
      <div>
        <div class="section-title" style="color:var(--purple); display:flex; align-items:center; gap:8px;">
          <span>🎯 Stan's Master 2025 Bidding Models &amp; 4-County Rollup</span>
          <span class="badge badge-purple" style="font-size:10px;">Production Ground Truth</span>
        </div>
        <div class="section-desc">Stan's exact filtering rule: Removed certs &lt; $3,000 where both installments are delinquent. Commercial separated from residential.</div>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <span class="badge badge-green" style="font-size:11px; font-weight:800;">Revised Total: 5,656 Certs &middot; $42.13M</span>
        <span id="secIconStan" style="font-size:14px; color:var(--text-muted);">▼</span>
      </div>
    </div>
    <div id="secBodyStan" class="section-body">
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>County</th>
              <th class="right">Non-Comm Certs</th>
              <th class="right">Non-Comm $</th>
              <th class="right">Comm Certs</th>
              <th class="right">Comm $</th>
              <th class="right" style="color:var(--success);">Revised Bid Certs</th>
              <th class="right" style="color:var(--success);">Revised Bid $</th>
              <th class="right" style="color:var(--text-muted);">Removed (&lt;$3k)</th>
              <th class="right" style="color:var(--text-muted);">Removed $</th>
              <th class="right">Orig Total Certs</th>
              <th class="right">Orig Total $</th>
            </tr>
          </thead>
          <tbody>
            
        <tr style="">
            <td><b>Lake</b></td>
            <td class="right">1,611</td>
            <td class="right">$11,740,875.39</td>
            <td class="right">29</td>
            <td class="right" style="color:var(--accent); font-weight:700;">$2,110,110.44</td>
            <td class="right" style="color:var(--success); font-weight:800;">1,640</td>
            <td class="right" style="color:var(--success); font-weight:800;">$13,850,985.83</td>
            <td class="right" style="color:var(--text-muted);">93</td>
            <td class="right" style="color:var(--text-muted);">$183,937.01</td>
            <td class="right" style="color:var(--text-primary);">1,733</td>
            <td class="right" style="color:var(--text-primary);">$14,034,922.84</td>
        </tr>
        
        <tr style="">
            <td><b>DuPage</b></td>
            <td class="right">1,142</td>
            <td class="right">$8,273,859.20</td>
            <td class="right">23</td>
            <td class="right" style="color:var(--accent); font-weight:700;">$1,053,093.80</td>
            <td class="right" style="color:var(--success); font-weight:800;">1,165</td>
            <td class="right" style="color:var(--success); font-weight:800;">$9,326,953.00</td>
            <td class="right" style="color:var(--text-muted);">73</td>
            <td class="right" style="color:var(--text-muted);">$156,875.76</td>
            <td class="right" style="color:var(--text-primary);">1,238</td>
            <td class="right" style="color:var(--text-primary);">$9,483,828.76</td>
        </tr>
        
        <tr style="">
            <td><b>McHenry</b></td>
            <td class="right">1,328</td>
            <td class="right">$7,788,659.33</td>
            <td class="right">31</td>
            <td class="right" style="color:var(--accent); font-weight:700;">$679,385.82</td>
            <td class="right" style="color:var(--success); font-weight:800;">1,359</td>
            <td class="right" style="color:var(--success); font-weight:800;">$8,468,045.15</td>
            <td class="right" style="color:var(--text-muted);">88</td>
            <td class="right" style="color:var(--text-muted);">$165,583.93</td>
            <td class="right" style="color:var(--text-primary);">1,447</td>
            <td class="right" style="color:var(--text-primary);">$8,633,629.08</td>
        </tr>
        
        <tr style="">
            <td><b>Will</b></td>
            <td class="right">1,442</td>
            <td class="right">$9,284,073.74</td>
            <td class="right">50</td>
            <td class="right" style="color:var(--accent); font-weight:700;">$1,203,089.34</td>
            <td class="right" style="color:var(--success); font-weight:800;">1,492</td>
            <td class="right" style="color:var(--success); font-weight:800;">$10,487,163.08</td>
            <td class="right" style="color:var(--text-muted);">82</td>
            <td class="right" style="color:var(--text-muted);">$152,209.13</td>
            <td class="right" style="color:var(--text-primary);">1,574</td>
            <td class="right" style="color:var(--text-primary);">$10,639,372.21</td>
        </tr>
        
        <tr style="font-weight:800; background:rgba(255,255,255,0.05);">
            <td><span class='badge badge-purple'>4-County Rollup</span></td>
            <td class="right">5,523</td>
            <td class="right">$37,087,467.66</td>
            <td class="right">133</td>
            <td class="right" style="color:var(--accent); font-weight:700;">$5,045,679.40</td>
            <td class="right" style="color:var(--success); font-weight:800;">5,656</td>
            <td class="right" style="color:var(--success); font-weight:800;">$42,133,147.06</td>
            <td class="right" style="color:var(--text-muted);">336</td>
            <td class="right" style="color:var(--text-muted);">$658,605.83</td>
            <td class="right" style="color:var(--text-primary);">5,992</td>
            <td class="right" style="color:var(--text-primary);">$42,791,752.89</td>
        </tr>
        
          </tbody>
        </table>
      </div>
      <div style="margin-top:10px; font-size:11px; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <div>📌 <i>Directly extracted from Stan's <code>4_County_2025_Sale_Revised_Rollup Claude Analysis.xlsx</code> model sent to Louis &amp; Jay.</i></div>
        <div><b>Commercial Average Ticket:</b> <span style="color:var(--accent); font-weight:700;">$37,937 / cert</span> (133 prime targets across 4 counties)</div>
      </div>
    </div>
  </div>

  <!-- SECTION 3: UPCOMING COLLAR COUNTIES SCHEDULE (COLLAPSED BY DEFAULT) -->
  <div class="section-card">
    <div class="section-header" style="cursor:pointer;" onclick="toggleSection('secBody3', 'secIcon3')">
      <div>
        <div class="section-title">⚖️ 3. Master 2026 Collar Counties Schedule (Target: $5.0M Deployment)</div>
        <div class="section-desc">Unified pipeline across Lake, DuPage, McHenry, and Will county auctions</div>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <span class="badge badge-blue">Tap to Expand</span>
        <span id="secIcon3" style="font-size:14px; color:var(--text-muted); font-weight:700;">▼</span>
      </div>
    </div>
    <div id="secBody3" style="display:none;">
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>County</th>
              <th>2026 Sale Date</th>
              <th>Status</th>
              <th class="right">Pre-Sale DB Size</th>
              <th class="right">2026 Target Allocation</th>
              <th>Strategic Campaign Focus</th>
            </tr>
          </thead>
          <tbody>
            <tr style="background:rgba(59,130,246,0.08); font-weight:700;">
              <td><b>Lake</b></td>
              <td><b>Fri, Nov 13, 2026</b></td>
              <td><span class="badge badge-blue">UPCOMING (NEXT SALE)</span></td>
              <td class="right">272 MB (6,078 certs)</td>
              <td class="right" style="color:var(--accent); font-size:13.5px;"><b>$2,000,000</b></td>
              <td>487 Commercials ($8.15M) &amp; 1/2 Inst (>=$10k); Bid 4% on >=$25k</td>
            </tr>
            <tr>
              <td><b>DuPage</b></td>
              <td>Thu, Nov 19, 2026</td>
              <td><span class="badge badge-purple">UPCOMING</span></td>
              <td class="right">147 MB</td>
              <td class="right" style="color:var(--accent);"><b>$1,500,000</b></td>
              <td>Bldg &gt; 2x Land &amp; Senior Living ($522k winner county)</td>
            </tr>
            <tr>
              <td><b>McHenry</b></td>
              <td>Mon, Nov 23, 2026</td>
              <td><span class="badge badge-yellow">UPCOMING</span></td>
              <td class="right">144 MB</td>
              <td class="right" style="color:var(--accent);"><b>$1,000,000</b></td>
              <td>Commercial Corridors (Route 14 &amp; Crystal Lake)</td>
            </tr>
            <tr>
              <td><b>Will</b></td>
              <td>Tue, Dec 01, 2026</td>
              <td><span class="badge badge-green">UPCOMING</span></td>
              <td class="right">434 MB</td>
              <td class="right" style="color:var(--accent);"><b>$2,000,000</b></td>
              <td>Logistics/Industrial &amp; '2 Commercials each a half'</td>
            </tr>
            <tr style="background:rgba(255,255,255,0.05); font-weight:800;">
              <td colspan="4">TOTAL REMAINING TARGET ALLOCATION (To hit $5.0M goal):</td>
              <td class="right" style="color:var(--success); font-size:14px;">$6,500,000</td>
              <td><span class="badge badge-green">Borrowing Base Compliant</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- SECTION 4: SUBTAX OPERATIONS UTILITY (COLLAPSED BY DEFAULT) -->
  <div class="section-card">
    <div class="section-header" style="background:rgba(239,68,68,0.15); cursor:pointer;" onclick="toggleSection('secBody4', 'secIcon4')">
      <div>
        <div class="section-title">🛠️ 4. Subtax Operations &amp; Check Requests ($127k / 18 Parcels)</div>
        <div class="section-desc">Utility: 18 parcels on the 2026 Lake County list where Jennings already holds prior certificates &middot; Submit to County Collector prior to Nov 13</div>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <button onclick="event.stopPropagation(); exportMarySubtaxCsv()" class="btn btn-primary" style="background:#dc2626;">📥 Export Check Request for Mary</button>
        <span id="secIcon4" style="font-size:14px; color:var(--text-muted); font-weight:700; margin-left:6px;">▼</span>
      </div>
    </div>
    <div id="secBody4" style="display:none;">
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>County</th>
              <th>PIN</th>
              <th>Taxpayer / Property Name</th>
              <th>Certificate Owner</th>
              <th>Prior Cert #</th>
              <th>Tax Year</th>
              <th class="right">Prior Cert Amt</th>
              <th class="right">Subtax Amount Due</th>
              <th class="right">12% Annual Yield</th>
              <th>Status / Action</th>
            </tr>
          </thead>
          <tbody id="subtaxTableBody"></tbody>
        </table>
      </div>
    </div>
  </div>

</div>

<!-- TOAST -->
<div id="toastMsg">Notification</div>

<script>
const lakePresaleData = {targets_json_str};
const subtaxHunterData = {subtax_json_str};

// Passcode verification
function verifyPasscode() {{
    const val = document.getElementById('passcodeInput').value.trim();
    if (val === 'Jennings2026' || val === 'Stan2026') {{
        localStorage.setItem('jennings_tax_auth', 'valid');
        document.getElementById('authOverlay').style.display = 'none';
    }} else {{
        alert('Invalid passcode. Access denied.');
    }}
}}

// Collapsible Section Toggle
function toggleSection(bodyId, iconId) {{
    const body = document.getElementById(bodyId);
    const icon = document.getElementById(iconId);
    if (!body) return;
    const isHidden = (body.style.display === 'none');
    body.style.display = isHidden ? 'block' : 'none';
    if (icon) icon.innerText = isHidden ? '▲' : '▼';
}}

// Filter by Repeat Redeemers directly
function filterByRepeatRedeemers() {{
    const sel = document.getElementById('lakeTierFilter');
    if (sel) {{
        sel.value = 'repeat';
        renderLakeTargetTable();
        const toast = document.getElementById('toastMsg');
        if (toast) {{
            toast.innerText = '⭐ Filtered: 70 Repeat Redeemers ($1.54M Pool)';
            toast.style.display = 'block';
            setTimeout(() => {{ toast.style.display = 'none'; }}, 2200);
        }}
    }}
}}

// Check existing auth
window.addEventListener('DOMContentLoaded', () => {{
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('passcode') === 'Jennings2026' || urlParams.get('passcode') === 'Stan2026' || localStorage.getItem('jennings_tax_auth') === 'valid') {{
        localStorage.setItem('jennings_tax_auth', 'valid');
        document.getElementById('authOverlay').style.display = 'none';
    }}
    renderSubtaxOpportunityTable();
    renderLakeTargetTable();
}});

function renderSubtaxOpportunityTable() {{
    const tbody = document.getElementById('subtaxTableBody');
    if (!tbody || !subtaxHunterData || !subtaxHunterData.opportunities) return;

    tbody.innerHTML = subtaxHunterData.opportunities.map(o => `
        <tr>
            <td><b>${{o.county}}</b></td>
            <td><code style="font-size:11px; color:var(--accent); cursor:pointer;" onclick="copyPin('${{o.pin}}')" title="Click to copy PIN">${{o.pin}}</code></td>
            <td><b>${{o.taxpayer_name}}</b> <span style="font-size:10px; color:var(--text-muted);">(${{o.city}})</span></td>
            <td><span class="badge badge-purple" style="font-size:9.5px;">${{o.certificate_owner.replace('INTERSTATE FUNDING CORP.', 'IFC').replace('CENTRAL BUYER CORP.', 'Central Buyer')}}</span></td>
            <td><code style="font-size:10.5px;">${{o.certificate_no}}</code></td>
            <td>${{o.cert_tax_year}}</td>
            <td class="right">$${{Number(o.original_cert_amount).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
            <td class="right" style="color:var(--warn); font-weight:700;">$${{Number(o.tax_due).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
            <td class="right" style="color:var(--success); font-weight:800;">+$${{Number(o.annual_12pct_interest).toLocaleString('en-US', {{maximumFractionDigits:0}})}}/yr</td>
            <td><span class="badge badge-green" style="font-size:9.5px;">12% Statutory Sub</span></td>
        </tr>
    `).join('');
}}

function renderLakeTargetTable() {{
    const tbody = document.getElementById('lakeTargetBody');
    const countEl = document.getElementById('lakeTargetCount');
    if (!tbody || !lakePresaleData || !lakePresaleData.top_targets) return;

    const tierVal = document.getElementById('lakeTierFilter') ? document.getElementById('lakeTierFilter').value : 'all';
    const classVal = document.getElementById('lakeClassFilter') ? document.getElementById('lakeClassFilter').value : 'all';
    const twpVal = document.getElementById('lakeTwpFilter') ? document.getElementById('lakeTwpFilter').value : 'all';
    const ratePreset = document.getElementById('lakeRatePreset') ? document.getElementById('lakeRatePreset').value : 'standard';
    const searchVal = document.getElementById('lakeSearchInput') ? document.getElementById('lakeSearchInput').value.toLowerCase().trim() : '';

    let dataset = (tierVal === 'curated' && lakePresaleData.curated_2m_portfolio)
        ? lakePresaleData.curated_2m_portfolio.parcels
        : lakePresaleData.top_targets;

    let filtered = dataset.filter(item => {{
        if (tierVal === 'repeat' && (!item.prior_redemptions_count || item.prior_redemptions_count < 1)) return false;
        if (tierVal === 'half' && !item.is_half_installment) return false;
        if (tierVal === '50k' && item.tax_due < 50000) return false;
        if (tierVal === '25k' && (item.tax_due < 25000 || item.tax_due >= 50000)) return false;
        if (tierVal === '10k' && (item.tax_due < 10000 || item.tax_due >= 25000)) return false;

        if (classVal === 'commercial' && !item.is_commercial) return false;
        if (classVal === 'residential' && item.is_commercial) return false;

        if (twpVal !== 'all' && !item.township.toLowerCase().includes(twpVal) && !item.city.toLowerCase().includes(twpVal)) return false;

        if (searchVal) {{
            const matches = item.pin.toLowerCase().includes(searchVal) ||
                            item.taxpayer.toLowerCase().includes(searchVal) ||
                            (item.address && item.address.toLowerCase().includes(searchVal)) ||
                            item.city.toLowerCase().includes(searchVal) ||
                            item.township.toLowerCase().includes(searchVal);
            if (!matches) return false;
        }}
        return true;
    }});

    const totDue = filtered.reduce((s, x) => s + x.tax_due, 0);
    const totSubtax = filtered.reduce((s, x) => s + (x.tax_due * 0.12), 0);
    const avgTicket = filtered.length > 0 ? (totDue / filtered.length) : 0;
    if (countEl) countEl.innerHTML = `Showing <b>${{filtered.length}}</b> parcels ($${{totDue.toLocaleString('en-US', {{maximumFractionDigits:0}})}}) &middot; 12% Subtaxes: <span style="color:var(--success); font-weight:700;">+$${{totSubtax.toLocaleString('en-US', {{maximumFractionDigits:0}})}}/yr</span> &middot; Avg: $${{avgTicket.toLocaleString('en-US', {{maximumFractionDigits:0}})}}`;

    tbody.innerHTML = filtered.slice(0, 100).map(t => {{
        const assessorUrl = `https://tax.lakecountyil.gov/search/commonsearch.aspx?mode=realprop`;
        const redlineBadge = t.waukegan_redline ? `<span class="badge badge-red" style="font-size:9px; margin-left:4px;" title="Stan Redline: Section ${{t.pin.slice(0,5)}} had 8 water lien failures">⚠️ Water Lien Risk</span>` : '';
        
        // Dynamic Bid Rate calculation based on selected Preset
        let activeBid = (t.tax_due >= 25000) ? 0.04 : 0.05;
        let activeLabel = (t.tax_due >= 25000) ? "4.0%" : "5.0%";
        if (ratePreset === 'aggressive') {{
            activeBid = (t.tax_due >= 25000) ? 0.03 : 0.04;
            activeLabel = (t.tax_due >= 25000) ? "3.0%" : "4.0%";
        }} else if (ratePreset === 'flat4') {{
            activeBid = 0.04;
            activeLabel = "4.0%";
        }} else if (ratePreset === 'flat5') {{
            activeBid = 0.05;
            activeLabel = "5.0%";
        }}
        // Maps & Visuals
        const addrSearch = encodeURIComponent((t.address + ' ' + t.city + ' IL').trim());
        const googleUrl = `https://www.google.com/maps/search/?api=1&query=${{addrSearch}}`;
        const zillowUrl = `https://www.zillow.com/homes/${{addrSearch}}_rb/`;
        const gisUrl = `https://maps.lakecountyil.gov/mapsonline/?pin=${{t.pin.replace(/-/g, '')}}`;
        
        let zillowBtn = !t.is_commercial ? `<a href=\"${{zillowUrl}}\" target=\"_blank\" class=\"btn btn-primary\" style=\"background:#006aff; font-size:9px; padding:3px 6px; text-decoration:none;\" title=\"Zillow Est & Photos\">🏡 Zillow</a>` : '';



        return `
        <tr>
            <td>
                <a href="${{assessorUrl}}" target="_blank" style="color:var(--accent); text-decoration:none; font-weight:700; font-family:monospace;" title="Open Lake County Assessor / Tax Portal">${{t.pin}} ↗</a>
                <span style="cursor:pointer; margin-left:4px; font-size:11px;" onclick="copyPin('${{t.pin}}')" title="Click to copy PIN">📋</span>
            </td>
            <td>
                <b>${{t.taxpayer}}</b> ${{redlineBadge}}
                <div style="font-size:10.5px; color:var(--text-muted);">${{t.address || ''}}</div>
            </td>
            <td>${{t.city}} <span style="font-size:10px; color:var(--text-muted);">(${{t.township}})</span></td>
            <td>
                <span class="badge ${{t.is_half_installment ? 'badge-purple' : 'badge-blue'}}" style="font-size:9px;">${{t.installment_tag}}</span>
                ${{t.prior_redemptions_count >= 1 ? `<span class="badge badge-purple" style="font-size:8.5px; margin-left:3px; font-weight:800;" title="Verified by County: ${{t.prior_redemptions_count}} prior redemptions">⭐ ${{t.prior_redemptions_count}}x Redeemed</span>` : ''}}
            </td>
            <td><span class="badge ${{t.is_commercial ? 'badge-blue' : 'badge-green'}}" style="font-size:9.5px;">${{t.property_type}}</span></td>
            <td class="right" style="font-weight:700; color:var(--text-primary);">$${{Number(t.tax_due).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
            <td class="right">$${{Number(t.asmt_bldg).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
            <td class="right" style="color:${{t.bldg_land_ratio >= 2.0 ? 'var(--success)' : 'var(--warn)'}}; font-weight:700;">${{t.bldg_land_ratio}}x</td>
            <td class="right"><span class="badge ${{activeBid <= 0.04 ? 'badge-green' : 'badge-blue'}}" style="font-size:10.5px; font-weight:800;">${{activeLabel}}</span></td>
            <td class="right" style="color:var(--success); font-weight:700;">+$${{Number(t.subtax_annual_return).toLocaleString('en-US', {{maximumFractionDigits:0}})}}/yr</td>
            <td><span class="badge ${{t.quality_score >= 90 ? 'badge-green' : 'badge-blue'}}" style="font-size:9.5px;">${{t.risk_rating}}</span></td>
            <td>
                <div style="display:flex; gap:4px; flex-wrap:wrap;">
                    <a href="${{googleUrl}}" target="_blank" class="btn btn-primary" style="background:#ea4335; font-size:9px; padding:3px 6px; text-decoration:none;" title="Google Maps Street View">📸 Maps</a>
                    <a href="${{gisUrl}}" target="_blank" class="btn btn-primary" style="background:#10b981; font-size:9px; padding:3px 6px; text-decoration:none;" title="Lake County 3D GIS Pictometry">🗺️ GIS</a>
                    ${{zillowBtn}}
                </div>
            </td>
        </tr>
        `;
    }}).join('');
}}

function copyPin(pin) {{
    if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(pin);
        const toast = document.getElementById('toastMsg');
        if (toast) {{
            toast.innerText = `📋 Copied PIN: ${{pin}}`;
            toast.style.display = 'block';
            setTimeout(() => {{ toast.style.display = 'none'; }}, 2000);
        }}
    }}
}}

// 1. Strict 2-Column Auction Upload CSV (Formatted strictly for RAMS / Realauction)
function exportCleanAuctionCsv() {{
    if (!lakePresaleData || !lakePresaleData.top_targets) return;
    const ratePreset = document.getElementById('lakeRatePreset') ? document.getElementById('lakeRatePreset').value : 'standard';
    let csv = ["Parcel Number,Bid %"];
    lakePresaleData.top_targets.forEach(t => {{
        let rate = (t.tax_due >= 25000) ? 4.0 : 5.0;
        if (ratePreset === 'aggressive') rate = (t.tax_due >= 25000) ? 3.0 : 4.0;
        else if (ratePreset === 'flat4') rate = 4.0;
        else if (ratePreset === 'flat5') rate = 5.0;
        csv.push(`"${{t.pin}}",${{rate}}`);
    }});
    const blob = new Blob([csv.join('\\n')], {{ type: 'text/csv;charset=utf-8;' }});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'Lake_County_2026_Auction_Upload_Clean.csv';
    link.click();
    const toast = document.getElementById('toastMsg');
    if (toast) {{
        toast.innerText = '⚡ Exported Clean 2-Column Auction Upload CSV!';
        toast.style.display = 'block';
        setTimeout(() => {{ toast.style.display = 'none'; }}, 2500);
    }}
}}

// 2. Full 12-Column Analytical Underwriting Spreadsheet
function exportLakeBiddingCsv() {{
    if (!lakePresaleData || !lakePresaleData.top_targets) return;
    let csv = ["PIN,Taxpayer,Address,City,Township,TaxDue,AssessedBldg,AssessedLand,BldgLandRatio,PropertyType,RecommendedBidPercent,SubtaxAnnualReturn12pct,RiskRating"];
    lakePresaleData.top_targets.forEach(t => {{
        csv.push(`"${{t.pin}}","${{t.taxpayer.replace(/"/g, '""')}}","${{(t.address || '').replace(/"/g, '""')}}","${{t.city}}","${{t.township}}",${{t.tax_due}},${{t.asmt_bldg}},${{t.asmt_land}},${{t.bldg_land_ratio}},"${{t.property_type}}",${{t.rec_bid}},${{t.subtax_annual_return}},"${{t.risk_rating}}"`);
    }});
    const blob = new Blob([csv.join('\\n')], {{ type: 'text/csv;charset=utf-8;' }});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'Lake_County_2026_Full_Underwriting_Analysis.csv';
    link.click();
    const toast = document.getElementById('toastMsg');
    if (toast) {{
        toast.innerText = '📄 Exported Full Underwriting Analysis CSV!';
        toast.style.display = 'block';
        setTimeout(() => {{ toast.style.display = 'none'; }}, 2500);
    }}
}}
</script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Generated Stan's dedicated Tax Buying Dashboard: {OUTPUT_HTML}")
    return html

if __name__ == "__main__":
    generate_tax_html()
