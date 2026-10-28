import json
import re

def build_complete_stan_html(is_cfo_viewer=False):
    with open('stan_bidding_models.json') as f:
        stan_rollup = json.load(f)

    with open('stan_commercial_targets.json') as f:
        comm_targets = json.load(f)

    with open('stan_category_summaries.json') as f:
        cat_summaries = json.load(f)

    ds = "$$" if is_cfo_viewer else "$"

    # 1. Rollup rows
    rollup_rows = ""
    for c in stan_rollup['rollup']:
        is_total = c['county'] == 'Total'
        style = "font-weight:800; background:rgba(255,255,255,0.06);" if is_total else ""
        c_badge = "<span class='badge badge-purple' style='font-size:11px; font-weight:800;'>4-County Rollup Total</span>" if is_total else f"<b>{c['county']}</b>"
        
        non_comm_amt = f"${c['non_commercial']['amount']:,.2f}"
        comm_amt = f"${c['commercial']['amount']:,.2f}"
        rev_amt = f"${c['revised_total']['amount']:,.2f}"
        rem_amt = f"${c['removed_under_3k']['amount']:,.2f}"
        orig_amt = f"${c['original_total']['amount']:,.2f}"

        if is_cfo_viewer:
            non_comm_amt = non_comm_amt.replace('$', '$$')
            comm_amt = comm_amt.replace('$', '$$')
            rev_amt = rev_amt.replace('$', '$$')
            rem_amt = rem_amt.replace('$', '$$')
            orig_amt = orig_amt.replace('$', '$$')

        rollup_rows += f"""
            <tr style="{style}">
              <td>{c_badge}</td>
              <td class="right">{c['non_commercial']['count']:,}</td>
              <td class="right">{non_comm_amt}</td>
              <td class="right">{c['commercial']['count']:,}</td>
              <td class="right" style="color:var(--accent); font-weight:700;">{comm_amt}</td>
              <td class="right" style="color:var(--success); font-weight:800;">{c['revised_total']['count']:,}</td>
              <td class="right" style="color:var(--success); font-weight:800;">{rev_amt}</td>
              <td class="right" style="color:var(--text-muted);">{c['removed_under_3k']['count']:,}</td>
              <td class="right" style="color:var(--text-muted);">{rem_amt}</td>
              <td class="right" style="color:var(--text-primary);">{c['original_total']['count']:,}</td>
              <td class="right" style="color:var(--text-primary);">{orig_amt}</td>
            </tr>"""

    # 2. Commercial rows (Top 35 rendered server-side)
    comm_rows = ""
    for item in comm_targets[:35]:
        amt_str = f"${item['tax_due']:,.2f}"
        if is_cfo_viewer:
            amt_str = amt_str.replace('$', '$$')
        
        no_mort_badge = "<span class='badge badge-green' style='font-size:9px;'>No Mort</span>" if item['no_mortgage'] else ""
        half_badge = "<span class='badge badge-purple' style='font-size:9px;'>2nd Inst Only</span>" if item['is_half_installment'] else ""
        comment_badge = f"<span class='badge badge-blue' style='font-size:9.5px; font-weight:700;'>{item['comment']}</span>" if item['comment'] else ""

        county_color = "var(--accent)" if item['county'] == 'Lake' else ("var(--purple)" if item['county'] == 'Will' else "var(--success)")

        comm_rows += f"""
            <tr>
              <td><b style="color:{county_color};">{item['county']}</b></td>
              <td><code style="font-size:11px; font-weight:700;">{item['pin']}</code></td>
              <td>
                <b>{item['taxpayer']}</b> {comment_badge}
                <div style="font-size:10.5px; color:var(--text-muted);">{item['address']} ({item['city']})</div>
              </td>
              <td class="right" style="font-weight:800; color:var(--text-primary);">{amt_str}</td>
              <td class="right"><span class="badge badge-green" style="font-size:10.5px; font-weight:800;">{item['bid']}</span></td>
              <td class="right" style="color:{'var(--success)' if item['bldg_land_ratio'] >= 2.0 else 'var(--warn)'}; font-weight:700;">{item['bldg_land_ratio']}x</td>
              <td>{no_mort_badge} {half_badge}</td>
            </tr>"""

    prefix = "cfoStan" if is_cfo_viewer else "stanPortal"

    html = f"""
  <!-- SECTION: STAN'S MASTER 2026 PRODUCTION BIDDING MODELS & 4-COUNTY ROLLUP (COMPLETE DATA SUITE) -->
  <div class="section-card" style="border: 2px solid rgba(139, 92, 246, 0.55); background: linear-gradient(135deg, rgba(30, 27, 75, 0.4), rgba(15, 23, 42, 0.55)); margin-bottom: 24px; box-shadow: 0 4px 25px rgba(139, 92, 246, 0.2);">
    <div class="section-header" style="background: rgba(139, 92, 246, 0.22); padding: 14px 20px; cursor: pointer;" onclick="toggleSection('{prefix}Body', '{prefix}Icon')">
      <div>
        <div class="section-title" style="color: #c4b5fd; font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
          <span>🎯 Stan's Master 2026 Bidding Models &amp; 4-County Production Rollup</span>
          <span class="badge badge-purple" style="font-size: 10px; font-weight: 800;">Jay's 2026 Bidding Blueprint</span>
        </div>
        <div class="section-desc" style="color: var(--text-muted); font-size: 12px; margin-top: 3px;">
          Complete dataset parsed from Stan's 5 production Excel models emailed to Louis &amp; Jay. Master 4-County Rollup, 133 Commercial Targets ({ds}5.05M), and Proprietary Redline Rules.
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 10px;">
        <span class="badge badge-green" style="font-size: 12px; font-weight: 800; padding: 6px 12px;">Revised Upload: 5,656 Certs &middot; {ds}42.13M</span>
        <span id="{prefix}Icon" style="font-size: 14px; color: var(--text-muted); font-weight: 700;">▲</span>
      </div>
    </div>
    
    <div id="{prefix}Body">
      <!-- 4 Strategic Takeaway Metrics -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; padding: 18px 20px 14px 20px;">
        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;">
          <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Revised Bidding Upload Pool</div>
          <div style="font-size: 22px; font-weight: 800; color: var(--success); margin: 4px 0;">5,656 Certs &middot; {ds}42.13M</div>
          <div style="font-size: 11px; color: var(--text-secondary);">Non-Commercial ({ds}37.09M) + Commercial ({ds}5.05M)</div>
        </div>

        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;">
          <div style="font-size: 11px; color: var(--accent); text-transform: uppercase; font-weight: 700;">Commercial / Industrial Focus</div>
          <div style="font-size: 22px; font-weight: 800; color: var(--accent); margin: 4px 0;">133 Certs &middot; {ds}5.05M</div>
          <div style="font-size: 11px; color: var(--text-secondary);"><b style="color:#60a5fa;">{ds}37,937 / cert avg</b> (Jay's high-dollar priority)</div>
        </div>

        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;">
          <div style="font-size: 11px; color: var(--warn); text-transform: uppercase; font-weight: 700;">Stan's &lt;{ds}3k Full-Inst Filter</div>
          <div style="font-size: 22px; font-weight: 800; color: var(--warn); margin: 4px 0;">336 Certs &middot; {ds}658,606</div>
          <div style="font-size: 11px; color: var(--text-secondary);">Removed low-margin junk &amp; admin overhead</div>
        </div>

        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;">
          <div style="font-size: 11px; color: var(--purple); text-transform: uppercase; font-weight: 700;">Win Rate Reality &amp; Target Spend</div>
          <div style="font-size: 22px; font-weight: 800; color: #c4b5fd; margin: 4px 0;">32.1% Win Rate</div>
          <div style="font-size: 11px; color: var(--text-secondary);">{ds}42.13M upload cleared {ds}13.54M won @ 2.01% avg bid</div>
        </div>
      </div>

      <!-- Stan Multi-Tab Navigation -->
      <div style="display: flex; gap: 8px; padding: 0 20px 12px 20px; border-bottom: 1px solid var(--border); flex-wrap: wrap;">
        <button id="{prefix}BtnRollup" onclick="switchStanSubTab('{prefix}', 'rollup')" class="btn btn-primary" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">📊 4-County Master Rollup</button>
        <button id="{prefix}BtnComm" onclick="switchStanSubTab('{prefix}', 'comm')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">🏢 133 Prime Commercial Targets ({ds}5.05M)</button>
        <button id="{prefix}BtnRedline" onclick="switchStanSubTab('{prefix}', 'redline')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">⚠️ Stan's Redlines &amp; Exclusions (58 Parcels)</button>
      </div>

      <!-- TAB 1: MASTER 4-COUNTY ROLLUP TABLE -->
      <div id="{prefix}TabRollup" style="display: block; padding: 14px 20px;">
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>County</th>
                <th class="right">Non-Comm Certs</th>
                <th class="right">Non-Comm $</th>
                <th class="right">Comm Certs</th>
                <th class="right">Comm $ (Avg ~{ds}38k)</th>
                <th class="right" style="color:var(--success);">Revised Bid Certs</th>
                <th class="right" style="color:var(--success);">Revised Bid $</th>
                <th class="right" style="color:var(--text-muted);">Removed (&lt;{ds}3k)</th>
                <th class="right" style="color:var(--text-muted);">Removed $</th>
                <th class="right">Orig Total Certs</th>
                <th class="right">Orig Total $</th>
              </tr>
            </thead>
            <tbody>
{rollup_rows}
            </tbody>
          </table>
        </div>
      </div>

      <!-- TAB 2: 133 PRIME COMMERCIAL TARGETS TABLE -->
      <div id="{prefix}TabComm" style="display: none; padding: 14px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
          <div>
            <span style="font-size: 13px; font-weight: 800; color: #fff;">🏢 Stan's 133 Commercial &amp; Industrial War Room Portfolio</span>
            <span style="font-size: 11px; color: var(--text-muted); margin-left: 8px;">Total Capital: <b>{ds}5,045,679</b> &middot; Average Ticket: <b>{ds}37,937 / cert</b></span>
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
{comm_rows}
            </tbody>
          </table>
        </div>
        <div style="margin-top: 8px; font-size: 11px; color: var(--text-muted); text-align: right;">
          <i>Showing top 35 commercial items sorted by dollar amount. Full 133 items available in Stan's spreadsheets.</i>
        </div>
      </div>

      <!-- TAB 3: STAN'S REDLINE RULES & EXCLUSIONS -->
      <div id="{prefix}TabRedline" style="display: none; padding: 14px 20px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-bottom: 14px;">
          <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 12px; font-weight: 800; color: var(--danger);">🚫 Lake County: North Chicago Redline</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">37 Certs &middot; {ds}185,773</div>
            <div style="font-size: 11px; color: var(--text-muted);">Flagged: <code>"Do Not Buy - Redlined North Chgo"</code>. Severely distressed housing stock and chronic non-redemption risk.</div>
          </div>

          <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 12px; font-weight: 800; color: var(--warn);">⚠️ DuPage County: Open Prior Sold Taxes</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">8 Certs &middot; {ds}57,415</div>
            <div style="font-size: 11px; color: var(--text-muted);">Flagged: <code>"DNB - Open Sold Taxes"</code>. Prior unredeemed certificate sales that jeopardize senior lien priority.</div>
          </div>

          <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 12px; font-weight: 800; color: var(--danger);">🚫 Will County: South Suburban Redline</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">10 Certs &middot; {ds}52,349</div>
            <div style="font-size: 11px; color: var(--text-muted);">Flagged in Steger, University Park, and Park Forest. Zero commercial viability and title extinction risks.</div>
          </div>

          <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 12px; font-weight: 800; color: var(--accent);">🛡️ Total Capital Protected Across 4 Counties</div>
            <div style="font-size: 20px; font-weight: 800; color: var(--success); margin: 4px 0;">58 Certs &middot; {ds}315,630</div>
            <div style="font-size: 11px; color: var(--text-muted);">Stan's proprietary exclusions prevented Jennings from trapping {ds}315k into non-redeeming dead-end assets.</div>
          </div>
        </div>
      </div>

      <!-- Deep Analysis Commentary -->
      <div style="background: rgba(0, 0, 0, 0.25); border-top: 1px solid var(--border); padding: 14px 20px; font-size: 11.5px; line-height: 1.6; color: var(--text-muted);">
        <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">🔍 Complete Strategic Synthesis from Stan's 5 Excel Spreadsheets:</div>
        <div>1. <b>The &lt;{ds}3,000 Filter Rule:</b> Stan deliberately removes certs under {ds}3,000 where both installments are delinquent. This cut <b>336 certs ({ds}658,606)</b> across the 4 collar counties, preserving 98.5% of deployable capital while avoiding low-margin title/servicing overhead.</div>
        <div>2. <b>Commercial High-Yield Focus:</b> Commercial &amp; industrial certs account for only 2.3% of certificate count (133 certs) but generate <b>12.0% of all capital ({ds}5.05M)</b> with an average ticket of <b>{ds}37,937</b>. These represent Jennings' primary profit centers (hotels in Itasca, shopping centers in Roselle, AMC Naperville).</div>
        <div>3. <b>Why Volume Bidding is Required:</b> Last year Jennings won {ds}13.54M out of {ds}42.13M bid (~32% clearance rate). Bidding aggressively on {ds}42M+ across all 4 counties is essential to ensure Jennings deploys its full {ds}5.0M - {ds}6.5M capital allocation target against Bridge and Bass.</div>
      </div>
    </div>
  </div>
"""
    return html

