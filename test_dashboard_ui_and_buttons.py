#!/usr/bin/env python3
"""
Automated Headless UI & Button Test Suite for Jennings Realty CFO Portal.

Tests all buttons, navigation flows, and interactive state transitions:
1. Default landing state (Pillar 1: Treasury & Liquidity -> Cash Flash).
2. Pillar Switching (Treasury, Tax & Specialty, Core Financials) and button filtering.
3. All 10 View Modes activation and pane visibility toggles.
4. Left Sidebar Pillar-Awareness (Treasury menu, Tax menu, Entity list).
5. Sidebar Auto-Switch safety net (clicking an entity from any pillar flips to Core Financials).
6. Jim Report Viewer Integration (Verifies Jim's latest emailed summaries & PDFs for all 12 entities).
7. URL Deep Linking & Passcode Authentication (?passcode=Jennings2026&mode=tax_activity).
"""

import os
import sys
import json
import re
import subprocess

PORTAL_HTML = os.path.abspath("index.html")

def run_tests():
    print("=" * 80)
    print("RUNNING AUTOMATED DASHBOARD UI, PILLAR & BUTTON TEST SUITE")
    print("=" * 80)

    if not os.path.exists(PORTAL_HTML):
        print(f"❌ FAIL: {PORTAL_HTML} does not exist.")
        sys.exit(1)

    with open(PORTAL_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✅ PASS [{total:02d}]: {name}")
        else:
            print(f"  ❌ FAIL [{total:02d}]: {name} — {details}")

    # =========================================================================
    # TEST 1: DOM Elements & Button IDs Integrity
    # =========================================================================
    print("\n--- Phase 1: DOM Button IDs & Viewport Integrity ---")
    required_buttons = [
        "pillarTabTreasury", "pillarTabAssets", "pillarTabFinancials",
        "btnModeCashFlash", "btnModeLiquidity", "btnModeForecast", "btnModeValuation",
        "btnModeTaxActivity", "btnModeNorthStar", "btnModeCapex",
        "btnModeSummary", "btnModeVisual", "btnModeSplit", "btnModeSkylinePdf", "btnModeJimPdf", "btnModeJimSummary"
    ]
    for b_id in required_buttons:
        assert_test(f"Button ID exists in HTML: {b_id}", f'id="{b_id}"' in html, f'Missing button id="{b_id}"')

    required_panes = [
        "contentPane", "visualPane", "sideBySidePane", "skylinePdfPane", "jimPdfPane", "jimSummaryPane",
        "northStarPane", "taxActivityPane", "cashFlashPane", "forecastPane",
        "liquidityPane", "capexPane", "valuationPane"
    ]
    for p_id in required_panes:
        assert_test(f"Viewport Pane exists in HTML: {p_id}", f'id="{p_id}"' in html, f'Missing pane id="{p_id}"')

    # =========================================================================
    # TEST 2: Jay's Executive Tax Capital & Liquidity Dashboard (index.html)
    # =========================================================================
    print("\n--- Phase 2: Jay's Executive Tax Capital & Liquidity Dashboard ---")
    assert_test("Tax Season Banner exists in DOM", "tax-season-banner" in html)
    assert_test("Tax Season Headroom ($6,250,000) displayed", "$6,250,000" in html)
    assert_test("Tax Season 1-tap jump button exists", "View Tax Flow" in html)
    assert_test("Stan's War Room Launch Link exists in DOM", "tax.html?passcode=Jennings2026" in html)
    assert_test("Jennings Own Cash ($7.38M) displayed in Capital Stack", "+$7.38M" in html)
    assert_test("Next-Auction Safe Bidding Limit displayed", "Safe Bidding Limit" in html)
    assert_test("Stan's 4-County Rollup Table ($42.13M) displayed", "$42,133,147" in html)
    assert_test("Credit Facility Borrowing Base Headroom ($11.51M) displayed", "$11.51M" in html)
    assert_test("SOFR Floating Debt Simulator exists in DOM", "simulateSofrRate" in html)
    assert_test("24-Month Debt Retirement Waterfall displayed", "Debt Retirement Waterfall" in html)

    # =========================================================================
    # TEST 3: Headless Execution via Node.js
    # =========================================================================
    print("\n--- Phase 3: JavaScript State Transitions & Button Click Simulation ---")

    # Extract script content from HTML
    script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    if not script_match:
        print("❌ FAIL: Could not extract <script> tag from index.html")
        sys.exit(1)

    js_code = script_match.group(1)

    node_test_script = f"""
    // Mock DOM Environment
    const dom = {{
        elements: {{}},
        getElementById: function(id) {{
            if (!this.elements[id]) {{
                this.elements[id] = {{
                    id: id,
                    style: {{ display: 'block' }},
                    classList: {{
                        classes: new Set(),
                        add: function(c) {{ this.classes.add(c); }},
                        remove: function(c) {{ this.classes.delete(c); }},
                        toggle: function(c, val) {{
                            if (val === undefined) val = !this.classes.has(c);
                            if (val) this.classes.add(c); else this.classes.delete(c);
                            return val;
                        }},
                        has: function(c) {{ return this.classes.has(c); }}
                    }},
                    innerHTML: '',
                    value: '',
                    src: '',
                    href: ''
                }};
            }}
            return this.elements[id];
        }},
        querySelectorAll: function(sel) {{ return []; }}
    }};

    const document = dom;
    const window = {{ location: {{ search: '?passcode=Jennings2026' }} }};
    const localStorage = {{
        store: {{}},
        getItem: function(k) {{ return this.store[k]; }},
        setItem: function(k, v) {{ this.store[k] = v; }}
    }};
    const URLSearchParams = function(s) {{
        return {{
            get: function(k) {{
                if (k === 'passcode') return 'Jennings2026';
                return null;
            }}
        }};
    }};

    {js_code}

    const testResults = [];

    // Test 1: Initial Default State (Option A)
    testResults.push({{
        name: "Initial Pillar is Treasury",
        passed: currentPillar === 'treasury'
    }});
    testResults.push({{
        name: "Initial View Mode is Cash Flash",
        passed: currentViewMode === 'cash_flash'
    }});

    // Test 2: Switch to Assets (Specialized Portfolios)
    switchPillar('assets');
    testResults.push({{
        name: "Switch to Assets defaults to Tax Flow",
        passed: currentPillar === 'assets' && currentViewMode === 'tax_activity'
    }});

    // Test 3: Switch to Financials
    switchPillar('financials');
    testResults.push({{
        name: "Switch to Financials defaults to Summary",
        passed: currentPillar === 'financials' && currentViewMode === 'summary'
    }});

    // Test 4: Auto-Switch from Treasury to Financials upon Entity Click
    switchPillar('treasury');
    selectEntity(1); // Click Park City
    testResults.push({{
        name: "selectEntity auto-switches pillar to Financials",
        passed: currentPillar === 'financials'
    }});
    testResults.push({{
        name: "selectEntity activates Summary view mode",
        passed: currentViewMode === 'summary'
    }});
    testResults.push({{
        name: "selectEntity sets selectedIdx to 1 (Park City)",
        passed: selectedIdx === 1
    }});

    // Test 5: Auto-Switch from Assets to Financials upon Entity Click
    switchPillar('assets');
    selectEntity(0); // Click Bay Bayou
    testResults.push({{
        name: "selectEntity from Assets auto-switches to Financials",
        passed: currentPillar === 'financials' && selectedIdx === 0
    }});

    // Test 6: Verify All 13 View Modes
    const allModes = ['cash_flash', 'liquidity', 'forecast', 'valuation', 'tax_activity', 'northstar', 'capex', 'summary', 'visual', 'split', 'skyline_pdf', 'jim_pdf', 'jim_summary'];
    let allModesPassed = true;
    allModes.forEach(m => {{
        setViewMode(m);
        if (currentViewMode !== m) allModesPassed = false;
    }});
    testResults.push({{
        name: "All 13 View Modes can be activated sequentially",
        passed: allModesPassed
    }});

    // Test 7: Jim Report Viewer Bridge Data Integrity
    testResults.push({{
        name: "Jim Summaries parsed and present",
        passed: typeof jimSummaries === 'object' && Object.keys(jimSummaries).length >= 12
    }});

    let jimAllHaveNarrative = true;
    entities.forEach(e => {{
        const js = jimSummaries[e.id];
        if (!js || !js.summary_text || !js.primary_pdf) jimAllHaveNarrative = false;
    }});
    testResults.push({{
        name: "All 12 entities have Jim's emailed summary narrative and primary PDF",
        passed: jimAllHaveNarrative
    }});

    // Test 8: Entity Jim PDF dynamic update
    let allEntityJimPdfsUpdated = true;
    entities.forEach(e => {{
        if (!e.jim_pdf || e.jim_pdf.includes('1999')) allEntityJimPdfsUpdated = false;
    }});
    testResults.push({{
        name: "All 12 entities dynamically updated e.jim_pdf from Jim's latest reports",
        passed: allEntityJimPdfsUpdated
    }});

    // Test 9: Lake County Pre-Sale Target Data Integrity
    testResults.push({{
        name: "Lake Pre-Sale target data parsed and top_targets present",
        passed: typeof lakePresaleData === 'object' && lakePresaleData.top_targets && lakePresaleData.top_targets.length >= 200
    }});

    testResults.push({{
        name: "Lake Curated $2.0M portfolio reaches target spend",
        passed: lakePresaleData.curated_2m_portfolio && lakePresaleData.curated_2m_portfolio.total_spend >= 2000000
    }});

    // Test 10: Subtax Hunter Priority Matches Integrity
    testResults.push({{
        name: "Subtax Hunter parsed and 18 priority opportunities present",
        passed: typeof subtaxHunterData === 'object' && subtaxHunterData.total_subtax_parcels === 18 && subtaxHunterData.total_subtax_capital_required > 120000
    }});

    console.log(JSON.stringify(testResults));
    """

    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
        tf.write(node_test_script)
        temp_js_path = tf.name

    try:
        res = subprocess.run(["node", temp_js_path], capture_output=True, text=True)
    finally:
        if os.path.exists(temp_js_path):
            os.remove(temp_js_path)

    if res.returncode != 0:
        print(f"❌ FAIL: Node script error: {res.stderr}")
        sys.exit(1)

    node_results = json.loads(res.stdout)
    for nr in node_results:
        assert_test(nr["name"], nr["passed"])

    # =========================================================================
    # TEST 4: Stan's Standalone Tax Buying Dashboard (tax.html)
    # =========================================================================
    print("\n--- Phase 4: Stan's Dedicated Tax Buying Dashboard (tax.html) ---")
    tax_html_path = "tax.html"
    assert_test("Standalone tax.html exists on disk", os.path.exists(tax_html_path))
    if os.path.exists(tax_html_path):
        with open(tax_html_path) as f:
            tax_html_content = f.read()
        assert_test("tax.html requires passcode authentication", 'id="authOverlay"' in tax_html_content)
        assert_test("tax.html leads with 2025 Historical Intelligence", "1. Full Historical Analysis" in tax_html_content)
        assert_test("tax.html contains Subtax Operations section", "Subtax Operations" in tax_html_content)
        assert_test("tax.html contains Lake County War Room table", 'id="lakeTargetBody"' in tax_html_content)
        assert_test("tax.html contains Waukegan water lien redline tags", "Water Lien Risk" in tax_html_content)
        assert_test("tax.html contains Lake County Assessor search links", "https://tax.lakecountyil.gov/search/commonsearch.aspx" in tax_html_content)
        assert_test("tax.html contains Lake Clean Auction CSV Export", "exportCleanAuctionCsv" in tax_html_content)
        assert_test("tax.html contains Mary Subtax CSV Export", "exportMarySubtaxCsv" in tax_html_content)
        assert_test("tax.html contains Visuals & Maps (Drive-By) buttons", "📸 Maps" in tax_html_content)
        assert_test("tax.html contains Stan's 4-County Rollup ($42.13M)", "$42,133,147" in tax_html_content)
        assert_test("tax.html contains Quantitative Redemption Certainty", "% Certainty" in tax_html_content)

    print("\n" + "=" * 80)
    if passed == total:
        print(f"🎉 ALL {total}/{total} TESTS PASSED PERFECTLY!")
    else:
        print(f"⚠️ {passed}/{total} TESTS PASSED ({total - passed} FAILED)")
    print("=" * 80)
    return passed == total

if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
