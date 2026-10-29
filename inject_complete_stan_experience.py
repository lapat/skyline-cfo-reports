import json
import re

def build_complete_stan_html(is_cfo_viewer=False):
    with open('stan_bidding_models.json') as f:
        stan_rollup = json.load(f)

    with open('stan_commercial_targets.json') as f:
        comm_targets = json.load(f)

    with open('stan_county_deep_strategies.json') as f:
        county_deep = json.load(f)

    with open('data/kendall_auction_results/kendall_results_2026.json') as f:
        kendall_data = json.load(f)

    with open('data/kendall_auction_results/kendall_class_codes_2026.json') as f:
        kendall_cc_data = json.load(f)

    with open('data/kendall_auction_results/kane_class_codes_2026.json') as f:
        kane_cc_data = json.load(f)

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

    # 2. Commercial rows
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

    # 3. County Deep Dive Cards
    deep_dive_cards = ""
    county_colors = {'Lake': '#3b82f6', 'DuPage': '#10b981', 'McHenry': '#f59e0b', 'Will': '#8b5cf6'}
    for cname, cinfo in county_deep.items():
        ccolor = county_colors.get(cname, 'var(--accent)')
        bid_pills = " ".join([f"<span class='badge badge-blue' style='font-size:10px;'>{k}%: <b>{v:,}</b></span>" for k, v in cinfo['bid_distribution'].items() if k])
        if not bid_pills:
            bid_pills = "<span class='badge badge-blue' style='font-size:10px;'>Selective Rates</span>"

        comm_pills = " ".join([f"<span class='badge badge-purple' style='font-size:9.5px;'>{k}: <b>{v}</b></span>" for k, v in cinfo['top_comments'].items() if k])

        items_html = ""
        for b in cinfo['breakdowns']:
            if b['label'] not in ['Category', 'Revised Total (keep)', 'Original Bid List Total', 'Non-Commercial breakdown by type', 'Non-Commercial breakdown by USE CODE', 'Commercial breakdown by USE CODE', 'Non-Commercial breakdown by ClassCode', 'Commercial breakdown by ClassCode', 'Flags in revised list']:
                amt_disp = f"${b['amount']:,.0f}" if isinstance(b['amount'], (int, float)) else str(b['amount'])
                if is_cfo_viewer:
                    amt_disp = amt_disp.replace('$', '$$')
                cnt_disp = f"{b['count']:,}" if isinstance(b['count'], int) else str(b['count'])
                items_html += f"<div style='display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span>{b['label']}</span><span><b>{cnt_disp}</b> ({amt_disp})</span></div>"

        deep_dive_cards += f"""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:16px; border-top:3px solid {ccolor};">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h4 style="margin:0; font-size:14px; color:{ccolor}; font-weight:800;">{cname} County Production Strategy</h4>
            <span class="badge badge-green" style="font-size:10px;">{cinfo['non_comm_count'] + cinfo['comm_count']:,} Kept</span>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-bottom:10px; line-height:1.4;">
            <b>Stan's Rule:</b> <i>{cinfo['rule']}</i>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Bid Distribution:</div>
            {bid_pills}
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Property &amp; Flag Breakdown:</div>
            {items_html}
          </div>
          {f"<div style='margin-top:6px;'><div style='font-size:10px; text-transform:uppercase; font-weight:700; color:var(--text-secondary); margin-bottom:4px;'>Stan's Key Tags:</div>{comm_pills}</div>" if comm_pills else ""}
        </div>
        """

    # 4. Kendall Results Table rows
    kendall_buyer_rows = ""
    for b in kendall_data.get('buyers', []):
        is_tot = b.get('is_total', False)
        style = "font-weight:800; background:rgba(255,255,255,0.06);" if is_tot else ""
        b_name = b['buyer_name']
        if 'PRIVATE EQUITY' in b_name:
            b_name = f"<b style='color:#ef4444;'>{b_name} (Bridge) ⚠️</b>"
        elif 'RAVEN' in b_name:
            b_name = f"<b style='color:#f59e0b;'>{b_name} (Bass)</b>"
        
        amt_disp = f"${b['amount_won']:,.2f}"
        if is_cfo_viewer:
            amt_disp = amt_disp.replace('$', '$$')

        kendall_buyer_rows += f"""
        <tr style="{style}">
          <td><code>{b['buyer_num']}</code></td>
          <td>{b_name}</td>
          <td class="right">{b['certs_won']}</td>
          <td class="right" style="font-weight:700;">{amt_disp}</td>
          <td class="right">{b['share_pct']}%</td>
          <td class="right"><span class="badge { 'badge-red' if b['wtd_avg_bid'] < 5.0 else 'badge-blue' }" style="font-weight:800;">{b['wtd_avg_bid']}%</span></td>
          <td class="right" style="color:var(--text-muted);">{b['min_bid']}% - {b['max_bid']}%</td>
        </tr>
        """

    # 4b. Kendall Use Code Breakdown rows
    kendall_cc_rows = ""
    for r in kendall_cc_data:
        amt_disp = f"${r['amount']:,.2f}"
        if is_cfo_viewer:
            amt_disp = amt_disp.replace('$', '$$')
        is_comm = r['use_code'] in ['50', '60', '70', '80']
        cc_badge = f"<span class='badge {'badge-purple' if is_comm else 'badge-blue'}' style='font-weight:800;'>Use {r['use_code']}</span>"
        kendall_cc_rows += f"""
        <tr>
          <td><b>{r['buyer']}</b></td>
          <td>{cc_badge} <span style="font-size:11px; color:var(--text-muted);">{r['desc']}</span></td>
          <td class="right">{r['certs']}</td>
          <td class="right" style="font-weight:700;">{amt_disp}</td>
          <td class="right"><span class="badge {'badge-red' if r['bid'] < 5.0 else 'badge-green'}" style="font-weight:800;">{r['bid']:.2f}%</span></td>
        </tr>
        """

    # 4c. Kane Class Code Breakdown rows
    kane_cc_rows = ""
    for r in kane_cc_data:
        amt_disp = f"${r['amount']:,.2f}"
        if is_cfo_viewer:
            amt_disp = amt_disp.replace('$', '$$')
        is_comm = r['class_code'] in ['50', '60', '70', '80']
        cc_badge = f"<span class='badge {'badge-purple' if is_comm else 'badge-blue'}' style='font-weight:800;'>Class {r['class_code']}</span>"
        kane_cc_rows += f"""
        <tr>
          <td><b>{r['buyer']}</b></td>
          <td>{cc_badge} <span style="font-size:11px; color:var(--text-muted);">{r['desc']}</span></td>
          <td class="right">{r['certs']}</td>
          <td class="right" style="font-weight:700;">{amt_disp}</td>
          <td class="right"><span class="badge {'badge-red' if r['bid'] < 5.0 else 'badge-green'}" style="font-weight:800;">{r['bid']:.2f}%</span></td>
        </tr>
        """

    # 5. Kane Buys rows
    kane_buys_data = [
        {"pin": "08-13-427-008", "owner": "BRINGAS, BRAULIO REVOC TR", "addr": "39W240 LONGMEADOW LN, ST CHARLES", "due": 16176.13, "bid": "5%", "bldg": 444179},
        {"pin": "09-04-302-001", "owner": "IZZO, THOMAS & TAYA", "addr": "7N475 HAMPTON DR, ST CHARLES", "due": 11317.40, "bid": "5%", "bldg": 273503},
        {"pin": "09-12-400-046", "owner": "HOLTZMAN, RICHARD & KATHY", "addr": "33W179 SURREY RD, WAYNE", "due": 10093.09, "bid": "5%", "bldg": 139219},
        {"pin": "09-24-150-016", "owner": "SCHUMACHER, BRAD G", "addr": "2504 ROYAL LYTHAM DR, ST CHARLES", "due": 11919.11, "bid": "5%", "bldg": 259905},
        {"pin": "10-22-100-001", "owner": "FLINT, G NADINE TR", "addr": "FARM PARCEL, KANE COUNTY", "due": 3558.68, "bid": "7%", "bldg": 32124},
        {"pin": "11-13-206-008", "owner": "BECKERMAN, BRETT", "addr": "0S140 N MATHEWSON LN, GENEVA", "due": 11031.04, "bid": "5%", "bldg": 238236},
        {"pin": "11-13-300-016", "owner": "RITSCHDORFF, MICHAEL IRREVOC TR", "addr": "39W796 FABYAN PKWY, ELBURN", "due": 11162.44, "bid": "5%", "bldg": 228694},
        {"pin": "12-31-173-014", "owner": "GUERRERO, H & LOPEZ, CLAUDIA", "addr": "960 N DEERPATH RD, NORTH AURORA", "due": 11208.90, "bid": "5%", "bldg": 277924}
    ]

    kane_rows = ""
    for k in kane_buys_data:
        k_due = f"${k['due']:,.2f}"
        if is_cfo_viewer:
            k_due = k_due.replace('$', '$$')
        k_bldg = f"${k['bldg']:,}"
        if is_cfo_viewer:
            k_bldg = k_bldg.replace('$', '$$')

        kane_rows += f"""
        <tr>
          <td><code style="font-weight:700;">{k['pin']}</code></td>
          <td><b>{k['owner']}</b><div style="font-size:10.5px; color:var(--text-muted);">{k['addr']}</div></td>
          <td class="right" style="font-weight:800; color:var(--success);">{k_due}</td>
          <td class="right"><span class="badge badge-green" style="font-weight:800;">{k['bid']}</span></td>
          <td class="right">{k_bldg}</td>
          <td><span class="badge badge-purple" style="font-size:9px;">Diamond Quest (180)</span></td>
        </tr>
        """

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
          Complete dataset parsed from Stan's production Excel models, Kane results, and live Kendall auction intelligence emailed to Louis &amp; Jay.
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
          <div style="font-size: 11px; color: #f87171; text-transform: uppercase; font-weight: 700;">Live 2026 Auction Intel</div>
          <div style="font-size: 22px; font-weight: 800; color: #f87171; margin: 4px 0;">Kendall &amp; Kane 2026</div>
          <div style="font-size: 11px; color: var(--text-secondary);">Bridge swept Kendall @ 4.95% &middot; <b>Jay Mandate: 5% Flat</b></div>
        </div>
      </div>

      <!-- Stan Multi-Tab Navigation (5 Rich Views) -->
      <div style="display: flex; gap: 8px; padding: 0 20px 12px 20px; border-bottom: 1px solid var(--border); flex-wrap: wrap;">
        <button id="{prefix}BtnRollup" onclick="switchStanSubTab('{prefix}', 'rollup')" class="btn btn-primary" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">📊 4-County Master Rollup</button>
        <button id="{prefix}BtnDeep" onclick="switchStanSubTab('{prefix}', 'deep')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">🗺️ County Strategy Deep Dives</button>
        <button id="{prefix}BtnComm" onclick="switchStanSubTab('{prefix}', 'comm')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">🏢 133 Prime Commercial Targets ({ds}5.05M)</button>
        <button id="{prefix}BtnRedline" onclick="switchStanSubTab('{prefix}', 'redline')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">⚠️ Stan's Redlines &amp; Exclusions (58 Parcels)</button>
        <button id="{prefix}BtnKane" onclick="switchStanSubTab('{prefix}', 'kane')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px;">🔥 Live 2026 Intel (Kendall &amp; Kane)</button>
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

      <!-- TAB 2: COUNTY STRATEGY DEEP DIVES -->
      <div id="{prefix}TabDeep" style="display: none; padding: 14px 20px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">
          {deep_dive_cards}
        </div>
      </div>

      <!-- TAB 3: 133 PRIME COMMERCIAL TARGETS TABLE -->
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

      <!-- TAB 4: STAN'S REDLINE RULES & EXCLUSIONS -->
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

      <!-- TAB 5: LIVE 2026 AUCTION INTEL (KENDALL & KANE) -->
      <div id="{prefix}TabKane" style="display: none; padding: 14px 20px;">
        <!-- KENDALL 2026 RESULTS (THE WAKE-UP CALL) -->
        <div style="background: rgba(239, 68, 68, 0.08); border: 1.5px solid rgba(239, 68, 68, 0.35); border-radius: 8px; padding: 16px; margin-bottom: 18px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
            <div>
              <span style="font-size: 14px; font-weight: 800; color: #fca5a5;">🚨 Kendall County 2026 Sale Results (Oct 26, 2026) — The Wake-Up Call</span>
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 3px;">
                Jennings bid 179 items ({ds}1.495M) at 6% to 9% &middot; <b style="color:var(--danger);">WON 0 ITEMS ({ds}0.00 DEPLOYED)</b>
              </div>
            </div>
            <span class="badge badge-red" style="font-size: 11px; font-weight: 800;">Market Cleared @ 4.88% Wtd Avg</span>
          </div>

          <div style="background: rgba(0,0,0,0.25); border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; font-size: 11.5px; line-height: 1.5; color: #fecaca; border-left: 3px solid #ef4444;">
            <b>Jay's Immediate Executive Directive to Stan:</b> <i>"Yeah - so it’s 4’s and 5’s most likely... We are going to bid 5 moving forward so that will be our rate and I will send over the bid ladder so once we have it all approved, we just put in 5."</i>
            <div style="margin-top: 4px; font-size: 11px; color: var(--text-muted);">
              <b>Stan's Intel Note:</b> <i>"Bridge took it at 5 but he bid some 4's too. I'm sure he regrets the 4's."</i> Bridge (Private Equity Group) swept half the auction (49.7%) at 4.95%, and Bass (Raven) swept 13.1% at 4.12%.
            </div>
          </div>

          <div class="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Buyer #</th>
                  <th>Buyer Name / Competitor</th>
                  <th class="right">Certs Won</th>
                  <th class="right">Amount Won</th>
                  <th class="right">Market Share</th>
                  <th class="right">Wtd Avg Bid</th>
                  <th class="right">Bid Range</th>
                </tr>
              </thead>
              <tbody>
{kendall_buyer_rows}
              </tbody>
            </table>
          </div>

          <!-- KENDALL USE CODE BREAKDOWN (STAN INTEL) -->
          <div style="margin-top: 14px; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 12px; border-left: 3px solid #8b5cf6;">
            <div style="font-size: 12px; font-weight: 800; color: #c4b5fd; margin-bottom: 4px;">
              🏢 Kendall Use Code Breakdown — Competitor Asset Pricing
            </div>
            <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 8px;">
              <b>Stan's Direct Email Intel:</b> <i>"Bridge bought commercials at 4 and 5."</i> Confirms Bridge selectively bid 4.69% on Use Code 60 (Commercial) and 4.63% on Use Code 80 (Industrial).
            </div>
            <div class="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Tax Buyer</th>
                    <th>Use Code &amp; Description</th>
                    <th class="right">Certs Won</th>
                    <th class="right">Total Amount</th>
                    <th class="right">Wtd Avg Bid</th>
                  </tr>
                </thead>
                <tbody>
{kendall_cc_rows}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- KANE 2026 LIVE BUYS BENCHMARK -->
        <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
            <div>
              <span style="font-size: 13.5px; font-weight: 800; color: #6ee7b7;">💎 Kane County 2026 Auction Results — Diamond Quest Realty Buys</span>
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 3px;">
                Executed Oct 27, 2026 &middot; 8 Certificates &middot; <b>{ds}86,467 Capital Deployed</b> &middot; <b style="color:var(--success);">100% Won at 5.0% - 7.0% Bid Rates</b>
              </div>
            </div>
            <span class="badge badge-green" style="font-size: 10.5px; font-weight: 800;">5.0% Cleared Market</span>
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
{kane_rows}
              </tbody>
            </table>
          </div>
          <div style="margin-top: 8px; font-size: 11px; color: var(--text-muted);">
            📌 <i>Stan's email to Jay: "Below are the 8 items we bought. They look fine. No mistakes." Confirms Jennings cleared 5.0% bids on high-equity St. Charles &amp; Geneva residential parcels.</i>
          </div>
        </div>

        <!-- KANE COMPETITOR CLASS CODE BREAKDOWN -->
        <div style="margin-top: 18px; background: rgba(59, 130, 246, 0.08); border: 1.5px solid rgba(59, 130, 246, 0.35); border-radius: 8px; padding: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
            <div>
              <span style="font-size: 13.5px; font-weight: 800; color: #93c5fd;">📊 Kane County Class Code Pricing Breakdown (Bridge &amp; Heartland Intel)</span>
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 3px;">
                Emailed by Stan Engelsen &middot; Analyzes 1,676 certificates ({ds}9.79M total auction) by property classification
              </div>
            </div>
            <span class="badge badge-blue" style="font-size: 10.5px; font-weight: 800;">Class Code Intel</span>
          </div>
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 10px; line-height: 1.5;">
            <b>Key Finding:</b> Heartland dominated residential (Class 40) at an ultra-low <b>2.95%</b>, while Bridge swept commercial (Class 60) at <b>4.67%</b> and industrial (Class 80) at <b>4.57%</b>.
          </div>
          <div class="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Tax Buyer</th>
                  <th>Class Code &amp; Description</th>
                  <th class="right">Certs Won</th>
                  <th class="right">Total Amount</th>
                  <th class="right">Wtd Avg Bid</th>
                </tr>
              </thead>
              <tbody>
{kane_cc_rows}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Deep Analysis Commentary -->
      <div style="background: rgba(0, 0, 0, 0.25); border-top: 1px solid var(--border); padding: 14px 20px; font-size: 11.5px; line-height: 1.6; color: var(--text-muted);">
        <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">🔍 Complete Strategic Synthesis from Stan's Spreadsheets &amp; Live 2026 Auctions:</div>
        <div>1. <b>The &lt;{ds}3,000 Filter Rule:</b> Stan deliberately removes certs under {ds}3,000 where both installments are delinquent. This cut <b>336 certs ({ds}658,606)</b> across the 4 collar counties, preserving 98.5% of deployable capital while avoiding low-margin title/servicing overhead.</div>
        <div>2. <b>Jay's 5.0% Bidding Mandate:</b> Kendall County proved that bidding 6%-9% results in 0% clearance against Private Equity Group (Bridge) and Raven (Bass). Jay's directive to bid 5.0% flat ensures Jennings clears its target capital while earning +552 bps net carry over borrowing costs.</div>
        <div>3. <b>Commercial High-Yield Focus:</b> Commercial &amp; industrial certs account for only 2.3% of certificate count (133 certs) but generate <b>12.0% of all capital ({ds}5.05M)</b> with an average ticket of <b>{ds}37,937</b>.</div>
      </div>
    </div>
  </div>
