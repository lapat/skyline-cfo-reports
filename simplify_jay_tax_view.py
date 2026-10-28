import re

def update_cfo_viewer():
    with open('generate_cfo_html_viewer.py', 'r') as f:
        code = f.read()

    # We want to wrap the Tax Activity View into two clean sub-views:
    # 1. taxCapitalView (Active by default for Jay):
    #    - Stat cards
    #    - Capital Stack & "Own Cash"
    #    - Mary's Daily Cash vs Certificate Payoffs
    #    - Subtax purchases deployed
    #    - Next-Auction Borrowing Capacity ($6.25M safe limit)
    #    - Stan's 4-County Production Bidding Models (Rollup Macro Table)
    #    - Callout banner linking to Stan's War Room & 1-click toggle to open Commander
    #
    # 2. taxCommanderView (Hidden by default or toggled):
    #    - Master Collar Counties Auction Commander with the 5 sub-tabs (Intel, Lake, DuPage, McHenry, Will, Subtax)

    # Let's find where the banner starts and where the two sections divide.
    # The dividing line is right above <!-- Master Collar Counties Auction Commander -->
    dividing_str = '        <!-- Master Collar Counties Auction Commander -->'

    if dividing_str not in code:
        print("❌ Could not find dividing_str in generate_cfo_html_viewer.py")
        return

    # Check if sub-view navigation is already injected
    if 'switchTaxPillarSubView' in code:
        print("Sub-view navigation already present, updating...")
    
    # 1. Inject the sub-view navigation right after <div class="entity-banner">...</div>
    banner_end = '        </div>\n\n        <div class="cards-grid">'
    
    nav_html = """        </div>

        <!-- Jay vs Stan Executive Sub-Navigation -->
        <div style="margin: 18px 0; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 6px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; gap: 6px;">
                <button id="btnTaxViewCapital" onclick="switchTaxPillarSubView('capital')" class="btn btn-primary" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px; border-radius: 6px;">🏛️ Jay's Tax Capital &amp; Liquidity (Executive)</button>
                <button id="btnTaxViewTactical" onclick="switchTaxPillarSubView('tactical')" class="btn btn-outline" style="font-size: 11.5px; font-weight: 700; padding: 6px 14px; border-radius: 6px;">🎯 Tactical Auction War Room (Stan's Underwriting)</button>
            </div>
            <div style="font-size: 11px; color: var(--text-muted); display: flex; align-items: center; gap: 8px;">
                <span>Jay's Focus: <b>Capital, Liquidity &amp; Borrowing Base</b></span>
                <a href="tax.html?passcode=Jennings2026" target="_blank" class="btn btn-primary" style="background: var(--purple); font-size: 10.5px; padding: 4px 10px; text-decoration: none; font-weight: 700;">⚡ Open Stan's Standalone Portal ↗</a>
            </div>
        </div>

        <!-- SUB-VIEW 1: JAY'S EXECUTIVE CAPITAL & LIQUIDITY (DEFAULT) -->
        <div id="taxSubViewCapital" style="display: block;">
            <div class="cards-grid">"""

    if banner_end in code:
        code = code.replace(banner_end, nav_html)
        print("✅ Injected sub-navigation and opened taxSubViewCapital")

    # 2. Close taxSubViewCapital and open taxSubViewTactical right at dividing_str
    # Inside the transition, we also add a prominent hand-off banner to Stan's War Room!
    handoff_html = """
            <!-- Stan's War Room Hand-off Banner -->
            <div style="background: rgba(139, 92, 246, 0.12); border: 1px solid rgba(139, 92, 246, 0.35); border-radius: 8px; padding: 18px 20px; margin-top: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="font-size: 14px; font-weight: 800; color: var(--text-primary); display: flex; align-items: center; gap: 8px;">
                        <span>🎯 Stan's Tactical Bidding &amp; Planning War Room</span>
                        <span class="badge badge-purple">Separate Operator Workbench</span>
                    </div>
                    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px; max-width: 680px; line-height: 1.5;">
                        To keep Jay's executive screen clean and uncluttered, the 268-parcel lien screener, 1-click Google Street View drive-bys, and state auction upload CSVs are housed in Stan's dedicated portal.
                    </div>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <a href="tax.html?passcode=Jennings2026" target="_blank" class="btn btn-primary" style="background: var(--accent); font-weight: 700; text-decoration: none; padding: 8px 16px; font-size: 12px;">⚡ Open Stan's War Room ↗</a>
                    <button onclick="switchTaxPillarSubView('tactical')" class="btn btn-outline" style="font-size: 12px; padding: 8px 14px;">📂 Expand Inside CFO Report</button>
                </div>
            </div>
        </div>

        <!-- SUB-VIEW 2: STAN'S TACTICAL AUCTION WAR ROOM (COLLAPSIBLE / SECONDARY) -->
        <div id="taxSubViewTactical" style="display: none;">
        <!-- Master Collar Counties Auction Commander -->"""

    if dividing_str in code:
        code = code.replace(dividing_str, handoff_html)
        print("✅ Injected handoff banner and divided into taxSubViewTactical")

    # 3. Add closing </div> for taxSubViewTactical at the very end of renderTaxActivityView
    # In generate_cfo_html_viewer.py, renderTaxActivityView ends right before setTimeout(() => { ... })
    # Let's find where the pane.innerHTML assignment ends:
    closing_pattern = r'(\s*</div>\s*`;\s*setTimeout\(\(\) => \{\{\s*switchAuctionTab\("intel"\);)'
    
    # We want to close taxSubViewTactical before the final </div> or before the closing backtick
    if re.search(closing_pattern, code):
        code = re.sub(closing_pattern, r'\n        </div>\1', code, count=1)
        print("✅ Closed taxSubViewTactical wrapper")

    # 4. Inject JavaScript function switchTaxPillarSubView(view)
    js_func = """
function switchTaxPillarSubView(view) {{
    const cap = document.getElementById('taxSubViewCapital');
    const tac = document.getElementById('taxSubViewTactical');
    const btnCap = document.getElementById('btnTaxViewCapital');
    const btnTac = document.getElementById('btnTaxViewTactical');

    if (view === 'capital') {{
        if (cap) cap.style.display = 'block';
        if (tac) tac.style.display = 'none';
        if (btnCap) {{ btnCap.className = 'btn btn-primary'; }}
        if (btnTac) {{ btnTac.className = 'btn btn-outline'; }}
    }} else {{
        if (cap) cap.style.display = 'none';
        if (tac) tac.style.display = 'block';
        if (btnCap) {{ btnCap.className = 'btn btn-outline'; }}
        if (btnTac) {{ btnTac.className = 'btn btn-primary'; }}
        // Ensure child tabs are initialized
        if (typeof switchAuctionTab === 'function') {{
            switchAuctionTab('intel');
        }}
    }}
}}
"""
    if "function switchTaxPillarSubView" not in code:
        # Inject right before switchAuctionTab
        code = code.replace("function switchAuctionTab", js_func + "\nfunction switchAuctionTab")
        print("✅ Injected switchTaxPillarSubView() JavaScript function")

    with open('generate_cfo_html_viewer.py', 'w') as f:
        f.write(code)
    print("✅ Successfully updated generate_cfo_html_viewer.py with Jay vs Stan dual view!")

if __name__ == '__main__':
    update_cfo_viewer()
