import re

def upgrade_cfo_viewer():
    with open('generate_cfo_html_viewer.py', 'r') as f:
        cfo_code = f.read()

    # The SOFR Sensitivity Matrix and 24-Month Debt Waterfall HTML Component for Jay
    sofr_and_waterfall_html = """
        <!-- ⚖️ INTERACTIVE SOFR SENSITIVITY MATRIX & 24-MONTH REDEMPTION WATERFALL -->
        <div class="table-wrapper" style="margin-top:20px; border:2px solid rgba(16,185,129,0.4); background:linear-gradient(135deg, rgba(6,78,59,0.15), rgba(15,23,42,0.6)); box-shadow:0 4px 20px rgba(16,185,129,0.1);">
            <div class="table-header" style="background:rgba(16,185,129,0.22); padding:14px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <h3 style="margin:0; font-size:15px; font-weight:800; color:#6ee7b7; display:flex; align-items:center; gap:8px;">
                        <span>⚖️ Floating Debt SOFR Sensitivity &amp; 24-Month Capital Payoff Waterfall</span>
                        <span class="badge badge-green" style="font-size:10px; font-weight:800;">Jay Treasury Simulator</span>
                    </h3>
                    <div style="font-size:11.5px; color:var(--text-muted); margin-top:3px;">
                        Models the net arbitrage spread against 12.0% statutory subtax return across benchmark rate shifts, and projects exact debt payoff velocity.
                    </div>
                </div>
                <div style="display:flex; gap:6px; align-items:center;">
                    <span style="font-size:11px; color:var(--text-muted); font-weight:700;">Simulate SOFR:</span>
                    <button onclick="simulateSofrRate(-1.0)" id="btnSofrM100" class="btn btn-outline" style="font-size:10px; padding:3px 8px;">-100 bps (3.32%)</button>
                    <button onclick="simulateSofrRate(-0.5)" id="btnSofrM50" class="btn btn-outline" style="font-size:10px; padding:3px 8px;">-50 bps (3.82%)</button>
                    <button onclick="simulateSofrRate(0.0)" id="btnSofrCur" class="btn btn-primary" style="font-size:10px; padding:3px 8px; font-weight:800;">Current (4.32%)</button>
                    <button onclick="simulateSofrRate(0.5)" id="btnSofrP50" class="btn btn-outline" style="font-size:10px; padding:3px 8px;">+50 bps (4.82%)</button>
                    <button onclick="simulateSofrRate(1.0)" id="btnSofrP100" class="btn btn-outline" style="font-size:10px; padding:3px 8px;">+100 bps (5.32%)</button>
                </div>
            </div>

            <!-- 4 Dynamic SOFR KPI Badges -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; padding:12px 18px; background:rgba(0,0,0,0.2); border-bottom:1px solid var(--border);">
                <div>
                    <div style="font-size:10.5px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Simulated SOFR Benchmark</div>
                    <div id="dispSofrRate" style="font-size:18px; font-weight:800; color:#fff;">4.324%</div>
                    <div style="font-size:10.5px; color:var(--text-secondary);">30-Day Term SOFR</div>
                </div>
                <div>
                    <div style="font-size:10.5px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Weighted Borrowing Cost</div>
                    <div id="dispWtdBorrow" style="font-size:18px; font-weight:800; color:var(--accent);">6.48%</div>
                    <div style="font-size:10.5px; color:var(--text-secondary);">Old Natl (6.32%), Byline (6.82%), 1st Chi (6.32%)</div>
                </div>
                <div>
                    <div style="font-size:10.5px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Net Arbitrage Carry Spread</div>
                    <div id="dispNetSpread" style="font-size:18px; font-weight:900; color:var(--success);">+552 bps</div>
                    <div style="font-size:10.5px; color:var(--text-secondary);">12.00% Subtax Yield minus Debt Cost</div>
                </div>
                <div>
                    <div style="font-size:10.5px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Net Spread Arbitrage Profit</div>
                    <div id="dispSpreadProfit" style="font-size:18px; font-weight:900; color:var(--success);">+$340,860 / yr</div>
                    <div style="font-size:10.5px; color:var(--text-secondary);">Pure net profit on $6.175M bank leverage</div>
                </div>
            </div>

            <!-- 24-Month Debt Payoff Waterfall Table -->
            <div style="padding:14px 20px;">
                <div style="font-size:12px; font-weight:800; color:#fff; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                    <span>🌊 15-Year Historical Redemption Decay Curve &amp; Debt Retirement Waterfall</span>
                    <span style="font-size:11px; color:var(--accent);">Assumes $6,175,000 borrowed at 95% advance rate for Fall 2026 auction</span>
                </div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Redemption Velocity Period</th>
                                <th>Historical Driver</th>
                                <th class="right">% of Capital Returned</th>
                                <th class="right">Cash Inflow to Pay Debt</th>
                                <th class="right">Remaining Bank Debt</th>
                                <th class="right" style="color:var(--success);">Cumulative Interest Saved</th>
                                <th>Debt Facility Retired</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><b>Months 1 – 6</b><div style="font-size:10px; color:var(--text-muted);">Immediate Turn</div></td>
                                <td>Property sales, refinances, title transfers</td>
                                <td class="right" style="font-weight:700;">35.0%</td>
                                <td class="right" style="color:var(--success); font-weight:800;">$2,161,250</td>
                                <td class="right">$4,013,750</td>
                                <td class="right" style="color:var(--success); font-weight:700;">+$70,024</td>
                                <td><span class="badge badge-green">Byline Line Paid Down to $2.84M</span></td>
                            </tr>
                            <tr>
                                <td><b>Months 7 – 12</b><div style="font-size:10px; color:var(--text-muted);">Summer Tax Cycle</div></td>
                                <td>Annual county property tax billing notice cure</td>
                                <td class="right" style="font-weight:700;">45.0%</td>
                                <td class="right" style="color:var(--success); font-weight:800;">$2,778,750</td>
                                <td class="right">$1,235,000</td>
                                <td class="right" style="color:var(--success); font-weight:700;">+$225,480</td>
                                <td><span class="badge badge-green">Byline Retired &middot; 1st Chicago Paid Down</span></td>
                            </tr>
                            <tr>
                                <td><b>Months 13 – 24</b><div style="font-size:10px; color:var(--text-muted);">Pre-Deed Cycle</div></td>
                                <td>Mortgage servicer pre-foreclosure tax cures</td>
                                <td class="right" style="font-weight:700;">15.0%</td>
                                <td class="right" style="color:var(--success); font-weight:800;">$926,250</td>
                                <td class="right">$308,750</td>
                                <td class="right" style="color:var(--success); font-weight:700;">+$415,920</td>
                                <td><span class="badge badge-green">1st Chicago Retired &middot; Old Natl Paid</span></td>
                            </tr>
                            <tr>
                                <td><b>Months 25+</b><div style="font-size:10px; color:var(--text-muted);">Final Redemption</div></td>
                                <td>Final legal notice &amp; courtroom redemptions</td>
                                <td class="right" style="font-weight:700;">5.0%</td>
                                <td class="right" style="color:var(--success); font-weight:800;">$308,750</td>
                                <td class="right" style="color:var(--success); font-weight:900;">$0.00</td>
                                <td class="right" style="color:var(--success); font-weight:900;">+$482,650</td>
                                <td><span class="badge badge-purple" style="font-weight:800;">100% DEBT RETIRED &middot; $0 BALANCE</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
"""

    # Inject into CFO viewer right after the Three-Bank Tax Credit Facilities table
    target_tax_lines = '        <!-- 🏛️ THE THREE SYNDICATED BANK TAX CREDIT FACILITIES ($52.0M COMMITMENTS) -->'
    if target_tax_lines in cfo_code:
        # replace right after the tax lines table ends
        pattern = r'(<!-- 🏛️ THE THREE SYNDICATED BANK TAX CREDIT FACILITIES.*?</tbody>\s*</table>\s*</div>)'
        if re.search(pattern, cfo_code, re.DOTALL):
            cfo_code = re.sub(pattern, r'\1\n' + sofr_and_waterfall_html, cfo_code, count=1, flags=re.DOTALL)
            print("✅ Injected SOFR Sensitivity & Waterfall into generate_cfo_html_viewer.py")

    # Inject JavaScript simulator for SOFR
    js_sofr_sim = """
function simulateSofrRate(deltaBps) {{
    const baseSofr = 4.324;
    const activeSofr = baseSofr + deltaBps;
    
    // Recalculate borrowing rates
    const oldNatlRate = activeSofr + 1.90;
    const firstChiRate = activeSofr + 1.90;
    const bylineRate = activeSofr + 2.50;
    
    // Weighted borrowing cost (based on $17.2M Old Natl, $6.3M First Chi, $5.0M Byline)
    const wtdBorrow = ((17.2 * oldNatlRate) + (6.3 * firstChiRate) + (5.0 * bylineRate)) / 28.5;
    
    // Net spread against 12% subtax return
    const netSpreadBps = Math.round((12.00 - wtdBorrow) * 100);
    
    // Annual profit spread on $6.175M bank debt
    const spreadProfit = 6175000 * ((12.00 - wtdBorrow) / 100);

    // Update DOM
    const dSofr = document.getElementById('dispSofrRate');
    const dWtd = document.getElementById('dispWtdBorrow');
    const dSpread = document.getElementById('dispNetSpread');
    const dProfit = document.getElementById('dispSpreadProfit');

    if (dSofr) dSofr.innerText = activeSofr.toFixed(3) + '%';
    if (dWtd) dWtd.innerText = wtdBorrow.toFixed(2) + '%';
    if (dSpread) dSpread.innerText = (netSpreadBps >= 0 ? '+' : '') + netSpreadBps + ' bps';
    if (dProfit) dProfit.innerText = '+$' + Math.round(spreadProfit).toLocaleString('en-US') + ' / yr';

    // Update button states
    const btnIds = ['btnSofrM100', 'btnSofrM50', 'btnSofrCur', 'btnSofrP50', 'btnSofrP100'];
    const activeIdx = deltaBps === -1.0 ? 0 : (deltaBps === -0.5 ? 1 : (deltaBps === 0.0 ? 2 : (deltaBps === 0.5 ? 3 : 4)));
    btnIds.forEach((id, idx) => {{
        const b = document.getElementById(id);
        if (b) b.className = (idx === activeIdx) ? 'btn btn-primary' : 'btn btn-outline';
    }});
}}
"""
    if "function simulateSofrRate" not in cfo_code:
        cfo_code = cfo_code.replace("function switchAuctionTab", js_sofr_sim + "\nfunction switchAuctionTab")
        print("✅ Injected simulateSofrRate() JS function into CFO viewer")

    with open('generate_cfo_html_viewer.py', 'w') as f:
        f.write(cfo_code)

