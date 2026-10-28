import re

def inject_region_map():
    with open('generate_tax_dashboard.py', 'r') as f:
        code = f.read()

    # The region map HTML component
    map_html = """
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

                <!-- [09] Waukegan (REDLINE RISK) -->
                <div onclick="selectTownshipFilter('waukegan')" style="cursor: pointer; background: rgba(239, 68, 68, 0.12); border: 2px solid #ef4444; border-radius: 6px; padding: 10px 12px; box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); transition: transform 0.15s;" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='scale(1.0)';">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; font-weight: 800; color: #f87171;">[08 / 09] WAUKEGAN ⚠️</span>
                        <span class="badge badge-red" style="font-size: 8.5px; padding: 1px 4px;">90.0% Tier 3</span>
                    </div>
                    <div style="font-size: 11.5px; font-weight: 700; color: #fca5a5; margin-top: 3px;">Waukegan Coastal City</div>
                    <div style="font-size: 9.5px; color: #fca5a5; margin-top: 2px;">Watch Water Liens &middot; 8 SIEs</div>
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
"""

    target_heading = '<div style="font-size:12px; font-weight:700; color:var(--text-secondary); margin-bottom:8px;">🏛️ 15-Year Historical Redemption Safety by Township (PIN Prefix) — Lake County:</div>'
    if target_heading in code:
        code = code.replace(target_heading, target_heading + "\n" + map_html)
        print("✅ Injected Visual Lake County Region Heatmap into generate_tax_dashboard.py")
    else:
        print("❌ Could not find target_heading in generate_tax_dashboard.py")

    # Inject selectTownshipFilter JS function
    js_func = """
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
"""
    if "function selectTownshipFilter" not in code:
        code = code.replace("function copyPin", js_func + "\nfunction copyPin")
        print("✅ Injected selectTownshipFilter() JS function")

    with open('generate_tax_dashboard.py', 'w') as f:
        f.write(code)

if __name__ == '__main__':
    inject_region_map()
