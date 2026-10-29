import json
import re

def update_generators():
    with open('stan_bidding_models.json') as f:
        stan_data = json.load(f)

    # Prepare HTML table for Stan's Rollup
    rows = ""
    for c in stan_data['rollup']:
        is_total = c['county'] == 'Total'
        style = "font-weight:800; background:rgba(255,255,255,0.05);" if is_total else ""
        c_badge = "<span class='badge badge-purple'>4-County Rollup</span>" if is_total else f"<b>{c['county']}</b>"
        
        rows += f"""
        <tr style="{style}">
            <td>{c_badge}</td>
            <td class="right">{c['non_commercial']['count']:,}</td>
            <td class="right">${c['non_commercial']['amount']:,.2f}</td>
            <td class="right">{c['commercial']['count']:,}</td>
            <td class="right" style="color:var(--accent); font-weight:700;">${c['commercial']['amount']:,.2f}</td>
            <td class="right" style="color:var(--success); font-weight:800;">{c['revised_total']['count']:,}</td>
            <td class="right" style="color:var(--success); font-weight:800;">${c['revised_total']['amount']:,.2f}</td>
            <td class="right" style="color:var(--text-muted);">{c['removed_under_3k']['count']:,}</td>
            <td class="right" style="color:var(--text-muted);">${c['removed_under_3k']['amount']:,.2f}</td>
            <td class="right" style="color:var(--text-primary);">{c['original_total']['count']:,}</td>
            <td class="right" style="color:var(--text-primary);">${c['original_total']['amount']:,.2f}</td>
        </tr>
        """

    stan_table_html = f"""
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
            {rows}
          </tbody>
        </table>
      </div>
      <div style="margin-top:10px; font-size:11px; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <div>📌 <i>Directly extracted from Stan's <code>4_County_2025_Sale_Revised_Rollup Claude Analysis.xlsx</code> model sent to Louis &amp; Jay.</i></div>
        <div><b>Commercial Average Ticket:</b> <span style="color:var(--accent); font-weight:700;">$37,937 / cert</span> (133 prime targets across 4 counties)</div>
      </div>
    </div>
  </div>
"""

    # 1. Update generate_tax_dashboard.py
    with open('generate_tax_dashboard.py') as f:
        tax_code = f.read()

    # Inject Stan's table right before Section 3
    sec3_target = '  <!-- SECTION 3: UPCOMING COLLAR COUNTIES SCHEDULE'
    if sec3_target in tax_code and "Stan's Master 2025 Bidding Models" not in tax_code:
        tax_code = tax_code.replace(sec3_target, stan_table_html + "\n" + sec3_target)
        print("✅ Injected Stan's Rollup into generate_tax_dashboard.py")

    with open('generate_tax_dashboard.py', 'w') as f:
        f.write(tax_code)

    # 2. Update generate_cfo_html_viewer.py
    with open('generate_cfo_html_viewer.py') as f:
        cfo_code = f.read()

    # Inject Stan's table right before TAB 3: DuPage County Placeholder
    cfo_target = '            <!-- TAB 3: DuPage County Placeholder -->'
    if cfo_target in cfo_code and "Stan's Master 2025 Bidding Models" not in cfo_code:
        cfo_code = cfo_code.replace(cfo_target, stan_table_html + "\n" + cfo_target)
        print("✅ Injected Stan's Rollup into generate_cfo_html_viewer.py")

    with open('generate_cfo_html_viewer.py', 'w') as f:
        f.write(cfo_code)

if __name__ == '__main__':
    update_generators()