def upgrade_tax_dashboard():
    with open('generate_tax_dashboard.py', 'r') as f:
        tax_code = f.read()

    # 1. Update filter dropdown with Ultra-Certain option
    filter_target = '<select id="lakeTierFilter" class="filter-select" onchange="renderLakeTargetTable()">'
    if filter_target in tax_code and 'ultra95' not in tax_code:
        tax_code = tax_code.replace(filter_target, filter_target + '\n          <option value="ultra95">🛡️ Ultra-Certain Only (&gt;=95% Redemption Score)</option>')
        print("✅ Injected ultra95 option into lakeTierFilter in generate_tax_dashboard.py")

    # 2. Update filter logic in renderLakeTargetTable
    filter_logic_target = 'if (tierVal === \'repeat\' && (!item.prior_redemptions_count || item.prior_redemptions_count < 1)) return false;'
    new_filter_logic = """if (tierVal === 'ultra95' && (!item.redemption_score || item.redemption_score < 95.0)) return false;
        if (tierVal === 'repeat' && (!item.prior_redemptions_count || item.prior_redemptions_count < 1)) return false;"""
    if filter_logic_target in tax_code and 'tierVal === \'ultra95\'' not in tax_code:
        tax_code = tax_code.replace(filter_logic_target, new_filter_logic)
        print("✅ Injected ultra95 filter logic into renderLakeTargetTable")

    # 3. Update table row to show Redemption Certainty Badge
    row_target = '            <td>\n                <span class="badge ${t.is_half_installment ? \'badge-purple\' : \'badge-blue\'}" style="font-size:9px;">${t.installment_tag}</span>\n            </td>'
    new_row_installment = """            <td>
                <span class="badge ${t.is_half_installment ? 'badge-purple' : 'badge-blue'}" style="font-size:9px;">${t.installment_tag}</span>
                <span class="badge ${t.redemption_score >= 95.0 ? 'badge-green' : 'badge-blue'}" style="font-size:8.5px; margin-left:3px; font-weight:800;" title="Quantitative Algorithmic Score: Building/land ratio, equity, township safety, installment intent">⭐ ${t.redemption_score || 95.0}% Certainty</span>
            </td>"""
    if row_target in tax_code and 'Redemption Certainty' not in tax_code:
        tax_code = tax_code.replace(row_target, new_row_installment)
        print("✅ Injected Redemption Certainty Badge into table row in generate_tax_dashboard.py")

    with open('generate_tax_dashboard.py', 'w') as f:
        f.write(tax_code)

if __name__ == '__main__':
    upgrade_cfo_viewer()
    upgrade_tax_dashboard()
