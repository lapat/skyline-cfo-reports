import json
import re

def update_cfo_viewer():
    with open('master_debt_and_tax_lines.json') as f:
        debt_data = json.load(f)

    with open('generate_cfo_html_viewer.py', 'r') as f:
        cfo_code = f.read()

    # 1. Tax Lines Table HTML for Jay's Tax Flow View
    tax_lines_html = """
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
        </div>"""

    # 2. Enhanced Bidding Optimizer incorporating 95% Advance Rate Math
    bidding_opt_html = """
        <!-- Pillar 2: Auction Bidding Optimizer (Incorporating 95% Bank Advance Rate) -->
        <div class="table-wrapper" style="margin-top:20px; border:1px solid rgba(16,185,129,0.3); background:rgba(6,78,59,0.12);">
            <div class="table-header" style="background:rgba(16,185,129,0.2); padding:14px 20px;">
                <div>
                    <h3 style="margin:0; color:var(--text-primary); font-size:15px; font-weight:800;">⚖️ Next-Auction Bidding Capacity &amp; Bank Borrowing Optimizer</h3>
                    <div style="font-size:11.5px; color:var(--text-muted); margin-top:3px;">
                        Under the <b>95% bank advance rate</b>, Jennings only needs to put up <b>5% cash equity ($325k total)</b> to deploy the full $6.5M Fall 2026 campaign!
                    </div>
                </div>
                <span class="badge badge-green" style="font-size:11.5px; font-weight:800; padding:6px 12px;">$23,500,000 Pre-Approved Facility Headroom</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Target County Tax Sale</th>
                        <th>Estimated Date</th>
                        <th class="right">Recommended Allocation</th>
                        <th class="right" style="color:var(--accent);">Bank Funded (95%)</th>
                        <th class="right" style="color:var(--warn);">Required Cash Equity (5%)</th>
                        <th>Target Return &amp; Net Spread</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Lake County Fall Tax Sale</b></td>
                        <td>Friday, Nov 13, 2026</td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$2,000,000</td>
                        <td class="right" style="color:var(--accent); font-weight:700;">$1,900,000</td>
                        <td class="right" style="color:var(--warn); font-weight:700;">$100,000</td>
                        <td><span class="badge badge-green">4%-5% Bids (12% Subtaxes &middot; +568 bps net carry)</span></td>
                    </tr>
                    <tr>
                        <td><b>DuPage County Fall Sale</b></td>
                        <td>Thursday, Nov 19, 2026</td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$1,500,000</td>
                        <td class="right" style="color:var(--accent); font-weight:700;">$1,425,000</td>
                        <td class="right" style="color:var(--warn); font-weight:700;">$75,000</td>
                        <td><span class="badge badge-green">12.0% Statutory Return (+518 bps net carry)</span></td>
                    </tr>
                    <tr>
                        <td><b>McHenry County Tax Sale</b></td>
                        <td>Monday, Nov 23, 2026</td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$1,000,000</td>
                        <td class="right" style="color:var(--accent); font-weight:700;">$950,000</td>
                        <td class="right" style="color:var(--warn); font-weight:700;">$50,000</td>
                        <td><span class="badge badge-green">12.0% Statutory Return (+568 bps net carry)</span></td>
                    </tr>
                    <tr>
                        <td><b>Will County Fall Tax Sale</b></td>
                        <td>Tuesday, Dec 01, 2026</td>
                        <td class="right" style="color:var(--accent); font-weight:800;">$2,000,000</td>
                        <td class="right" style="color:var(--accent); font-weight:700;">$1,900,000</td>
                        <td class="right" style="color:var(--warn); font-weight:700;">$100,000</td>
                        <td><span class="badge badge-green">12.0% Statutory Return (+552 bps net carry)</span></td>
                    </tr>
                    <tr style="background:rgba(255,255,255,0.06); font-weight:800;">
                        <td><b>TOTAL TARGET AUCTION ALLOCATION</b></td>
                        <td>Fall 2026 Season</td>
                        <td class="right" style="color:var(--success); font-size:15px;">$6,500,000</td>
                        <td class="right" style="color:var(--accent); font-size:14px;">$6,175,000</td>
                        <td class="right" style="color:var(--warn); font-size:14px;">$325,000</td>
                        <td><b style="color:var(--success);">Pre-Approved &middot; 95% Funded by Banks</b></td>
                    </tr>
                </tbody>
            </table>
            <div style="background:rgba(0,0,0,0.2); padding:10px 18px; font-size:11px; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>💡 <b>Arbitrage Math:</b> Borrowing at <b>6.32% - 6.82%</b> vs Statutory <b>12.00%</b> yield locks in <b>+518 to +568 bps of pure net positive carry</b> on bank money.</div>
                <div><b>Immediate Capacity:</b> $23.50M headroom is more than 3.6x total campaign demand.</div>
            </div>
        </div>"""

    # 3. Master Real Estate Mortgages Table for the Liquidity View
    mortgages_html = """
        <!-- 🏢 MASTER REAL ESTATE MORTGAGE DEBT PORTFOLIO ($68,200,000 TOTAL DEBT) -->
        <div class="table-wrapper" style="margin-top:24px; border:2px solid rgba(139,92,246,0.4); background:rgba(30,27,75,0.15);">
            <div class="table-header" style="background:rgba(139,92,246,0.2); padding:14px 20px;">
                <div>
                    <h3 style="margin:0; font-size:15px; font-weight:800; color:#c4b5fd; display:flex; align-items:center; gap:8px;">
                        <span>🏢 Master Real Estate Mortgage Debt Portfolio</span>
                        <span class="badge badge-purple" style="font-size:10px; font-weight:800;">Total Mortgages: $68,200,000</span>
                    </h3>
                    <div style="font-size:11.5px; color:var(--text-muted); margin-top:3px;">
                        Verified from Jay's <i>Mortgage and Tax Line Summary</i>. Complete schedule of amortization, maturity dates, and bank covenants across Jennings real estate assets.
                    </div>
                </div>
                <span class="badge badge-blue" style="font-size:11px; font-weight:800;">Total Enterprise Debt: $120,200,000</span>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Property &amp; Borrower Entity</th>
                        <th>Bank Lender</th>
                        <th class="right">Loan Facility</th>
                        <th class="right">Current Rate</th>
                        <th class="right">Monthly P&amp;I</th>
                        <th>Amortization</th>
                        <th>Maturity</th>
                        <th class="right">Balloon at Maturity</th>
                        <th>DSCR &amp; Bank Covenants</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Park City Manufactured Homes</b><div style="font-size:10.5px; color:var(--text-muted);">Fixed Swap Loan</div></td>
                        <td>Old National Bank (FMW)</td>
                        <td class="right" style="font-weight:700;">$19,125,000</td>
                        <td class="right"><span class="badge badge-green">4.33% Fixed</span></td>
                        <td class="right">$119,246</td>
                        <td>20 years</td>
                        <td>12/20/2029</td>
                        <td class="right" style="color:var(--warn); font-weight:700;">$11,520,565</td>
                        <td style="font-size:10.5px; color:var(--text-muted);">DSCR 1.30x &middot; $1.0M min dep &middot; Tax escrow 1 yr &middot; JRI TNW $1.8M</td>
                    </tr>
                    <tr>
                        <td><b>Park City MHC (Revolver)</b><div style="font-size:10.5px; color:var(--text-muted);">Revolving Credit Line</div></td>
                        <td>Old National Bank (FMW)</td>
                        <td class="right" style="font-weight:700;">$20,000,000</td>
                        <td class="right"><span class="badge badge-green">6.22% SOFR+1.9%</span></td>
                        <td class="right">Interest Only</td>
                        <td>Interest Only</td>
                        <td>12/19/2029</td>
                        <td class="right">-</td>
                        <td style="font-size:10.5px; color:var(--text-muted);">DSCR 1.30x TTM &middot; $1.0M min dep</td>
                    </tr>
                    <tr>
                        <td><b>Lakeview Mobile Home Park</b><div style="font-size:10.5px; color:var(--text-muted);">Partnership</div></td>
                        <td>Fannie Mae / SunTrust</td>
                        <td class="right" style="font-weight:700;">$8,000,000</td>
                        <td class="right"><span class="badge badge-green">4.40% Fixed</span></td>
                        <td class="right">$40,061</td>
                        <td>Yrs 1-5 IO, 30-yr amort</td>
                        <td>3/01/2028</td>
                        <td class="right" style="color:var(--warn); font-weight:700;">$7,281,523</td>
                        <td style="font-size:10.5px; color:var(--text-muted);">DSCR 1.55x &middot; Non-recourse (Jay, BDT, JRI) &middot; Prepay yield maint till 8/27</td>
                    </tr>
                    <tr>
                        <td><b>Bay Bayou RV Resort</b><div style="font-size:10.5px; color:var(--text-muted);">Florida LLC</div></td>
                        <td>Byline Bank</td>
                        <td class="right" style="font-weight:700;">$8,500,000</td>
                        <td class="right"><span class="badge badge-green">6.50% Fixed</span></td>
                        <td class="right">$57,393</td>
                        <td>7 years</td>
                        <td>7/28/2030</td>
                        <td class="right" style="color:var(--warn); font-weight:700;">$7,296,648</td>
                        <td style="font-size:10.5px; color:var(--text-muted);">DSCR 1.25x semi-annual &middot; Operating acct required</td>
                    </tr>
                    <tr>
                        <td><b>Sunkissed Village RV Resort</b><div style="font-size:10.5px; color:var(--text-muted);">Florida LLC</div></td>
                        <td>Byline Bank</td>
                        <td class="right" style="font-weight:700;">$5,000,000</td>
                        <td class="right"><span class="badge badge-green">6.47% Fixed</span></td>
                        <td class="right">$37,200</td>
                        <td>20 years</td>
                        <td>8/29/2031</td>
                        <td class="right">-</td>
                        <td style="font-size:10.5px; color:var(--text-muted);">DSCR 1.25x &middot; Guaranteed: BDT (elim if DSC 1.50x)</td>
                    </tr>
                    <tr>
                        <td><b>Upriver Partners</b><div style="font-size:10.5px; color:var(--text-muted);">Florida LLC</div></td>
                        <td>LMCU Florida</td>
                        <td class="right" style="font-weight:700;">$2,500,000</td>
                        <td class="right"><span class="badge badge-green">4.60% Fixed</span></td>
                        <td class="right">$15,952</td>
                        <td>20 years</td>
                        <td>7/31/2028</td>
                        <td class="right">-</td>
                        <td style="font-size:10.5px; color:var(--text-muted);">$2.36M outstanding &middot; DSCR 1.25x &middot; Zero prepay penalty</td>
                    </tr>
                    <tr>
                        <td><b>Home Sites Series C (Ellis Apts)</b><div style="font-size:10.5px; color:var(--text-muted);">Series C LLC</div></td>
                        <td>Byline Bank</td>
                        <td class="right" style="font-weight:700;">$2,100,000</td>
                        <td class="right"><span class="badge badge-green">6.01% Fixed</span></td>
                        <td class="right">$13,540</td>
                        <td>25 years</td>
                        <td>9/08/2029</td>
                        <td class="right">-</td>
                        <td style="font-size:10.5px; color:var(--text-muted);">DSCR 1.20x &middot; BDT Assets $45M &middot; BDT Liquidity $700k</td>
                    </tr>
                    <tr>
                        <td><b>The Bluffs MH &amp; RV Resort</b><div style="font-size:10.5px; color:var(--text-muted);">Loans A &amp; B Combined</div></td>
                        <td>Byline Bank</td>
                        <td class="right" style="font-weight:700;">$2,975,000</td>
                        <td class="right"><span class="badge badge-green">6.75% Float</span></td>
                        <td class="right">$16,500</td>
                        <td>25 yrs / IO</td>
                        <td>11/14/2032</td>
                        <td class="right">-</td>
                        <td style="font-size:10.5px; color:var(--text-muted);">DSCR 1.20x &middot; Max LTV 50% &middot; $45k Keepwell deposit</td>
                    </tr>
                    <tr style="font-weight:800; background:rgba(255,255,255,0.06);">
                        <td><span class="badge badge-purple" style="font-size:11px;">Total Real Estate Mortgages</span></td>
                        <td>7 Key Facilities</td>
                        <td class="right" style="color:var(--accent); font-size:14px;">$68,200,000</td>
                        <td class="right"><span class="badge badge-green" style="font-size:11px;">5.42% Wtd Avg</span></td>
                        <td class="right" style="font-size:13px;">$319,892/mo</td>
                        <td>20 - 30 yrs</td>
                        <td>2028 - 2032</td>
                        <td class="right" style="color:var(--warn); font-size:13px;">$26,098,736</td>
                        <td style="font-size:11px; color:var(--success); font-weight:700;">100% In Compliance across all Banks</td>
                    </tr>
                </tbody>
            </table>
        </div>"""

    # In generate_cfo_html_viewer.py:
    # 1. Replace the existing Bidding Optimizer with the enhanced one
    opt_start = '        <!-- Pillar 2: Auction Bidding Optimizer -->'
    opt_end = '        <!-- Stan\'s Master 4-County Production Bidding Models Table'
    if opt_start in cfo_code:
        # replace between opt_start and opt_end or before the Stan section
        pattern_opt = r'        <!-- Pillar 2: Auction Bidding Optimizer -->.*?</div>\s*</div>'
        if re.search(pattern_opt, cfo_code, re.DOTALL):
            cfo_code = re.sub(pattern_opt, bidding_opt_html + "\n\n" + tax_lines_html, cfo_code, count=1, flags=re.DOTALL)
            print("✅ Replaced Bidding Optimizer and injected 3-Bank Tax Lines in CFO viewer")

    # 2. In Liquidity View, replace the old $12.8M Tax Line Headroom with the full $120.2M Master Debt Portfolio
    old_liq_debt = '            <!-- Tax Line Headroom -->\n            <div class="table-wrapper">\n                <div class="table-header">\n                    <h3>🏦 $12.8M Tax Line Borrowing Headroom</h3>'
    if old_liq_debt in cfo_code:
        pattern_liq = r'            <!-- Tax Line Headroom -->.*?</tbody>\s*</table>\s*</div>'
        if re.search(pattern_liq, cfo_code, re.DOTALL):
            cfo_code = re.sub(pattern_liq, tax_lines_html + "\n\n" + mortgages_html, cfo_code, count=1, flags=re.DOTALL)
            print("✅ Injected Master Debt Portfolio into Liquidity View")

    with open('generate_cfo_html_viewer.py', 'w') as f:
        f.write(cfo_code)

    # 3. Update generate_tax_dashboard.py Section 3 with the verified $52.0M Tax Lines & 95% Advance Rate
    with open('generate_tax_dashboard.py', 'r') as f:
        tax_code = f.read()

    # In tax dashboard, find section 3 table and enhance with 95% advance rate
    sec3_target = '  <!-- SECTION 3: UPCOMING COLLAR COUNTIES SCHEDULE'
    if sec3_target in tax_code:
        # inject the 3-bank tax lines table inside section 3
        tax_code = tax_code.replace(sec3_target, tax_lines_html + "\n\n" + sec3_target)
        print("✅ Injected 3-Bank Tax Lines into generate_tax_dashboard.py")

    with open('generate_tax_dashboard.py', 'w') as f:
        f.write(tax_code)

if __name__ == '__main__':
    update_cfo_viewer()