# Doubled-braces for f-strings
stan_tab_js_fstring = """
function switchStanSubTab(prefix, tab) {{
    const tabs = ['rollup', 'comm', 'redline'];
    tabs.forEach(t => {{
        const pane = document.getElementById(prefix + 'Tab' + t.charAt(0).toUpperCase() + t.slice(1));
        const btn = document.getElementById(prefix + 'Btn' + t.charAt(0).toUpperCase() + t.slice(1));
        if (pane) pane.style.display = (t === tab) ? 'block' : 'none';
        if (btn) {{
            btn.className = (t === tab) ? 'btn btn-primary' : 'btn btn-outline';
        }}
    }});
}}
"""

def update_all():
    # 1. Update generate_tax_dashboard.py
    with open('generate_tax_dashboard.py', 'r') as f:
        tax_code = f.read()

    stan_tax_component = build_complete_stan_html(is_cfo_viewer=False)

    # In generate_tax_dashboard.py, replace the existing top section
    target_top = """  <!-- SECTION: STAN'S MASTER 2026 PRODUCTION BIDDING MODELS & 4-COUNTY ROLLUP (TOP LEAD) -->"""
    if target_top in tax_code:
        # replace from target_top to the start of Section 1
        end_target = """  <!-- SECTION 1: 2025 HISTORICAL INTELLIGENCE (LEADS WITH THIS - COLLAPSIBLE) -->"""
        idx1 = tax_code.find(target_top)
        idx2 = tax_code.find(end_target)
        if idx1 != -1 and idx2 != -1:
            tax_code = tax_code[:idx1] + stan_tax_component + "\n\n" + tax_code[idx2:]
            print("✅ Successfully updated Stan's complete data suite at the top of generate_tax_dashboard.py")

    # Inject JS switcher
    if "function switchStanSubTab" not in tax_code:
        tax_code = tax_code.replace("function toggleSection", stan_tab_js_fstring + "\nfunction toggleSection")
        print("✅ Injected switchStanSubTab JS into generate_tax_dashboard.py")

    with open('generate_tax_dashboard.py', 'w') as f:
        f.write(tax_code)

    # 2. Update generate_cfo_html_viewer.py
    with open('generate_cfo_html_viewer.py', 'r') as f:
        cfo_code = f.read()

    stan_cfo_component = build_complete_stan_html(is_cfo_viewer=True)

    # In CFO viewer, target_top
    target_top_cfo = """        <!-- 🎯 STAN'S MASTER 2026 BIDDING MODELS & 4-COUNTY ROLLUP (TOP LEAD) -->"""
    if target_top_cfo in cfo_code:
        cards_grid_target = """        <div class="cards-grid">
            <div class="stat-card">
                <div class="stat-card-label">Monday Redemptions (10/19)</div>"""
        idx1 = cfo_code.find(target_top_cfo)
        idx2 = cfo_code.find(cards_grid_target)
        if idx1 != -1 and idx2 != -1:
            cfo_code = cfo_code[:idx1] + stan_cfo_component + "\n\n" + cfo_code[idx2:]
            print("✅ Successfully updated Stan's complete data suite at the top of generate_cfo_html_viewer.py")

    # Inject JS switcher
    if "function switchStanSubTab" not in cfo_code:
        cfo_code = cfo_code.replace("function switchAuctionTab", stan_tab_js_fstring + "\nfunction switchAuctionTab")
        print("✅ Injected switchStanSubTab JS into generate_cfo_html_viewer.py")

    with open('generate_cfo_html_viewer.py', 'w') as f:
        f.write(cfo_code)

if __name__ == '__main__':
    update_all()