"""
    return html

stan_tab_js_fstring = """
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
"""

def update_all():
    # 1. Update generate_tax_dashboard.py
    with open('generate_tax_dashboard.py', 'r') as f:
        tax_code = f.read()

    stan_tax_component = build_complete_stan_html(is_cfo_viewer=False)

    target_top = """  <!-- SECTION: STAN'S MASTER 2026 PRODUCTION BIDDING MODELS & 4-COUNTY ROLLUP (COMPLETE DATA SUITE) -->"""
    end_target = """  <!-- SECTION 1: 2025 HISTORICAL INTELLIGENCE (LEADS WITH THIS - COLLAPSIBLE) -->"""
    idx1 = tax_code.find(target_top)
    idx2 = tax_code.find(end_target)
    if idx1 != -1 and idx2 != -1:
        tax_code = tax_code[:idx1] + stan_tax_component + "\n\n" + tax_code[idx2:]
        print("✅ Injected Kendall & Kane 2026 Intel into generate_tax_dashboard.py")

    # Update default lakeRatePreset to Jay's 5% Mandate
    old_preset_select = """        <select id="lakeRatePreset" class="filter-select" onchange="renderLakeTargetTable()" style="border-color:rgba(16,185,129,0.5);">
          <option value="standard" selected>Strategy: 4% on >=$25k (Beat Bridge) / 5% on $10k-$25k</option>
          <option value="aggressive">Aggressive: 3% on >=$25k / 4% on $10k-$25k</option>
          <option value="flat4">Universal: 4% Flat on All Items</option>
          <option value="flat5">Match Market: 5% Flat on All Items</option>
        </select>"""

    new_preset_select = """        <select id="lakeRatePreset" class="filter-select" onchange="renderLakeTargetTable()" style="border-color:rgba(16,185,129,0.8); font-weight:700;">
          <option value="flat5" selected>⭐ Jay's Mandate: 5.0% Flat to Clear Market</option>
          <option value="standard">Aggressive Spread: 4.0% on >=$25k / 5.0% on $10k-$25k</option>
          <option value="aggressive">Ultra-Aggressive: 3.0% on >=$25k / 4.0% on $10k-$25k</option>
          <option value="flat4">Universal: 4.0% Flat on All Items</option>
        </select>"""

    if old_preset_select in tax_code:
        tax_code = tax_code.replace(old_preset_select, new_preset_select)
        print("✅ Set Jay's Mandate (5.0% Flat) as default rate preset in generate_tax_dashboard.py")

    with open('generate_tax_dashboard.py', 'w') as f:
        f.write(tax_code)

    # 2. Update generate_cfo_html_viewer.py
    with open('generate_cfo_html_viewer.py', 'r') as f:
        cfo_code = f.read()

    stan_cfo_component = build_complete_stan_html(is_cfo_viewer=True)

    target_top_cfo = """  <!-- SECTION: STAN'S MASTER 2026 PRODUCTION BIDDING MODELS & 4-COUNTY ROLLUP (COMPLETE DATA SUITE) -->"""
    cards_grid_target = """        <div class="cards-grid">
            <div class="stat-card">
                <div class="stat-card-label">Monday Redemptions (10/19)</div>"""
    idx1 = cfo_code.find(target_top_cfo)
    idx2 = cfo_code.find(cards_grid_target)
    if idx1 != -1 and idx2 != -1:
        cfo_code = cfo_code[:idx1] + stan_cfo_component + "\n\n" + cfo_code[idx2:]
        print("✅ Injected Kendall & Kane 2026 Intel into generate_cfo_html_viewer.py")

    with open('generate_cfo_html_viewer.py', 'w') as f:
        f.write(cfo_code)

if __name__ == '__main__':
    update_all()
