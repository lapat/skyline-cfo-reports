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

  <!-- SECTION: STAN'S MASTER 2026 PRODUCTION BIDDING MODELS & 4-COUNTY ROLLUP (COMPLETE DATA SUITE) -->
  <div class="section-card" style="border: 2px solid rgba(139, 92, 246, 0.55); background: linear-gradient(135deg, rgba(30, 27, 75, 0.4), rgba(15, 23, 42, 0.55)); margin-bottom: 24px; box-shadow: 0 4px 25px rgba(139, 92, 246, 0.2);">
    <div class="section-header" style="background: rgba(139, 92, 246, 0.22); padding: 14px 20px; cursor: pointer;" onclick="toggleSection('stanPortalBody', 'stanPortalIcon')">
      <div>
        <div class="section-title" style="color: #c4b5fd; font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
          <span>🎯 Stan's Master 2026 Bidding Models &amp; 4-County Production Rollup</span>
          <span class="badge badge-purple" style="font-size: 10px; font-weight: 800;">Jay's 2026 Bidding Blueprint</span>
        </div>
        <div class="section-desc" style="color: var(--text-muted); font-size: 12px; margin-top: 3px;">
          Complete dataset parsed from Stan's 5 production Excel models &amp; Kane results emailed to Louis &amp; Jay. Master 4-County Rollup, 133 Commercial Targets ($5.05M), County Deep Dives, and Redlines.
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 10px;">
        <span class="badge badge-green" style="font-size: 12px; font-weight: 800; padding: 6px 12px;">Revised Upload: 5,656 Certs &middot; $42.13M</span>
        <span id="stanPortalIcon" style="font-size: 14px; color: var(--text-muted); font-weight: 700;">▲</span>
      </div>
    </div>
    
    <div id="stanPortalBody">
      <!-- 4 Strategic Takeaway Metrics -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; padding: 18px 20px 14px 20px;">
        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;">
          <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Revised Bidding Upload Pool</div>
          <div style="font-size: 22px; font-weight: 800; color: var(--success); margin: 4px 0;">5,656 Certs &middot; $42.13M</div>
          <div style="font-size: 11px; color: var(--text-secondary);">Non-Commercial ($37.09M) + Commercial ($5.05M)</div>
        </div>

        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;">
          <div style="font-size: 11px; color: var(--accent); text-transform: uppercase; font-weight: 700;">Commercial / Industrial Focus</div>
          <div style="font-size: 22px; font-weight: 800; color: var(--accent); margin: 4px 0;">133 Certs &middot; $5.05M</div>
          <div style="font-size: 11px; color: var(--text-secondary);"><b style="color:#60a5fa;">$37,937 / cert avg</b> (Jay's high-dollar priority)</div>
        </div>

        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;">
          <div style="font-size: 11px; color: var(--warn); text-transform: uppercase; font-weight: 700;">Stan's &lt;$3k Full-Inst Filter</div>
          <div style="font-size: 22px; font-weight: 800; color: var(--warn); margin: 4px 0;">336 Certs &middot; $658,606</div>
          <div style="font-size: 11px; color: var(--text-secondary);">Removed low-margin junk &amp; admin overhead</div>
        </div>

        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;">
          <div style="font-size: 11px; color: var(--purple); text-transform: uppercase; font-weight: 700;">Win Rate Reality &amp; Target Spend</div>
          <div style="font-size: 22px; font-weight: 800; color: #c4b5fd; margin: 4px 0;">32.1% Win Rate</div>
          <div style="font-size: 11px; color: var(--text-secondary);">$42.13M upload cleared $13.54M won @ 2.01% avg bid</div>
        </div>
      </div>

      <!-- Stan Multi-Tab Navigation (5 Rich Views) -->
      <div style="display: flex; gap: 8px; padding: 0 20px 12px 20px; border-bottom: 1px solid var(--border); flex-wrap: wrap;">
        <button id="stanPortalBtnRollup" onclick="switchStanSubTab('stanPortal', 'rollup')" class="btn btn-primary" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">📊 4-County Master Rollup</button>
        <button id="stanPortalBtnDeep" onclick="switchStanSubTab('stanPortal', 'deep')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">🗺️ County Strategy Deep Dives</button>
        <button id="stanPortalBtnComm" onclick="switchStanSubTab('stanPortal', 'comm')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">🏢 133 Prime Commercial Targets ($5.05M)</button>
        <button id="stanPortalBtnRedline" onclick="switchStanSubTab('stanPortal', 'redline')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">⚠️ Stan's Redlines &amp; Exclusions (58 Parcels)</button>
        <button id="stanPortalBtnKane" onclick="switchStanSubTab('stanPortal', 'kane')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">💎 Kane 2026 Live Buys (8 Certs @ 5%-7%)</button>
      </div>

      <!-- TAB 1: MASTER 4-COUNTY ROLLUP TABLE -->
      <div id="stanPortalTabRollup" style="display: block; padding: 14px 20px;">
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>County</th>
                <th class="right">Non-Comm Certs</th>
                <th class="right">Non-Comm $</th>
                <th class="right">Comm Certs</th>
                <th class="right">Comm $ (Avg ~$38k)</th>
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
            <tr style="font-weight:800; background:rgba(255,255,255,0.06);">
              <td><span class='badge badge-purple' style='font-size:11px; font-weight:800;'>4-County Rollup Total</span></td>
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
      </div>

      <!-- TAB 2: COUNTY STRATEGY DEEP DIVES -->
      <div id="stanPortalTabDeep" style="display: none; padding: 14px 20px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">
          
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:16px; border-top:3px solid #3b82f6;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h4 style="margin:0; font-size:14px; color:#3b82f6; font-weight:800;">Lake County Production Strategy</h4>
            <span class="badge badge-green" style="font-size:10px;">1,644 Kept</span>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-bottom:10px; line-height:1.4;">
            <b>Stan's Rule:</b> <i>Removed: certs under $3,000 where both installments are delinquent (1Inst = FALSE). Commercial = MSG "Commercial Improvements".</i>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Bid Distribution:</div>
            <span class='badge badge-blue' style='font-size:10px;'>2%: <b>1,176</b></span> <span class='badge badge-blue' style='font-size:10px;'>1%: <b>355</b></span> <span class='badge badge-blue' style='font-size:10px;'>3%: <b>80</b></span>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Property &amp; Flag Breakdown:</div>
            <div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Revised Non-Commercial</span><span><b>1,611</b> ($11,740,875)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Commercial</span><span><b>29</b> ($2,110,110)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Removed – Full Inst Under $3,000</span><span><b>93</b> ($183,937)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Residential Improvements</span><span><b>1,592</b> ($11,574,028)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Farm A Improvements</span><span><b>16</b> ($163,734)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Farmland</span><span><b>3</b> ($3,113)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Incl. "Do Not Buy- Redlined North Chgo" comment</span><span><b>37</b> ($185,773)</span></div>
          </div>
          <div style='margin-top:6px;'><div style='font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;'>Stan's Key Tags:</div><span class='badge badge-purple' style='font-size:9.5px;'>Do Not Buy- Redlined North Chgo: <b>37</b></span></div>
        </div>
        
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:16px; border-top:3px solid #10b981;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h4 style="margin:0; font-size:14px; color:#10b981; font-weight:800;">DuPage County Production Strategy</h4>
            <span class="badge badge-green" style="font-size:10px;">1,169 Kept</span>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-bottom:10px; line-height:1.4;">
            <b>Stan's Rule:</b> <i>Removed: certs under $3,000 where both installments are delinquent (HalfInstallment = FALSE). Commercial = ClassCode "60 - Commercial Improvements".</i>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Bid Distribution:</div>
            <span class='badge badge-blue' style='font-size:10px;'>2%: <b>776</b></span> <span class='badge badge-blue' style='font-size:10px;'>3%: <b>366</b></span>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Property &amp; Flag Breakdown:</div>
            <div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Revised Non-Commercial (Residential)</span><span><b>1,142</b> ($8,273,859)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Commercial</span><span><b>23</b> ($1,053,094)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Removed – Full Inst Under $3,000</span><span><b>73</b> ($156,876)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>2024 comment "DNB-Open Sold Taxes" (Revised Non-Commercial)</span><span><b>8</b> ($57,415)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>2024 comment "DNB-Open Sold Taxes" (Commercial)</span><span><b>0</b> ($0)</span></div>
          </div>
          
        </div>
        
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:16px; border-top:3px solid #f59e0b;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h4 style="margin:0; font-size:14px; color:#f59e0b; font-weight:800;">McHenry County Production Strategy</h4>
            <span class="badge badge-green" style="font-size:10px;">1,363 Kept</span>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-bottom:10px; line-height:1.4;">
            <b>Stan's Rule:</b> <i>Removed: certs under $3,000 where both installments are delinquent (1Inst = FALSE). Commercial = USE CODE 60 and 70. Cert amount = SaleAmount.</i>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Bid Distribution:</div>
            <span class='badge badge-blue' style='font-size:10px;'>Selective Rates</span>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Property &amp; Flag Breakdown:</div>
            <div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Revised Non-Commercial</span><span><b>1,328</b> ($7,788,659)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Commercial</span><span><b>31</b> ($679,386)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Removed – Full Inst Under $3,000</span><span><b>88</b> ($165,584)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>40 – Residential</span><span><b>1,244</b> ($7,286,129)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>50</span><span><b>3</b> ($27,087)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>11 – Farm</span><span><b>59</b> ($455,087)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>21 – Farmland</span><span><b>22</b> ($20,356)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>60 – Commercial</span><span><b>18</b> ($524,644)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>70</span><span><b>13</b> ($154,742)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>2024 comment "Do Not Buy" (Non-Commercial)</span><span><b>3</b> ($20,093)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>2024 comment "Do Not Buy" (Commercial)</span><span><b>0</b> ($0)</span></div>
          </div>
          <div style='margin-top:6px;'><div style='font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;'>Stan's Key Tags:</div><span class='badge badge-purple' style='font-size:9.5px;'>Ok to Buy: <b>934</b></span> <span class='badge badge-purple' style='font-size:9.5px;'>Ok To Buy-noMort/1inst: <b>372</b></span> <span class='badge badge-purple' style='font-size:9.5px;'>Farm: <b>22</b></span></div>
        </div>
        
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:16px; border-top:3px solid #8b5cf6;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h4 style="margin:0; font-size:14px; color:#8b5cf6; font-weight:800;">Will County Production Strategy</h4>
            <span class="badge badge-green" style="font-size:10px;">1,496 Kept</span>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-bottom:10px; line-height:1.4;">
            <b>Stan's Rule:</b> <i>Removed: certs under $3,000 where both installments are delinquent (OneInstllmt = FALSE). Commercial = ClassCode "0060 Commercial" and "0080 Industrial". Cert amount = Total-amount-owed.</i>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Bid Distribution:</div>
            <span class='badge badge-blue' style='font-size:10px;'>3%: <b>12</b></span>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Property &amp; Flag Breakdown:</div>
            <div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Revised Non-Commercial</span><span><b>1,442</b> ($9,284,074)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Commercial</span><span><b>50</b> ($1,203,089)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Removed – Full Inst Under $3,000</span><span><b>82</b> ($152,209)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>0040 Residential</span><span><b>1,393</b> ($9,070,807)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>0011 Farm Land with Buildings</span><span><b>31</b> ($186,837)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>0021 Farm Land without Buildings</span><span><b>18</b> ($26,429)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>0060 Commercial</span><span><b>40</b> ($1,110,791)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>0080 Industrial</span><span><b>10</b> ($92,299)</span></div><div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>Redlined comments (Steger / Univ Park / Park Forest)</span><span><b>10</b> ($52,349)</span></div>
          </div>
          <div style='margin-top:6px;'><div style='font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;'>Stan's Key Tags:</div><span class='badge badge-purple' style='font-size:9.5px;'>Do Not Buy-Steger tRedlined: <b>5</b></span> <span class='badge badge-purple' style='font-size:9.5px;'>Do Not Buy-UnivParkRedlined: <b>3</b></span> <span class='badge badge-purple' style='font-size:9.5px;'>Redlined-Park Forest: <b>2</b></span></div>
        </div>
        
        </div>
      </div>

      <!-- TAB 3: 133 PRIME COMMERCIAL TARGETS TABLE -->
      <div id="stanPortalTabComm" style="display: none; padding: 14px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
          <div>
            <span style="font-size: 13px; font-weight: 800; color: #fff;">🏢 Stan's 133 Commercial &amp; Industrial War Room Portfolio</span>
            <span style="font-size: 11px; color: var(--text-muted); margin-left: 8px;">Total Capital: <b>$5,045,679</b> &middot; Average Ticket: <b>$37,937 / cert</b></span>
          </div>
          <div style="font-size: 11px; color: var(--text-muted);">
            Includes Stan's exact underwriting comments (AMC, hotel, strip center, skilled nursing home)
          </div>
        </div>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>County</th>
                <th>PIN</th>
                <th>Business / Property Name &amp; Address</th>
                <th class="right">Tax Due</th>
                <th class="right">Stan Bid</th>
                <th class="right">Bldg/Land Ratio</th>
                <th>Flags</th>
              </tr>
            </thead>
            <tbody>

            <tr>
              <td><b style="color:var(--accent);">Lake</b></td>
              <td><code style="font-size:11px; font-weight:700;">15-35-402-125</code></td>
              <td>
                <b>BRI 1862 RIVERWALK, LLC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">2100 E LAKE COOK RD (BUFFALO GROVE)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$724,500.53</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">7%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">41.8x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--accent);">Lake</b></td>
              <td><code style="font-size:11px; font-weight:700;">07-25-308-009</code></td>
              <td>
                <b>FOUNTAIN SQUARE HOSPITALITY INC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">400 LAKEHURST RD (WAUKEGAN)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$345,151.86</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">6%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">3.4x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">23-15-02-400-015-0000</code></td>
              <td>
                <b>ST JAMES PROPERTY LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>skilled nursing home</span>
                <div style="font-size:10.5px; color:var(--text-muted);">1251 E RICHTON RD, CRETE IL 60417 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$289,375.15</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">12.9x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">03-05-200-031</code></td>
              <td>
                <b>IHP HOSPITALITY LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>hotel</span>
                <div style="font-size:10.5px; color:var(--text-muted);">1150 N ARLINGTON HTS (ITASCA)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$220,377.93</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">5%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">2.2x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--accent);">Lake</b></td>
              <td><code style="font-size:11px; font-weight:700;">08-21-211-018</code></td>
              <td>
                <b>LAKESIDE PHASED LLC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">200 JULIAN ST (WAUKEGAN)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$212,789.78</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">6%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">37.2x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">McHenry</b></td>
              <td><code style="font-size:11px; font-weight:700;">18-28-477-012</code></td>
              <td>
                <b>EP HSS LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>4% or higher - self storage</span>
                <div style="font-size:10.5px; color:var(--text-muted);"> ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$186,431.88</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">6.2x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">09-26-402-028</code></td>
              <td>
                <b>A1 HOSPITALITY</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>Hotel</span>
                <div style="font-size:10.5px; color:var(--text-muted);">7800 KINGERY HWY (WILLOWBROOK)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$174,927.81</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">5%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">3.3x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">07-12-204-005</code></td>
              <td>
                <b>BOBR GROUP LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>offfice buildings</span>
                <div style="font-size:10.5px; color:var(--text-muted);">1717 PARK ST (NAPERVILLE)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$154,032.31</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">5%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">2.7x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--accent);">Lake</b></td>
              <td><code style="font-size:11px; font-weight:700;">16-19-105-012</code></td>
              <td>
                <b>L2 KARMA FUND 1 LLC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">1000 LAKESIDE DR (BANNOCKBURN)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$128,252.20</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">5%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">0.2x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--accent);">Lake</b></td>
              <td><code style="font-size:11px; font-weight:700;">16-22-107-005</code></td>
              <td>
                <b>CVS HEALTH CORPORATION</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">2000 SKOKIE VALLEY RD (HIGHLAND PARK)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$119,722.38</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">5%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.0x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">19-09-01-204-004-0000</code></td>
              <td>
                <b>TINLEY PARK CHICAGO HOTELS LLC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">7255 183RD ST, TINLEY PARK IL 60477 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$116,311.41</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">7.7x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--accent);">Lake</b></td>
              <td><code style="font-size:11px; font-weight:700;">16-16-408-016</code></td>
              <td>
                <b>2396 SKOKIE VALLEY LLC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">2396 SKOKIE VALLEY RD (HIGHLAND PARK)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$111,117.25</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">5%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.3x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">07-01-04-410-060-0000</code></td>
              <td>
                <b>NATIONAL RETAIL PROPERTIES LP</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>AMC</span>
                <div style="font-size:10.5px; color:var(--text-muted);">2815 SHOWPLACE DR, NAPERVILLE IL 60564 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$74,757.59</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">0.6x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> <span class='badge badge-purple' style='font-size:9px;'>2nd Inst Only</span></td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">02-02-317-002</code></td>
              <td>
                <b>MILLION WAYS SERIES LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>strip center</span>
                <div style="font-size:10.5px; color:var(--text-muted);">610 E IRVING PARK RD (ROSELLE)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$71,869.85</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">2.6x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--accent);">Lake</b></td>
              <td><code style="font-size:11px; font-weight:700;">15-34-309-002</code></td>
              <td>
                <b>100 LEXINGTON PROPERTIES LLC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">100 LEXINGTON DR (BUFFALO GROVE)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$70,473.13</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">3.5x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">06-19-305-006</code></td>
              <td>
                <b>DM EQUITIES LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>office</span>
                <div style="font-size:10.5px; color:var(--text-muted);">555 WATERS EDGE (LOMBARD)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$69,534.80</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">2.3x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">12-02-17-102-029-0000</code></td>
              <td>
                <b>RB PROPERTY INVESTMENTS LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>cannabis building</span>
                <div style="font-size:10.5px; color:var(--text-muted);">190 S WEBER RD, BOLINGBROOK IL 60490 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$67,242.41</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.4x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">11-04-08-304-006-0000</code></td>
              <td>
                <b>SENIOR SERVICES CTR WILL CNTY</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">349 S WEBER RD, ROMEOVILLE IL 60446 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$66,136.45</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">0.7x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">McHenry</b></td>
              <td><code style="font-size:11px; font-weight:700;">09-26-100-046</code></td>
              <td>
                <b>LASALLE NATL BK TR 131445</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>4% or higher</span>
                <div style="font-size:10.5px; color:var(--text-muted);">1701 N RICHMOND RD (MCHENRY)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$56,551.20</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.2x</td>
              <td> <span class='badge badge-purple' style='font-size:9px;'>2nd Inst Only</span></td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">06-30-407-009</code></td>
              <td>
                <b>1430 BRANDING DG LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>office 1/2 installment</span>
                <div style="font-size:10.5px; color:var(--text-muted);">1430 BRANDING AVE (DOWNERS GROVE)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$50,579.30</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.1x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> <span class='badge badge-purple' style='font-size:9px;'>2nd Inst Only</span></td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">McHenry</b></td>
              <td><code style="font-size:11px; font-weight:700;">13-25-101-002</code></td>
              <td>
                <b>COACHING KIDS INC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>3% or higher</span>
                <div style="font-size:10.5px; color:var(--text-muted);">1310 RIDGEFIELD RD (CRYSTAL LAKE)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$49,639.00</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">5.5x</td>
              <td> <span class='badge badge-purple' style='font-size:9px;'>2nd Inst Only</span></td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">05-06-15-203-006-0000</code></td>
              <td>
                <b>SPECIALTY PROJECTS INC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>storage</span>
                <div style="font-size:10.5px; color:var(--text-muted);">201 MCDONALD AVE UNIT A, JOLIET IL 60431 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$49,003.67</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">4.2x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">09-04-403-001</code></td>
              <td>
                <b>TF PORTFOLIO I LLC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">19-31 W OGDEN AVE (WESTMONT)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$47,609.57</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.5x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--accent);">Lake</b></td>
              <td><code style="font-size:11px; font-weight:700;">15-21-405-007</code></td>
              <td>
                <b>REALTY INCOME U S CORE PLUS 3 LP</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">675 HEATHROW DR (LINCOLNSHIRE)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$44,493.56</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">4.3x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">11-04-23-317-009-0000</code></td>
              <td>
                <b>MADHUNT LLC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">110 W 10TH ST, LOCKPORT IL 60441 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$42,553.46</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">4%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">10.6x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">McHenry</b></td>
              <td><code style="font-size:11px; font-weight:700;">09-09-451-009</code></td>
              <td>
                <b>SUHR ENT INC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>3% or higher</span>
                <div style="font-size:10.5px; color:var(--text-muted);">5418 BUSINESS PKWY (RINGWOOD)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$39,247.05</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">9.6x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> <span class='badge badge-purple' style='font-size:9px;'>2nd Inst Only</span></td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">16-05-11-401-004-0000</code></td>
              <td>
                <b>GARCIA ANTONIO LIVING TRUST</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>restaurant</span>
                <div style="font-size:10.5px; color:var(--text-muted);">14853 S FOUNDERS XING, HOMER GLEN IL 60491 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$36,103.75</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.4x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">12-02-15-402-013-0000</code></td>
              <td>
                <b>ELISKA HOSPITALITY LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>motel</span>
                <div style="font-size:10.5px; color:var(--text-muted);">175 REMINGTON BLVD, BOLINGBROOK IL 60440 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$35,745.79</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.3x</td>
              <td> <span class='badge badge-purple' style='font-size:9px;'>2nd Inst Only</span></td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">07-13-436-016</code></td>
              <td>
                <b>48 WEST CHICAGO LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>restaurant</span>
                <div style="font-size:10.5px; color:var(--text-muted);">36-50 W CHICAGO AVE (NAPERVILLE)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$33,686.70</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">7.0x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">06-08-100-009</code></td>
              <td>
                <b>MILLION WAYS SERIES LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>apts</span>
                <div style="font-size:10.5px; color:var(--text-muted);">9 N MAIN ST (LOMBARD)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$32,998.22</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">10.2x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">06-03-04-201-046-0000</code></td>
              <td>
                <b>RT 59 OPERATIONS INC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>autospa</span>
                <div style="font-size:10.5px; color:var(--text-muted);">24037 W 135TH ST, PLAINFIELD IL 60544 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$32,241.82</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.5x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">06-03-32-208-084-0000</code></td>
              <td>
                <b>ZENITH HOLDINGS LTD</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>dialysis</span>
                <div style="font-size:10.5px; color:var(--text-muted);">2320 MICHAS DR, PLAINFIELD IL 60586 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$31,956.36</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">5.6x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            <tr>
              <td><b style="color:var(--accent);">Lake</b></td>
              <td><code style="font-size:11px; font-weight:700;">11-28-411-006</code></td>
              <td>
                <b>BRADFORD LANDINGS SOUTH 6 LLC</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">1680 N MILWAUKEE AVE (VERNON HILLS)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$31,867.56</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.4x</td>
              <td> </td>
            </tr>
            <tr>
              <td><b style="color:var(--purple);">Will</b></td>
              <td><code style="font-size:11px; font-weight:700;">06-03-09-302-056-0000</code></td>
              <td>
                <b>LIGHTHOUSE ACADEMY PLAINFIELD</b> 
                <div style="font-size:10.5px; color:var(--text-muted);">14957 S VAN DYKE RD, PLAINFIELD IL 60544 ()</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$28,779.49</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--success); font-weight:700;">13.5x</td>
              <td> <span class='badge badge-purple' style='font-size:9px;'>2nd Inst Only</span></td>
            </tr>
            <tr>
              <td><b style="color:var(--success);">DuPage</b></td>
              <td><code style="font-size:11px; font-weight:700;">07-10-105-013</code></td>
              <td>
                <b>PANERA LLC</b> <span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>panera</span>
                <div style="font-size:10.5px; color:var(--text-muted);">1620 N ROUTE 59 (NAPERVILLE)</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">$28,553.01</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">3%</span></td>
              <td class="right" style="color:var(--warn); font-weight:700;">1.1x</td>
              <td><span class='badge badge-green' style='font-size:9px;'>No Mort</span> </td>
            </tr>
            </tbody>
          </table>
        </div>
        <div style="margin-top: 8px; font-size: 11px; color: var(--text-muted); text-align: right;">
          <i>Showing top 35 commercial items sorted by dollar amount. Full 133 items available in Stan's spreadsheets.</i>
        </div>
      </div>

      <!-- TAB 4: STAN'S REDLINE RULES & EXCLUSIONS -->
      <div id="stanPortalTabRedline" style="display: none; padding: 14px 20px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-bottom: 14px;">
          <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 12px; font-weight: 800; color: var(--danger);">🚫 Lake County: North Chicago Redline</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">37 Certs &middot; $185,773</div>
            <div style="font-size: 11px; color: var(--text-muted);">Flagged: <code>"Do Not Buy - Redlined North Chgo"</code>. Severely distressed housing stock and chronic non-redemption risk.</div>
          </div>

          <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 12px; font-weight: 800; color: var(--warn);">⚠️ DuPage County: Open Prior Sold Taxes</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">8 Certs &middot; $57,415</div>
            <div style="font-size: 11px; color: var(--text-muted);">Flagged: <code>"DNB - Open Sold Taxes"</code>. Prior unredeemed certificate sales that jeopardize senior lien priority.</div>
          </div>

          <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 12px; font-weight: 800; color: var(--danger);">🚫 Will County: South Suburban Redline</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">10 Certs &middot; $52,349</div>
            <div style="font-size: 11px; color: var(--text-muted);">Flagged in Steger, University Park, and Park Forest. Zero commercial viability and title extinction risks.</div>
          </div>

          <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 12px; font-weight: 800; color: var(--accent);">🛡️ Total Capital Protected Across 4 Counties</div>
            <div style="font-size: 20px; font-weight: 800; color: var(--success); margin: 4px 0;">58 Certs &middot; $315,630</div>
            <div style="font-size: 11px; color: var(--text-muted);">Stan's proprietary exclusions prevented Jennings from trapping $315k into non-redeeming dead-end assets.</div>
          </div>
        </div>
      </div>

      <!-- TAB 5: KANE 2026 LIVE BUYS BENCHMARK -->
      <div id="stanPortalTabKane" style="display: none; padding: 14px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
          <div>
            <span style="font-size: 13px; font-weight: 800; color: #fff;">💎 2026 Kane County Auction Results — Diamond Quest Realty Buys</span>
            <span style="font-size: 11px; color: var(--text-muted); margin-left: 8px;">Executed Oct 27, 2026 &middot; 8 Certificates &middot; <b>$86,467 Capital Deployed</b></span>
          </div>
          <div style="font-size: 11px; color: var(--success); font-weight: 700;">
            100% Won at 5.0% - 7.0% Bid Rates
          </div>
        </div>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>PIN</th>
                <th>Taxpayer Name &amp; Site Address</th>
                <th class="right">Total Due</th>
                <th class="right">Winning Bid</th>
                <th class="right">Assessed Bldg</th>
                <th>Entity</th>
              </tr>
            </thead>
            <tbody>

        <tr>
          <td><code style="font-weight:700;">08-13-427-008</code></td>
          <td><b>BRINGAS, BRAULIO REVOC TR</b><div style="font-size:10.5px; color:var(--text-muted);">39W240 LONGMEADOW LN, ST CHARLES</div></td>
          <td class="right" style="font-weight:800; color:var(--success);">$16,176.13</td>
          <td class="right"><span class="badge badge-green" style="font-weight:800;">5%</span></td>
          <td class="right">$444,179</td>
          <td><span class="badge badge-purple" style="font-size:9px;">Diamond Quest (180)</span></td>
        </tr>
        
        <tr>
          <td><code style="font-weight:700;">09-04-302-001</code></td>
          <td><b>IZZO, THOMAS & TAYA</b><div style="font-size:10.5px; color:var(--text-muted);">7N475 HAMPTON DR, ST CHARLES</div></td>
          <td class="right" style="font-weight:800; color:var(--success);">$11,317.40</td>
          <td class="right"><span class="badge badge-green" style="font-weight:800;">5%</span></td>
          <td class="right">$273,503</td>
          <td><span class="badge badge-purple" style="font-size:9px;">Diamond Quest (180)</span></td>
        </tr>
        
        <tr>
          <td><code style="font-weight:700;">09-12-400-046</code></td>
          <td><b>HOLTZMAN, RICHARD & KATHY</b><div style="font-size:10.5px; color:var(--text-muted);">33W179 SURREY RD, WAYNE</div></td>
          <td class="right" style="font-weight:800; color:var(--success);">$10,093.09</td>
          <td class="right"><span class="badge badge-green" style="font-weight:800;">5%</span></td>
          <td class="right">$139,219</td>
          <td><span class="badge badge-purple" style="font-size:9px;">Diamond Quest (180)</span></td>
        </tr>
        
        <tr>
          <td><code style="font-weight:700;">09-24-150-016</code></td>
          <td><b>SCHUMACHER, BRAD G</b><div style="font-size:10.5px; color:var(--text-muted);">2504 ROYAL LYTHAM DR, ST CHARLES</div></td>
          <td class="right" style="font-weight:800; color:var(--success);">$11,919.11</td>
          <td class="right"><span class="badge badge-green" style="font-weight:800;">5%</span></td>
          <td class="right">$259,905</td>
          <td><span class="badge badge-purple" style="font-size:9px;">Diamond Quest (180)</span></td>
        </tr>
        
        <tr>
          <td><code style="font-weight:700;">10-22-100-001</code></td>
          <td><b>FLINT, G NADINE TR</b><div style="font-size:10.5px; color:var(--text-muted);">FARM PARCEL, KANE COUNTY</div></td>
          <td class="right" style="font-weight:800; color:var(--success);">$3,558.68</td>
          <td class="right"><span class="badge badge-green" style="font-weight:800;">7%</span></td>
          <td class="right">$32,124</td>
          <td><span class="badge badge-purple" style="font-size:9px;">Diamond Quest (180)</span></td>
        </tr>
        
        <tr>
          <td><code style="font-weight:700;">11-13-206-008</code></td>
          <td><b>BECKERMAN, BRETT</b><div style="font-size:10.5px; color:var(--text-muted);">0S140 N MATHEWSON LN, GENEVA</div></td>
          <td class="right" style="font-weight:800; color:var(--success);">$11,031.04</td>
          <td class="right"><span class="badge badge-green" style="font-weight:800;">5%</span></td>
          <td class="right">$238,236</td>
          <td><span class="badge badge-purple" style="font-size:9px;">Diamond Quest (180)</span></td>
        </tr>
        
        <tr>
          <td><code style="font-weight:700;">11-13-300-016</code></td>
          <td><b>RITSCHDORFF, MICHAEL IRREVOC TR</b><div style="font-size:10.5px; color:var(--text-muted);">39W796 FABYAN PKWY, ELBURN</div></td>
          <td class="right" style="font-weight:800; color:var(--success);">$11,162.44</td>
          <td class="right"><span class="badge badge-green" style="font-weight:800;">5%</span></td>
          <td class="right">$228,694</td>
          <td><span class="badge badge-purple" style="font-size:9px;">Diamond Quest (180)</span></td>
        </tr>
        
        <tr>
          <td><code style="font-weight:700;">12-31-173-014</code></td>
          <td><b>GUERRERO, H & LOPEZ, CLAUDIA</b><div style="font-size:10.5px; color:var(--text-muted);">960 N DEERPATH RD, NORTH AURORA</div></td>
          <td class="right" style="font-weight:800; color:var(--success);">$11,208.90</td>
          <td class="right"><span class="badge badge-green" style="font-weight:800;">5%</span></td>
          <td class="right">$277,924</td>
          <td><span class="badge badge-purple" style="font-size:9px;">Diamond Quest (180)</span></td>
        </tr>
        
            </tbody>
          </table>
        </div>
        <div style="margin-top: 8px; font-size: 11px; color: var(--text-muted);">
          📌 <i>From Stan's Tuesday email to Jay: "Below are the 8 items we bought. They look fine. No mistakes." Confirms Jennings cleared 5.0% bids on high-equity St. Charles &amp; Geneva residential parcels.</i>
        </div>
      </div>

      <!-- Deep Analysis Commentary -->
      <div style="background: rgba(0, 0, 0, 0.25); border-top: 1px solid var(--border); padding: 14px 20px; font-size: 11.5px; line-height: 1.6; color: var(--text-muted);">
        <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">🔍 Complete Strategic Synthesis from Stan's 5 Excel Spreadsheets:</div>
        <div>1. <b>The &lt;$3,000 Filter Rule:</b> Stan deliberately removes certs under $3,000 where both installments are delinquent. This cut <b>336 certs ($658,606)</b> across the 4 collar counties, preserving 98.5% of deployable capital while avoiding low-margin title/servicing overhead.</div>
        <div>2. <b>Commercial High-Yield Focus:</b> Commercial &amp; industrial certs account for only 2.3% of certificate count (133 certs) but generate <b>12.0% of all capital ($5.05M)</b> with an average ticket of <b>$37,937</b>. These represent Jennings' primary profit centers (hotels in Itasca, shopping centers in Roselle, AMC Naperville).</div>
        <div>3. <b>Why Volume Bidding is Required:</b> Last year Jennings won $13.54M out of $42.13M bid (~32% clearance rate). Bidding aggressively on $42M+ across all 4 counties is essential to ensure Jennings deploys its full $5.0M - $6.5M capital allocation target against Bridge and Bass.</div>
      </div>
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

        <!-- VISUAL LAKE COUNTY REGION HEATMAP (GEOGRAPHIC GRID) -->
        <div style="margin: 14px 0 18px 0; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: 16px; overflow-x: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <div style="font-size: 13px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 8px;">
                    <span>🗺️ Lake County Geographic Region Heatmap (North to South, West to East Coast)</span>
                    <span class="badge badge-purple" style="font-size: 9.5px; font-weight: 800;">Interactive 1-Tap Filter</span>
                </div>
                <div style="display: flex; gap: 10px; font-size: 10.5px; align-items: center;">
                    <span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 9px; height: 9px; border-radius: 2px; background: #10b981;"></span> <b>Tier 1</b> (&gt;96% Ultra-Safe)</span>
                    <span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 9px; height: 9px; border-radius: 2px; background: #3b82f6;"></span> <b>Tier 2</b> (92%-95% Strong)</span>
                    <span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 9px; height: 9px; border-radius: 2px; background: #ef4444;"></span> <b>Tier 3</b> (&lt;91% Water Lien Risk)</span>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr) 55px; gap: 8px; min-width: 680px;">
                <!-- ROW 1: NORTH TIER (WISCONSIN BORDER) -->
                <!-- [04] Antioch -->
                <div onclick="selectTownshipFilter('antioch')" style="cursor: pointer; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 6px; padding: 10px 12px; transition: transform 0.15s, border-color 0.15s;" onmouseover="this.style.borderColor='#3b82f6'; this.style.transform='scale(1.02)';" onmouseout="this.style.borderColor='rgba(59, 130, 246, 0.35)'; this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">[02 / 04] ANTIOCH</span>
                        <span class="badge badge-blue" style="font-size: 8.5px; padding: 1px 4px;">93.8%</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Chain O'Lakes Resort</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$820k &middot; 138 certs</div>
                </div>

                <!-- [03] Newport -->
                <div onclick="selectTownshipFilter('all')" style="cursor: pointer; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 6px; padding: 10px 12px; transition: transform 0.15s, border-color 0.15s;" onmouseover="this.style.borderColor='#3b82f6'; this.style.transform='scale(1.02)';" onmouseout="this.style.borderColor='rgba(59, 130, 246, 0.35)'; this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">[03] NEWPORT</span>
                        <span class="badge badge-blue" style="font-size: 8.5px; padding: 1px 4px;">94.1%</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Old Mill Creek Rural</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$340k &middot; 42 certs</div>
                </div>

                <!-- [01] Benton -->
                <div onclick="selectTownshipFilter('zion')" style="cursor: pointer; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 6px; padding: 10px 12px; transition: transform 0.15s, border-color 0.15s;" onmouseover="this.style.borderColor='#3b82f6'; this.style.transform='scale(1.02)';" onmouseout="this.style.borderColor='rgba(59, 130, 246, 0.35)'; this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">[01] BENTON</span>
                        <span class="badge badge-blue" style="font-size: 8.5px; padding: 1px 4px;">92.8%</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Beach Park Suburb</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$912k &middot; 186 certs</div>
                </div>

                <!-- [02] Zion -->
                <div onclick="selectTownshipFilter('zion')" style="cursor: pointer; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 6px; padding: 10px 12px; transition: transform 0.15s, border-color 0.15s;" onmouseover="this.style.borderColor='#3b82f6'; this.style.transform='scale(1.02)';" onmouseout="this.style.borderColor='rgba(59, 130, 246, 0.35)'; this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">[02] ZION</span>
                        <span class="badge badge-blue" style="font-size: 8.5px; padding: 1px 4px;">91.2%</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Zion Coastal City</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$1.14M &middot; 245 certs</div>
                </div>

                <!-- LAKE MICHIGAN STRIP (ROW 1-4 SPAN) -->
                <div style="grid-row: span 4; background: linear-gradient(180deg, rgba(30, 58, 138, 0.5), rgba(14, 116, 144, 0.6)); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 6px; display: flex; align-items: center; justify-content: center; writing-mode: vertical-rl; text-orientation: mixed; font-size: 11px; font-weight: 800; color: #38bdf8; letter-spacing: 2px; text-shadow: 0 0 8px rgba(56,189,248,0.5);">
                    🌊 LAKE MICHIGAN (EAST COAST)
                </div>

                <!-- ROW 2: UPPER-MID TIER -->
                <!-- [06] Grant -->
                <div onclick="selectTownshipFilter('antioch')" style="cursor: pointer; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 6px; padding: 10px 12px; transition: transform 0.15s, border-color 0.15s;" onmouseover="this.style.borderColor='#3b82f6'; this.style.transform='scale(1.02)';" onmouseout="this.style.borderColor='rgba(59, 130, 246, 0.35)'; this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">[05 / 06] GRANT / VILLA</span>
                        <span class="badge badge-blue" style="font-size: 8.5px; padding: 1px 4px;">93.4%</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Fox Lake / Ingleside</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$1.42M &middot; 210 certs</div>
                </div>

                <!-- [07] Avon / Round Lake -->
                <div onclick="selectTownshipFilter('all')" style="cursor: pointer; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 6px; padding: 10px 12px; transition: transform 0.15s, border-color 0.15s;" onmouseover="this.style.borderColor='#3b82f6'; this.style.transform='scale(1.02)';" onmouseout="this.style.borderColor='rgba(59, 130, 246, 0.35)'; this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">[06 / 07] AVON</span>
                        <span class="badge badge-blue" style="font-size: 8.5px; padding: 1px 4px;">92.4%</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Round Lake Beach</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$3.18M &middot; 482 certs (Vol)</div>
                </div>

                <!-- [08] Warren / Gurnee -->
                <div onclick="selectTownshipFilter('gurnee')" style="cursor: pointer; background: rgba(16, 185, 129, 0.1); border: 2px solid #10b981; border-radius: 6px; padding: 10px 12px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.15); transition: transform 0.15s;" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #34d399;">[07 / 08] WARREN / GURNEE</span>
                        <span class="badge badge-green" style="font-size: 8.5px; padding: 1px 4px;">94.7% Tier 1</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Gurnee Mills Corridor</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$2.89M &middot; 385 certs</div>
                </div>

                <!-- [09] Waukegan & North Chicago (JAY EXCLUSION ZONE) -->
                <div style="pointer-events: none; opacity: 0.45; background: repeating-linear-gradient(45deg, rgba(0,0,0,0.2), rgba(0,0,0,0.2) 10px, rgba(255,255,255,0.02) 10px, rgba(255,255,255,0.02) 20px); border: 2px dashed rgba(255,255,255,0.2); border-radius: 6px; padding: 10px 12px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                    <div style="font-size: 10.5px; font-weight: 900; color: #94a3b8; letter-spacing: 0.5px;">🚫 JAY EXCLUSION ZONE</div>
                    <div style="font-size: 9px; color: #64748b; margin-top: 4px; font-weight: 700;">Waukegan / North Chicago<br/>Auto-Purged (Zero Bids)</div>
                </div>

                <!-- ROW 3: CENTRAL HIGH-EQUITY TIER -->
                <!-- [13] Wauconda -->
                <div onclick="selectTownshipFilter('all')" style="cursor: pointer; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 6px; padding: 10px 12px; transition: transform 0.15s, border-color 0.15s;" onmouseover="this.style.borderColor='#3b82f6'; this.style.transform='scale(1.02)';" onmouseout="this.style.borderColor='rgba(59, 130, 246, 0.35)'; this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">[13] WAUCONDA</span>
                        <span class="badge badge-blue" style="font-size: 8.5px; padding: 1px 4px;">94.2%</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Bangs Lake Suburban</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$1.10M &middot; 165 certs</div>
                </div>

                <!-- [12] Fremont / Mundelein -->
                <div onclick="selectTownshipFilter('all')" style="cursor: pointer; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 6px; padding: 10px 12px; transition: transform 0.15s, border-color 0.15s;" onmouseover="this.style.borderColor='#10b981'; this.style.transform='scale(1.02)';" onmouseout="this.style.borderColor='rgba(16, 185, 129, 0.4)'; this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #34d399;">[10 / 12] FREMONT</span>
                        <span class="badge badge-green" style="font-size: 8.5px; padding: 1px 4px;">96.2% Tier 1</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Mundelein Central</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$2.39M &middot; 356 certs</div>
                </div>

                <!-- [11] Libertyville -->
                <div onclick="selectTownshipFilter('libertyville')" style="cursor: pointer; background: rgba(16, 185, 129, 0.12); border: 2px solid #10b981; border-radius: 6px; padding: 10px 12px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.15); transition: transform 0.15s;" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #34d399;">[11] LIBERTYVILLE</span>
                        <span class="badge badge-green" style="font-size: 8.5px; padding: 1px 4px;">96.5% Tier 1</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">High Corporate Equity</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$2.97M &middot; 496 certs</div>
                </div>

                <!-- [10] Shields / Lake Forest -->
                <div onclick="selectTownshipFilter('all')" style="cursor: pointer; background: rgba(16, 185, 129, 0.12); border: 2px solid #10b981; border-radius: 6px; padding: 10px 12px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.15); transition: transform 0.15s;" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #34d399;">[12 / 10] SHIELDS</span>
                        <span class="badge badge-green" style="font-size: 8.5px; padding: 1px 4px;">97.1% Tier 1</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Lake Forest / Bluff</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$2.48M &middot; 222 certs</div>
                </div>

                <!-- ROW 4: SOUTH LUXURY TIER (COOK COUNTY BORDER) -->
                <!-- [14] Cuba / Barrington -->
                <div onclick="selectTownshipFilter('all')" style="cursor: pointer; background: rgba(16, 185, 129, 0.1); border: 1.5px solid #10b981; border-radius: 6px; padding: 10px 12px; transition: transform 0.15s;" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #34d399;">[13 / 14] CUBA</span>
                        <span class="badge badge-green" style="font-size: 8.5px; padding: 1px 4px;">96.8% Tier 1</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Barrington Luxury</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$1.89M &middot; 230 certs</div>
                </div>

                <!-- [15] Ela / Lake Zurich -->
                <div onclick="selectTownshipFilter('all')" style="cursor: pointer; background: rgba(16, 185, 129, 0.1); border: 1.5px solid #10b981; border-radius: 6px; padding: 10px 12px; transition: transform 0.15s;" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #34d399;">[14 / 15] ELA</span>
                        <span class="badge badge-green" style="font-size: 8.5px; padding: 1px 4px;">95.9% Tier 1</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Lake Zurich Suburban</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$3.79M &middot; 429 certs</div>
                </div>

                <!-- [16] Vernon / Buffalo Grove -->
                <div onclick="selectTownshipFilter('vernon')" style="cursor: pointer; background: rgba(16, 185, 129, 0.12); border: 2px solid #10b981; border-radius: 6px; padding: 10px 12px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.15); transition: transform 0.15s;" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #34d399;">[15 / 16] VERNON</span>
                        <span class="badge badge-green" style="font-size: 8.5px; padding: 1px 4px;">96.1% Tier 1</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Buffalo Grove / VH</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$5.24M &middot; 629 certs</div>
                </div>

                <!-- [18] Moraine / Highland Park -->
                <div onclick="selectTownshipFilter('highland park')" style="cursor: pointer; background: rgba(16, 185, 129, 0.15); border: 2px solid #10b981; border-radius: 6px; padding: 10px 12px; box-shadow: 0 0 12px rgba(16, 185, 129, 0.25); transition: transform 0.15s;" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #34d399;">[16 / 18] MORAINE ⭐</span>
                        <span class="badge badge-green" style="font-size: 8.5px; padding: 1px 4px;">97.3% Top Safe</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fff; margin-top: 3px;">Highland Park Luxury</div>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">$8.10M &middot; 708 certs</div>
                </div>
            </div>
            
            <div style="margin-top: 10px; font-size: 11px; color: var(--text-muted); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>🧭 <i>Orientation: North (Wisconsin) at top &middot; South (Cook Co border) at bottom &middot; Lake Michigan on right edge.</i></div>
                <div style="color: var(--accent); font-weight: 700;">💡 Pro-Tip: Click any township box above to instantly filter the parcel table below!</div>
            </div>
        </div>

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
          <option value="ultra95">🛡️ Ultra-Certain Only (&gt;=95% Redemption Score)</option>
          <option value="half" selected>⭐ 2nd Installment Only (268 Parcels · $5.12M)</option>
          <option value="all">All High-Yield ($10k+)</option>
          <option value="curated">Curated $2.0M Plan (55 Parcels)</option>
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
        <select id="lakeCautionFilter" class="filter-select" onchange="renderLakeTargetTable()" style="border-color:#ef4444; font-weight:700;">
          <option value="exclude" selected>🛡️ Jay Rule: Exclude Caution Areas (Auto-Purged)</option>
          <option value="include">⚠️ Show Caution Areas (North Chicago &amp; Waukegan Liens)</option>
        </select>
        <input type="text" id="lakeSearchInput" class="filter-input" onkeyup="renderLakeTargetTable()" placeholder="Search PIN, Taxpayer, Street Address, City, Township..." />
        <span id="lakeTargetCount" style="font-size:11px; color:var(--text-muted); margin-left:auto; font-weight:600;">Showing 0 parcels</span>
      </div>

      <!-- Screener Table -->
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th style="width:110px;">House / Building Photo</th>
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



  </div>


        <!-- 🏛️ THE THREE SYNDICATED BANK TAX CREDIT FACILITIES ($52.0M COMMITMENTS) -->
        <div class="table-wrapper" style="margin-top:20px; border:2px solid rgba(59,130,246,0.4); background:rgba(30,58,138,0.1);">
            <div class="table-header" style="background:rgba(59,130,246,0.2); padding:14px 20px;">
                <div>
                    <h3 style="margin:0; font-size:15px; font-weight:800; color:#93c5fd; display:flex; align-items:center; gap:8px;">
                        <span>🏦 Syndicated Bank Tax Credit Facilities &amp; Available Headroom</span>
                        <span class="badge badge-blue" style="font-size:10px; font-weight:800;">Official Bank Credit Agreement</span>
                    </h3>
                    <div style="font-size:11.5px; color:var(--text-muted); margin-top:3px;">
                        Verified from Jay's <i>Mortgage and Tax Line Summary</i>. Lenders advance <b>95% of all Certs and Posts</b> against tax lien collateral.
                    </div>
                </div>
                <div style="display:flex; gap:8px; align-items:center;">
                    <span class="badge badge-purple" style="font-size:11px; font-weight:800;">Total Lines: $52,000,000</span>
                    <span class="badge badge-green" style="font-size:11px; font-weight:800;">Available Headroom: $23,500,000</span>
                </div>
            </div>

            <!-- 4 Quick Debt Metrics -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; padding:12px 18px; background:rgba(0,0,0,0.15); border-bottom:1px solid var(--border);">
                <div>
                    <div style="font-size:10.5px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Total Tax Facilities</div>
                    <div style="font-size:18px; font-weight:800; color:#fff;">$52,000,000</div>
                    <div style="font-size:10.5px; color:var(--text-secondary);">Old Natl, Byline, 1st Chicago</div>
                </div>
                <div>
                    <div style="font-size:10.5px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Current Drawn</div>
                    <div style="font-size:18px; font-weight:800; color:var(--warn);">$28,500,000</div>
                    <div style="font-size:10.5px; color:var(--text-secondary);">54.8% Utilization</div>
                </div>
                <div>
                    <div style="font-size:10.5px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Dry Powder Headroom</div>
                    <div style="font-size:18px; font-weight:800; color:var(--success);">$23,500,000</div>
                    <div style="font-size:10.5px; color:var(--text-secondary);">Immediate borrowing capacity</div>
                </div>
                <div>
                    <div style="font-size:10.5px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Advance Rate &amp; Spread</div>
                    <div style="font-size:18px; font-weight:800; color:var(--accent);">95% / +552 bps</div>
                    <div style="font-size:10.5px; color:var(--text-secondary);">6.48% debt vs 12.0% statutory carry</div>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Bank Lender</th>
                        <th class="right">Total Facility</th>
                        <th class="right">Current Drawn</th>
                        <th class="right" style="color:var(--success);">Available Headroom</th>
                        <th class="right">Borrowing Rate</th>
                        <th>Advance Rate</th>
                        <th>Maturity Date</th>
                        <th>Key Bank Covenants &amp; Terms</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Byline Bank</b></td>
                        <td class="right" style="font-weight:700;">$17,000,000</td>
                        <td class="right">$5,000,000</td>
                        <td class="right" style="color:var(--success); font-weight:800; font-size:13px;">$12,000,000</td>
                        <td class="right"><span class="badge badge-green">6.82%</span></td>
                        <td>95% of certs &amp; posts (3.10% floor)</td>
                        <td><b>5/19/2028</b></td>
                        <td style="font-size:11px; color:var(--text-muted);">DSCR 1.00x &middot; $500k deposit &middot; BDT Assets $45M &middot; Guaranteed: BDT &amp; JRI</td>
                    </tr>
                    <tr>
                        <td><b>First Chicago Bank (FBHP)</b></td>
                        <td class="right" style="font-weight:700;">$15,000,000</td>
                        <td class="right">$6,300,000</td>
                        <td class="right" style="color:var(--success); font-weight:800; font-size:13px;">$8,700,000</td>
                        <td class="right"><span class="badge badge-green">6.32%</span></td>
                        <td>95% of certs &amp; posts (3.10% floor)</td>
                        <td><b>7/01/2027</b></td>
                        <td style="font-size:11px; color:var(--text-muted);">TNW: Tax Buyers $7.8M, JRI $15.0M &middot; $200k-$500k dep &middot; Guaranteed: BDT</td>
                    </tr>
                    <tr>
                        <td><b>Old National Bank (FMW)</b></td>
                        <td class="right" style="font-weight:700;">$20,000,000</td>
                        <td class="right" style="color:var(--warn); font-weight:700;">$17,200,000</td>
                        <td class="right" style="color:var(--success); font-weight:800; font-size:13px;">$2,800,000</td>
                        <td class="right"><span class="badge badge-green">6.32%</span></td>
                        <td>95% of certs &amp; posts</td>
                        <td><b style="color:#fbbf24;">2/28/2026</b></td>
                        <td style="font-size:11px; color:var(--text-muted);">DSCR 1.25x pre / 1.00x post &middot; All operating accts ($3.0M ave) &middot; TNW: JRI $5.0M</td>
                    </tr>
                    <tr style="font-weight:800; background:rgba(255,255,255,0.06);">
                        <td><span class="badge badge-purple" style="font-size:11px;">Total Tax Facilities</span></td>
                        <td class="right" style="font-size:14px;">$52,000,000</td>
                        <td class="right" style="color:var(--warn); font-size:14px;">$28,500,000</td>
                        <td class="right" style="color:var(--success); font-weight:900; font-size:15px;">$23,500,000</td>
                        <td class="right"><span class="badge badge-green" style="font-size:11px;">6.48% Wtd Avg</span></td>
                        <td><b style="color:var(--accent);">95% Advanced</b></td>
                        <td>2026 - 2028</td>
                        <td style="font-size:11px; color:var(--success); font-weight:700;">100% Covenant Compliant &middot; Full $6.5M Auction Spend Pre-Approved</td>
                    </tr>
                </tbody>
            </table>
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

