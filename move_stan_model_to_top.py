import os

def update_cfo_viewer():
    with open('generate_cfo_html_viewer.py', 'r') as f:
        code = f.read()

    # The exact block to cut from the bottom:
    cut_target = """        <!-- Stan's Master 4-County Production Bidding Models Table (Summary View) -->
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
        </div>"""

    if cut_target not in code:
        print("❌ Could not find cut_target in generate_cfo_html_viewer.py")
        return

    # Cut from lower position
    code = code.replace(cut_target, "")
    print("✅ Removed Stan table from lower position in CFO viewer")

    # The new enhanced block for the top of Jay's view:
    top_block = """        <!-- 🎯 STAN'S MASTER 2026 BIDDING MODELS & 4-COUNTY ROLLUP (TOP LEAD) -->
        <div class="table-wrapper" style="margin-top:20px; margin-bottom:24px; border:2px solid rgba(139,92,246,0.55); background:linear-gradient(135deg, rgba(30,27,75,0.35), rgba(15,23,42,0.5)); box-shadow:0 4px 20px rgba(139,92,246,0.15);">
            <div class="table-header" style="background:rgba(139,92,246,0.22); padding:14px 20px;">
                <div>
                    <h3 style="margin:0; font-size:16px; font-weight:800; color:#c4b5fd; display:flex; align-items:center; gap:8px;">
                        <span>🎯 Stan's Master 2026 Bidding Models &amp; 4-County Production Rollup</span>
                        <span class="badge badge-purple" style="font-size:10px; font-weight:800;">Jay's 2026 Bidding Blueprint</span>
                    </h3>
                    <div style="font-size:11.5px; color:var(--text-muted); margin-top:3px;">Parsed directly from Stan's production Excel models emailed to Louis &amp; Jay. Defines Jennings' revised baseline across Lake, DuPage, McHenry, and Will.</div>
                </div>
                <span class="badge badge-green" style="font-size:12px; font-weight:800; padding:6px 12px;">Revised Total: 5,656 Certs &middot; $42.13M</span>
            </div>
            
            <!-- 3 Key Takeaways -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:10px; padding:14px 18px; background:rgba(0,0,0,0.15); border-bottom:1px solid var(--border);">
                <div style="font-size:11.5px; color:var(--text-muted);">
                    <b style="color:var(--warn);">1. &lt;$3k Filter Rule:</b> Stan eliminated <b>336 certs ($658k)</b> of full delinquent items to cut low-margin servicing overhead.
                </div>
                <div style="font-size:11.5px; color:var(--text-muted);">
                    <b style="color:var(--accent);">2. Commercial Focus:</b> <b>133 certs ($5.05M)</b> averaging <b style="color:#60a5fa;">$37,937 / cert</b> (Jay's large-ticket priority).
                </div>
                <div style="font-size:11.5px; color:var(--text-muted);">
                    <b style="color:var(--success);">3. Win Rate Reality:</b> <b>$42.13M upload</b> cleared <b>$13.54M won</b> last year (~32% win rate @ 2.01% avg bid).
                </div>
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
                        <td><span class="badge badge-purple" style="font-size:11px;">4-County Rollup</span></td>
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
        </div>"""

    # Insert top_block right before <div class="cards-grid">
    cards_grid_target = """        <div class="cards-grid">
            <div class="stat-card">
                <div class="stat-card-label">Monday Redemptions (10/19)</div>"""

    if cards_grid_target in code:
        code = code.replace(cards_grid_target, top_block + "\n\n" + cards_grid_target)
        print("✅ Injected Stan Master table at the very top of CFO view")
    else:
        print("❌ Could not find cards_grid_target in generate_cfo_html_viewer.py")
        return

    with open('generate_cfo_html_viewer.py', 'w') as f:
        f.write(code)

if __name__ == '__main__':
    update_cfo_viewer()
