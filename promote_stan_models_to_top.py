import json
import re

def build_master_stan_component(is_cfo_viewer=False):
    with open('stan_bidding_models.json') as f:
        stan_data = json.load(f)

    # Build rows
    rows = ""
    for c in stan_data['rollup']:
        is_total = c['county'] == 'Total'
        style = "font-weight:800; background:rgba(255,255,255,0.06);" if is_total else ""
        c_badge = "<span class='badge badge-purple' style='font-size:11px; font-weight:800;'>4-County Rollup Total</span>" if is_total else f"<b>{c['county']}</b>"
        
        # Format amounts
        non_comm_amt = f"${c['non_commercial']['amount']:,.2f}"
        comm_amt = f"${c['commercial']['amount']:,.2f}"
        rev_amt = f"${c['revised_total']['amount']:,.2f}"
        rem_amt = f"${c['removed_under_3k']['amount']:,.2f}"
        orig_amt = f"${c['original_total']['amount']:,.2f}"

        # In CFO viewer f-string, we must escape dollar signs if inside f-string or just use raw strings
        if is_cfo_viewer:
            non_comm_amt = non_comm_amt.replace('$', '$$')
            comm_amt = comm_amt.replace('$', '$$')
            rev_amt = rev_amt.replace('$', '$$')
            rem_amt = rem_amt.replace('$', '$$')
            orig_amt = orig_amt.replace('$', '$$')

        rows += f"""
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

    # Top KPI cards for the Stan Component
    ds = "$$" if is_cfo_viewer else "$"
    
    html = f"""
  <!-- SECTION: STAN'S MASTER 2026 PRODUCTION BIDDING MODELS & 4-COUNTY ROLLUP (TOP LEAD) -->
  <div class="section-card" style="border: 2px solid rgba(139, 92, 246, 0.55); background: linear-gradient(135deg, rgba(30, 27, 75, 0.35), rgba(15, 23, 42, 0.45)); margin-bottom: 24px; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.15);">
    <div class="section-header" style="background: rgba(139, 92, 246, 0.2); padding: 14px 20px; cursor: pointer;" onclick="toggleSection('secBodyStanTop', 'secIconStanTop')">
      <div>
        <div class="section-title" style="color: #c4b5fd; font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
          <span>🎯 Stan's Master 2026 Bidding Models &amp; 4-County Production Rollup</span>
          <span class="badge badge-purple" style="font-size: 10px; font-weight: 800;">Jay's 2026 Bidding Blueprint</span>
        </div>
        <div class="section-desc" style="color: var(--text-muted); font-size: 12px; margin-top: 3px;">
          Directly parsed from Stan's production Excel models emailed to Louis &amp; Jay. Defines Jennings' revised baseline across Lake, DuPage, McHenry, and Will.
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 10px;">
        <span class="badge badge-green" style="font-size: 12px; font-weight: 800; padding: 6px 12px;">Revised Upload: 5,656 Certs &middot; {ds}42.13M</span>
        <span id="secIconStanTop" style="font-size: 14px; color: var(--text-muted); font-weight: 700;">▲</span>
      </div>
    </div>
    
    <div id="secBodyStanTop">
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

      <!-- Master 4-County Rollup Table -->
      <div class="table-responsive" style="padding: 0 20px 14px 20px;">
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
{rows}
          </tbody>
        </table>
      </div>

      <!-- Deep Analysis Commentary -->
      <div style="background: rgba(0, 0, 0, 0.2); border-top: 1px solid var(--border); padding: 14px 20px; font-size: 11.5px; line-height: 1.6; color: var(--text-muted);">
        <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">🔍 Strategic Synthesis from Stan's Spreadsheets for Jay &amp; Louis:</div>
        <div>1. <b>The &lt;{ds}3,000 Filter Rule:</b> Stan deliberately removes certs under {ds}3,000 where both installments are delinquent. This cut <b>336 certs ({ds}658,606)</b> across the 4 collar counties, preserving 98.5% of deployable capital while avoiding low-margin title/servicing overhead.</div>
        <div>2. <b>Commercial High-Yield Focus:</b> Commercial &amp; industrial certs account for only 2.3% of certificate count (133 certs) but generate <b>12.0% of all capital ({ds}5.05M)</b> with an average ticket of <b>{ds}37,937</b>. These represent Jennings' primary profit centers.</div>
        <div>3. <b>Why Volume Bidding is Required:</b> Last year Jennings won {ds}13.54M out of {ds}42.13M bid (~32% clearance rate). Bidding aggressively on {ds}42M+ across all 4 counties is essential to ensure Jennings deploys its full {ds}5.0M - {ds}6.5M capital allocation target against Bridge and Bass.</div>
      </div>
    </div>
  </div>