function switchStanSubTab(prefix, tab) {{
    const tabs = ['rollup', 'deep', 'comm', 'redline', 'kane'];
    tabs.forEach(t => {{
        const pane = document.getElementById(prefix + 'Tab' + t.charAt(0).toUpperCase() + t.slice(1));
        const btn = document.getElementById(prefix + 'Btn' + t.charAt(0).toUpperCase() + t.slice(1));
        if (pane) pane.style.display = (t === tab) ? 'block' : 'none';
        if (btn) {{
            btn.className = (t === tab) ? 'btn btn-primary' : 'btn btn-outline';
        }}
    }});
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
    const cautionVal = document.getElementById('lakeCautionFilter') ? document.getElementById('lakeCautionFilter').value : 'exclude';
    const searchVal = document.getElementById('lakeSearchInput') ? document.getElementById('lakeSearchInput').value.toLowerCase().trim() : '';

    let dataset = (tierVal === 'curated' && lakePresaleData.curated_2m_portfolio)
        ? lakePresaleData.curated_2m_portfolio.parcels
        : lakePresaleData.top_targets;

    let filtered = dataset.filter(item => {{
        // Jay Caution Rule: Auto-purge North Chicago & Waukegan Water Lien Sections
        if (cautionVal === 'exclude') {{
            if (item.waukegan_redline) return false;
            if (item.city && item.city.toLowerCase().includes('north chicago')) return false;
            if (item.township && item.township.toLowerCase().includes('north chicago')) return false;
        }}

        if (tierVal === 'ultra95' && (!item.redemption_score || item.redemption_score < 95.0)) return false;
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



        const photoHtml = t.photo_url ? `
            <div style="position:relative; width:100px; height:68px; border-radius:6px; overflow:hidden; border:1px solid rgba(255,255,255,0.15); box-shadow:0 2px 6px rgba(0,0,0,0.4); background:#1e293b;">
                <a href="${{googleUrl}}" target="_blank" title="Click to open Google Maps Street View for this house">
                    <img src="${{t.photo_url}}" loading="lazy" style="width:100%; height:100%; object-fit:cover; transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1.0)'" alt="House Photo" />
                </a>
                <span style="position:absolute; bottom:2px; right:2px; background:rgba(0,0,0,0.7); color:#fff; font-size:8px; padding:1px 4px; border-radius:3px; font-weight:700;">🛰️ Aerial</span>
            </div>
        ` : `<div style="width:100px; height:68px; background:rgba(255,255,255,0.05); border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:10px; color:var(--text-muted);">No Photo</div>`;

        return `
        <tr>
            <td style="width:110px; padding:6px; vertical-align:middle;">
                ${{photoHtml}}
            </td>
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
                <span class="badge ${{t.redemption_score >= 95.0 ? 'badge-green' : 'badge-blue'}}" style="font-size:8.5px; margin-left:3px; font-weight:800;" title="Quantitative Algorithmic Score: Building/land ratio, equity, township safety, installment intent">⭐ ${{t.redemption_score || 95.0}}% Certainty</span>
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


function selectTownshipFilter(twp) {{
    const sel = document.getElementById('lakeTwpFilter');
    if (sel) {{
        sel.value = twp;
        renderLakeTargetTable();
        const screener = document.getElementById('secBody2');
        if (screener) {{
            screener.scrollIntoView({{ behavior: 'smooth' }});
        }}
    }}
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
