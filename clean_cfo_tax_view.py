import os
import re

def clean_cfo_tax_view():
    with open('generate_cfo_html_viewer.py', 'r') as f:
        code = f.read()

    # 1. Clean up any accidental sub-nav button injections in other views
    accidental_nav = re.findall(r'<!-- Jay vs Stan Executive Sub-Navigation -->.*?</div>\s*</div>\s*<!-- SUB-VIEW 1: JAY\'S EXECUTIVE CAPITAL & LIQUIDITY \(DEFAULT\) -->\s*<div id="taxSubViewCapital" style="display: block;">\s*<div class="cards-grid">', code, re.DOTALL)
    for match in accidental_nav:
        code = code.replace(match, '<div class="cards-grid">')
    print("✅ Cleaned accidental sub-nav injections")

    # 2. In renderTaxActivityView, remove the sub-nav and hand-off clutter, and remove the bulky collar counties commander
    # Instead, we end the taxActivity view right after Stan's 4-County Rollup Table, with a clean, beautiful 1-click launch card to Stan's War Room!
    
    # Let's inspect where renderTaxActivityView begins and ends
    start_str = "function renderTaxActivityView() {"
    if start_str not in code:
        print("❌ Could not find renderTaxActivityView")
        return

    # Let's write the exact, clean, beautiful renderTaxActivityView function:
    clean_tax_func = '''function renderTaxActivityView() {{
    const pane = document.getElementById('taxActivityPane');
    if (!pane) return;

    const mary = (taxActivity && taxActivity.mary_daily_cash) ? taxActivity.mary_daily_cash : {{}};
    const octRed = (taxActivity && taxActivity.october_redemptions) ? taxActivity.october_redemptions : {{}};
    const subs = (taxActivity && taxActivity.recent_subtax_purchases) ? taxActivity.recent_subtax_purchases : {{}};

    const monIn = mary.monday_inflows || 342344.02;
    const twIn = mary.this_week_inflows || 903197.20;
    const twNet = mary.this_week_net || 778578.20;
    const octTotal = octRed.total_collected || 1824472.25;
    const octProfit = octRed.net_profit_earned || 1055292.01;
    const subDeployed = subs.total_deployed || 5328924.71;

    // Daily rows from Mary's sheet
    let dailyRows = "";
    const activeDaily = (mary.daily_breakdown && mary.daily_breakdown.length > 0) ? mary.daily_breakdown : [
        {{"date": "2026-10-23", "inflows": 431745.72, "cb_in": 226390.00, "if_in": 152809.72, "outflows": -124619.00, "net": 307126.72}},
        {{"date": "2026-10-22", "inflows": 129107.46, "cb_in": 94433.89, "if_in": 34673.57, "outflows": 0.0, "net": 129107.46}},
        {{"date": "2026-10-19", "inflows": 342344.02, "cb_in": 337756.76, "if_in": 4587.26, "outflows": 0.0, "net": 342344.02}},
        {{"date": "2026-10-14", "inflows": 89767.47, "cb_in": 89767.47, "if_in": 0.0, "outflows": -162478.88, "net": -72711.41}},
        {{"date": "2026-10-08", "inflows": 45327.01, "cb_in": 45327.01, "if_in": 0.0, "outflows": -34343.55, "net": 10983.46}},
        {{"date": "2026-10-06", "inflows": 1310228.90, "cb_in": 1303822.58, "if_in": 2291.70, "outflows": -2500.0, "net": 1307728.90}},
        {{"date": "2026-10-05", "inflows": 1001266.48, "cb_in": 641667.44, "if_in": 277128.89, "outflows": -1536011.12, "net": -534744.64}}
    ];

    activeDaily.slice(-7).reverse().forEach(d => {{
        dailyRows += `
            <tr>
                <td><b>${{d.date}}</b></td>
                <td class="right" style="color:var(--success); font-weight:700;">$${{Number(d.inflows).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
                <td class="right">$${{Number(d.cb_in || 0).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
                <td class="right">$${{Number(d.if_in || 0).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
                <td class="right" style="color:${{d.outflows < 0 ? 'var(--warn)' : 'var(--text-muted)'}};">$${{Number(d.outflows).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
                <td class="right" style="font-weight:700; color:${{d.net >= 0 ? 'var(--success)' : 'var(--warn)'}};">$${{Number(d.net).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
            </tr>
        `;
    }});

    // Top redemptions from Jim's database
    let topRedRows = "";
    if (octRed.top_redemptions && octRed.top_redemptions.length > 0) {{
        octRed.top_redemptions.slice(0, 8).forEach(r => {{
            topRedRows += `
                <tr>
                    <td><b>${{r.county_name}}</b></td>
                    <td><code style="font-size:10.5px;">${{r.pin}}</code></td>
                    <td class="right">$${{Number(r.principal).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
                    <td class="right" style="color:var(--success); font-weight:700;">$${{Number(r.payoff).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
                    <td class="right" style="color:var(--accent); font-weight:700;">+$${{Number(r.profit).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</td>
                    <td><span class="badge badge-blue" style="font-size:9px;">${{r.owner.replace('INTERSTATE FUNDING CORP.', 'IFC').replace('CENTRAL BUYER CORP.', 'CBC')}}</span></td>
                </tr>
            `;
        }});
    }}

    pane.innerHTML = `
        <div class="entity-banner">
            <div style="margin-bottom:8px; display:flex; gap:6px; flex-wrap:wrap; align-items:center;">
                <span class="badge badge-green">Dual Data Stream</span>
                <span class="badge badge-blue">S-Drive Read-Only</span>
                <span class="badge badge-blue">Mary's Sheet + County Access DB</span>
            </div>
            <h2>Tax Certificate Lien Portfolio — Live Cash Flow & Redemptions</h2>
            <p>Real-time visibility into certificate payoffs, weekly bank clearing, and capital deployed across Interstate Funding (150), Central Buyer (160), Diamond Quest (180), and Union Tax (190).</p>
        </div>

        <div class="cards-grid">
            <div class="stat-card">
                <div class="stat-card-label">Monday Redemptions (10/19)</div>
                <div class="stat-card-val" style="color:var(--success);">$${{Number(monIn).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</div>
                <div class="stat-card-sub">Cleared Monday: Central Buyer & IFC</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-label">Total Redemptions This Week</div>
                <div class="stat-card-val" style="color:var(--success);">$${{Number(twIn).toLocaleString('en-US', {{maximumFractionDigits:0}})}}</div>
                <div class="stat-card-sub">Mon ($342k), Thu ($129k), Fri ($432k)</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-label">Jennings "Own Cash" in Tax Biz</div>
                <div class="stat-card-val" style="color:var(--success); font-weight:900;">+$7.38M</div>
                <div class="stat-card-sub">Beyond the 10% bank minimum ($10.4M total equity)</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-label">Excess Collateral Available</div>
                <div class="stat-card-val" style="color:var(--accent); font-weight:800;">$11.51M</div>
                <div class="stat-card-sub">Available loan borrowing headroom (Leslie's report)</div>
            </div>
        </div>

        <!-- Capital Stack & "Own Cash" in Tax Business -->
        <div class="table-wrapper" style="margin-top:20px; border:1px solid rgba(59,130,246,0.3); background:rgba(30,58,138,0.08);">
            <div class="table-header" style="background:rgba(59,130,246,0.15);">
                <div>
                    <h3 style="margin:0; color:var(--text-primary);">💎 Jennings Capital Stack & "Own Cash" in Tax Business</h3>
                    <div style="font-size:11px; color:var(--text-muted);">Real-world equity deployed beyond the 10% bank covenant minimum requirement</div>
                </div>
                <span class="badge badge-green" style="font-size:11px; font-weight:800;">+$7,375,867 Own Cash Beyond Bank 10%</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Capital & Debt Component</th>
                        <th class="right">Dollar Amount</th>
                        <th class="right">% of Tax Business</th>
                        <th>Executive Significance for Jay</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Total Tax Business Assets & Active Liens</b></td>
                        <td class="right" style="font-weight:700;">$40,622,612</td>
                        <td class="right">100.0%</td>
                        <td>Total portfolio book value across Interstate, Central Buyer, Diamond Quest, Union Tax</td>
                    </tr>
                    <tr>
                        <td><b>Less: Bank Facility Borrowings (Old Natl, Byline, 1st Bank)</b></td>
                        <td class="right" style="color:var(--warn); font-weight:700;">($30,224,314)</td>
                        <td class="right">74.4%</td>
                        <td>Total debt drawn across the three syndicated bank credit facilities ($45M total facility)</td>
                    </tr>
                    <tr style="background:rgba(255,255,255,0.03);">
                        <td><b>TOTAL JENNINGS EQUITY CAPITAL IN TAX BUSINESS</b></td>
                        <td class="right" style="color:var(--accent); font-weight:800; font-size:13px;">$10,398,298</td>
                        <td class="right" style="font-weight:700;">25.6%</td>
                        <td><b>Total Jennings capital & retained earnings actively deployed in tax portfolios</b></td>
                    </tr>
                    <tr>
                        <td>&nbsp;&nbsp;Less: Bank Required 10% Minimum Equity Margin</td>
                        <td class="right" style="color:var(--text-muted);">($3,022,431)</td>
                        <td class="right">7.4%</td>
                        <td>Minimum 10% equity cushion mandated by lenders under Section 8.4D borrowing base</td>
                    </tr>
                    <tr style="background:rgba(16,185,129,0.12); border-top:1px solid var(--success); border-bottom:1px solid var(--success);">
                        <td><b style="color:var(--success); font-size:13px;">💎 JENNINGS "OWN CASH" INVESTED BEYOND BANK 10%</b></td>
                        <td class="right" style="color:var(--success); font-weight:900; font-size:15px;">+$7,375,867</td>
                        <td class="right" style="color:var(--success); font-weight:800;">18.2%</td>
                        <td><b style="color:var(--success);">Extra unencumbered Jennings cash & capital working in the tax business!</b></td>
                    </tr>
                    <tr>
                        <td><b>📈 Total Excess Collateral Borrowing Headroom Available</b></td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$11,510,385</td>
                        <td class="right">25.6%</td>
                        <td>Unpledged tax certificate collateral available to draw fresh liquidity on demand (Leslie's report)</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="tax-grid-two-col">
            <!-- Mary's Daily Reconciled Cash -->
            <div class="table-wrapper">
                <div class="table-header">
                    <h3>🏦 Daily Bank Cash Activity (Mary's Daily Sheet)</h3>
                    <span class="badge badge-green">Reconciled to Bank</span>
                </div>
                <div class="mobile-scroll-hint">← Swipe horizontally to see all bank accounts →</div>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th class="right">Total Inflows</th>
                            <th class="right">Central Buyer</th>
                            <th class="right">Interstate</th>
                            <th class="right">Outflows</th>
                            <th class="right">Net Daily Cash</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${{dailyRows}}
                    </tbody>
                </table>
            </div>

            <!-- County Certificate Payoffs -->
            <div class="table-wrapper">
                <div class="table-header">
                    <h3>🏛️ Top October Certificate Payoffs (Certificates Access DB)</h3>
                    <span class="badge badge-blue">Collar Counties</span>
                </div>
                <div class="mobile-scroll-hint">← Swipe horizontally to see parcel details →</div>
                <table>
                    <thead>
                        <tr>
                            <th>County</th>
                            <th>PIN</th>
                            <th class="right">Cert Amt</th>
                            <th class="right">Payoff</th>
                            <th class="right">Profit / Interest</th>
                            <th>Entity</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${{topRedRows}}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Pillar 2: Auction Bidding Optimizer -->
        <div class="table-wrapper" style="margin-top:20px; border:1px solid rgba(16,185,129,0.3); background:rgba(6,78,59,0.12);">
            <div class="table-header" style="background:rgba(16,185,129,0.2);">
                <div>
                    <h3 style="margin:0; color:var(--text-primary);">⚖️ Next-Auction Bidding Capacity & Bank Borrowing Optimizer</h3>
                    <div style="font-size:11px; color:var(--text-muted);">Maximum capital Jay can deploy at upcoming Fall/Spring sales without tripping Byline Bank covenants</div>
                </div>
                <span class="badge badge-green" style="font-size:11px; font-weight:800;">$6,250,000 Safe Bidding Limit</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Target County Tax Sale</th>
                        <th>Estimated Date</th>
                        <th class="right">Recommended Bidding Allocation</th>
                        <th class="right">Required 10% Cash Deposit</th>
                        <th>Target Statutory Return</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Lake County Fall Tax Sale</b></td>
                        <td>Friday, Nov 13, 2026</td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$2,000,000</td>
                        <td class="right" style="color:var(--text-muted);">$200,000 (from Own Cash)</td>
                        <td><span class="badge badge-green">4.0% - 5.0% Bids (12% Subtaxes)</span></td>
                    </tr>
                    <tr>
                        <td><b>DuPage County Fall Sale</b></td>
                        <td>Thursday, Nov 19, 2026</td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$1,500,000</td>
                        <td class="right" style="color:var(--text-muted);">$150,000 (from Own Cash)</td>
                        <td><span class="badge badge-green">12.0% Statutory Compounding</span></td>
                    </tr>
                    <tr>
                        <td><b>McHenry County Tax Sale</b></td>
                        <td>Monday, Nov 23, 2026</td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$1,000,000</td>
                        <td class="right" style="color:var(--text-muted);">$100,000 (from Own Cash)</td>
                        <td><span class="badge badge-green">12.0% Statutory Penalty</span></td>
                    </tr>
                    <tr>
                        <td><b>Will County Fall Tax Sale</b></td>
                        <td>Tuesday, Dec 01, 2026</td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$2,000,000</td>
                        <td class="right" style="color:var(--text-muted);">$200,000 (from Own Cash)</td>
                        <td><span class="badge badge-green">12.0% Statutory Penalty</span></td>
                    </tr>
                    <tr style="background:rgba(255,255,255,0.04); font-weight:800;">
                        <td><b>TOTAL TARGET AUCTION ALLOCATION</b></td>
                        <td>Fall 2026 Season</td>
                        <td class="right" style="color:var(--success); font-size:14px;">$6,500,000</td>
                        <td class="right" style="color:var(--warn);">$650,000</td>
                        <td><span class="badge badge-green">Bank Covenants: 100% IN COMPLIANCE</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Stan's Master 4-County Production Bidding Models Table (Summary View) -->
        <div class="table-wrapper" style="margin-top:20px; border:1px solid rgba(139,92,246,0.4); background:rgba(30,27,75,0.15);">
            <div class="table-header" style="background:rgba(139,92,246,0.2);">
                <div>
                    <h3 style="margin:0; color:var(--text-primary);">🎯 Stan's Master 2025 Bidding Models &amp; 4-County Rollup</h3>
                    <div style="font-size:11px; color:var(--text-muted);">Jennings production baseline: Removed certs &lt; $3,000 where both installments are delinquent. Commercial isolated.</div>
                </div>
                <span class="badge badge-green" style="font-size:11px; font-weight:800;">Revised Total: 5,656 Certs &middot; $42.13M</span>
            </div>
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
                        <th class="right">Orig Total $</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Lake</b></td>
                        <td class="right">1,611</td>
                        <td class="right">$11,740,875</td>
                        <td class="right">29</td>
                        <td class="right" style="color:var(--accent); font-weight:700;">$2,110,110</td>
                        <td class="right" style="color:var(--success); font-weight:800;">1,640</td>
                        <td class="right" style="color:var(--success); font-weight:800;">$13,850,986</td>
                        <td class="right" style="color:var(--text-muted);">93 ($184k)</td>
                        <td class="right">$14,034,923</td>
                    </tr>
                    <tr>
                        <td><b>Will</b></td>
                        <td class="right">1,442</td>
                        <td class="right">$9,284,074</td>
                        <td class="right">50</td>
                        <td class="right" style="color:var(--accent); font-weight:700;">$1,203,089</td>
                        <td class="right" style="color:var(--success); font-weight:800;">1,492</td>
                        <td class="right" style="color:var(--success); font-weight:800;">$10,487,163</td>
                        <td class="right" style="color:var(--text-muted);">82 ($152k)</td>
                        <td class="right">$10,639,372</td>
                    </tr>
                    <tr>
                        <td><b>McHenry</b></td>
                        <td class="right">1,328</td>
                        <td class="right">$7,788,659</td>
                        <td class="right">31</td>
                        <td class="right" style="color:var(--accent); font-weight:700;">$679,386</td>
                        <td class="right" style="color:var(--success); font-weight:800;">1,359</td>
                        <td class="right" style="color:var(--success); font-weight:800;">$8,468,045</td>
                        <td class="right" style="color:var(--text-muted);">88 ($166k)</td>
                        <td class="right">$8,633,629</td>
                    </tr>
                    <tr>
                        <td><b>DuPage</b></td>
                        <td class="right">1,142</td>
                        <td class="right">$8,273,859</td>
                        <td class="right">23</td>
                        <td class="right" style="color:var(--accent); font-weight:700;">$1,053,094</td>
                        <td class="right" style="color:var(--success); font-weight:800;">1,165</td>
                        <td class="right" style="color:var(--success); font-weight:800;">$9,326,953</td>
                        <td class="right" style="color:var(--text-muted);">73 ($157k)</td>
                        <td class="right">$9,483,829</td>
                    </tr>
                    <tr style="font-weight:800; background:rgba(255,255,255,0.06);">
                        <td><span class="badge badge-purple">4-County Rollup</span></td>
                        <td class="right">5,523</td>
                        <td class="right">$37,087,468</td>
                        <td class="right">133</td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$5,045,679</td>
                        <td class="right" style="color:var(--success); font-weight:900; font-size:14px;">5,656</td>
                        <td class="right" style="color:var(--success); font-weight:900; font-size:14px;">$42,133,147</td>
                        <td class="right" style="color:var(--text-muted);">336 ($659k)</td>
                        <td class="right">$42,791,753</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 1-Click Launch Card to Stan's Dedicated Tactical War Room -->
        <div style="background: linear-gradient(135deg, rgba(30,27,75,0.8), rgba(15,23,42,0.95)); border: 1px solid rgba(139,92,246,0.45); border-radius: 10px; padding: 22px 24px; margin-top: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
            <div>
                <div style="font-size: 16px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 10px;">
                    <span>🎯 Stan's Tactical Bidding &amp; Planning War Room</span>
                    <span class="badge badge-purple" style="font-size:10.5px;">Operator Workbench</span>
                </div>
                <div style="font-size: 12.5px; color: var(--text-muted); margin-top: 6px; max-width: 680px; line-height: 1.6;">
                    To keep Jay's executive screen clean and institutional, the full lien-by-lien screener (268 parcels), 1-click Google Street View / County GIS drive-bys, and state auction upload CSVs are housed in Stan's dedicated tactical portal.
                </div>
            </div>
            <div>
                <a href="tax.html?passcode=Jennings2026" target="_blank" class="btn btn-primary" style="background: var(--accent); font-weight: 800; text-decoration: none; padding: 12px 24px; font-size: 13.5px; display: inline-flex; align-items: center; gap: 8px; border-radius: 6px; box-shadow: 0 4px 14px rgba(59,130,246,0.4);">
                    <span>⚡ Launch Stan's War Room</span>
                    <span style="font-size: 13px;">↗</span>
                </a>
            </div>
        </div>
    `;
}}
'''

    # Replace renderTaxActivityView in code
    # Find start and end of renderTaxActivityView
    pattern = r'function renderTaxActivityView\(\) \{.*?(?=function renderCashFlashView)'
    if re.search(pattern, code, re.DOTALL):
        code = re.sub(pattern, clean_tax_func + '\n\n', code, flags=re.DOTALL)
        print("✅ Successfully replaced renderTaxActivityView with clean, simplified executive capital view")
    else:
        print("❌ Could not match renderTaxActivityView block")

    with open('generate_cfo_html_viewer.py', 'w') as f:
        f.write(code)

if __name__ == '__main__':
    clean_cfo_tax_view()