"""
    return html

def update_all():
    # 1. Update generate_tax_dashboard.py
    with open('generate_tax_dashboard.py', 'r') as f:
        tax_code = f.read()

    # Remove any existing Stan master component
    tax_code = re.sub(r'  <!-- SECTION: STAN\'S MASTER 4-COUNTY PRODUCTION BIDDING MODELS -->.*?</div>\s*</div>\s*</div>', '', tax_code, flags=re.DOTALL)
    tax_code = re.sub(r'  <!-- SECTION: STAN\'S MASTER 2026 PRODUCTION BIDDING MODELS & 4-COUNTY ROLLUP \(TOP LEAD\) -->.*?</div>\s*</div>\s*</div>', '', tax_code, flags=re.DOTALL)

    stan_tax_component = build_master_stan_component(is_cfo_viewer=False)

    # Place at the very top of the body, right after the metric cards grid
    metric_grid_end = '    <div class="metric-box">\n      <div class="metric-label">Next Sale (Lake County)</div>\n      <div class="metric-val">Fri, Nov 13</div>\n      <div class="metric-note" style="color:#fbbf24;">Target Spend: $2,000,000</div>\n    </div>\n  </div>'
    
    if metric_grid_end in tax_code:
        tax_code = tax_code.replace(metric_grid_end, metric_grid_end + "\n\n" + stan_tax_component)
        print("✅ Injected Stan's Master 2026 Bidding Models at the top of generate_tax_dashboard.py")
    else:
        print("❌ Could not find metric_grid_end in generate_tax_dashboard.py")

    with open('generate_tax_dashboard.py', 'w') as f:
        f.write(tax_code)

    # 2. Update generate_cfo_html_viewer.py
    with open('generate_cfo_html_viewer.py', 'r') as f:
        cfo_code = f.read()

    # Remove old lower placement of Stan table in CFO viewer
    cfo_code = re.sub(r'        <!-- Stan\'s Master 4-County Production Bidding Models Table \(Summary View\) -->.*?</div>\s*</div>\s*</div>', '', cfo_code, flags=re.DOTALL)
    cfo_code = re.sub(r'  <!-- SECTION: STAN\'S MASTER 2026 PRODUCTION BIDDING MODELS & 4-COUNTY ROLLUP \(TOP LEAD\) -->.*?</div>\s*</div>\s*</div>', '', cfo_code, flags=re.DOTALL)

    stan_cfo_component = build_master_stan_component(is_cfo_viewer=True)

    # Place right at the top of renderTaxActivityView, right after the entity banner
    cfo_banner_end = '            <h2>Tax Certificate Lien Portfolio — Live Cash Flow & Redemptions</h2>\n            <p>Real-time visibility into certificate payoffs, weekly bank clearing, and capital deployed across Interstate Funding (150), Central Buyer (160), Diamond Quest (180), and Union Tax (190).</p>\n        </div>'

    if cfo_banner_end in cfo_code:
        cfo_code = cfo_code.replace(cfo_banner_end, cfo_banner_end + "\n\n" + stan_cfo_component)
        print("✅ Injected Stan's Master 2026 Bidding Models at the top of generate_cfo_html_viewer.py")
    else:
        print("❌ Could not find cfo_banner_end in generate_cfo_html_viewer.py")

    with open('generate_cfo_html_viewer.py', 'w') as f:
        f.write(cfo_code)

if __name__ == '__main__':
    update_all()
