#!/usr/bin/env python3
"""
jays_valuation_engine.py — Jay's Real Estate Community & Expansion Valuation Engine.

Implements Jay's explicit formula:
1. In-Place Communities:
   - T12 Income Statement (Rev - Expenses)
   - Add back management fees
   - Forward 12 Months: +3% Gross Revenue, +1% Expenses
   - Forward NOI = Forward Rev - Forward Exp
   - Cap Rates:
     * Lakeview: 4.5%
     * Park City: 4.0%
     * The Bluffs (MH): 4.0%
     * RV Resorts (Bay Bayou, Sunkissed, Madison, Bluffs RV): 5.5%
   - Gross Asset Value (GAV) = Forward NOI / Cap Rate
   - Owner's Equity (NAV) = GAV - Actual Debt Due Now
   - Loan to Value (LTV) = Actual Debt / GAV

2. Active Expansions Pro Forma:
   - Sunkissed: +150 RV Sites
   - Madison: +220 RV Sites
   - The Bluffs: +150 MH Sites & +11 RV Sites
   - Uses existing revenue and expense per site (Forward) applied to expansion sites
   - Expansion GAV = Expansion NOI / Cap Rate
   - Future Debt = 50% of Expansion GAV (Refinancing Takeout)
   - Cash Extracted = 50% of Expansion GAV (Self-financed capital returned)
   - Total Expansion Value = Retained Equity (50%) + Cash Extracted (50%) = 100% GAV
"""

import os
import json
import sqlite3
import time

OUTPUT_JSON = os.path.abspath("data/jays_real_estate_valuation.json")

def calculate_jays_valuations():
    t0 = time.time()
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    
    # -------------------------------------------------------------
    # 1. Base Data from Skyline GL or Validated TTM Operating Metrics
    # -------------------------------------------------------------
    # Sourced from T12 Income Statements / Audited Financial Packages
    # (Excludes balance sheet loans, intercompany debt, & cash flow noise)
    communities_base = [
        {
            "id": "lakeview",
            "name": "Lakeview Mobile Home Park (Beach Park)",
            "type": "MH",
            "cap_rate": 0.045, # Jay Mandate: 4.5% for Lakeview
            "sites": 150,
            "t12_rev": 1317818.00,
            "t12_exp": 424168.00,
            "mgmt_fee": 212084.00, # Management fee add-back (stays in family)
            "debt_due_now": 7640754.00, # Actual debt due now (Fannie Mae)
            "expansion_mh_sites": 0,
            "expansion_rv_sites": 0
        },
        {
            "id": "park_city",
            "name": "Park City Manufactured Home Community & Plaza",
            "type": "MH",
            "cap_rate": 0.040, # Jay Mandate: 4.0% for Park City
            "sites": 480,
            "t12_rev": 22450000.00,
            "t12_exp": 5850000.00,
            "mgmt_fee": 1185530.00, # Management fee add-back
            "debt_due_now": 39125000.00, # $19.125M term loan + $20M credit line
            "expansion_mh_sites": 0,
            "expansion_rv_sites": 0
        },
        {
            "id": "bay_bayou",
            "name": "Bay Bayou Florida RV Resort",
            "type": "RV",
            "cap_rate": 0.055, # Jay Mandate: 5.5% for RV Resorts
            "sites": 308,
            "t12_rev": 3793570.00,
            "t12_exp": 993570.00,
            "mgmt_fee": 185000.00, # Management fee add-back
            "debt_due_now": 8500000.00, # Actual debt due now
            "expansion_mh_sites": 0,
            "expansion_rv_sites": 42 # Phase II waterfront engineered
        },
        {
            "id": "sunkissed",
            "name": "Sunkissed Village RV Resort",
            "type": "RV",
            "cap_rate": 0.055, # Jay Mandate: 5.5% for RV Resorts
            "sites": 275,
            "t12_rev": 2599444.00,
            "t12_exp": 1250000.00,
            "mgmt_fee": 145000.00, # Management fee add-back
            "debt_due_now": 5000000.00, # Actual debt due now
            "expansion_mh_sites": 0,
            "expansion_rv_sites": 150 # Jay: 150 RV sites expansion
        },
        {
            "id": "the_bluffs",
            "name": "The Bluffs MH & RV Resort",
            "type": "MIXED",
            "cap_rate_mh": 0.040, # Jay Mandate: 4.0% for The Bluffs MH
            "cap_rate_rv": 0.055, # Jay Mandate: 5.5% for RV Resorts
            "sites_mh": 95,
            "sites_rv": 0,
            "t12_rev": 1139154.00,
            "t12_exp": 485000.00,
            "mgmt_fee": 75000.00,
            "debt_due_now": 2975000.00,
            "expansion_mh_sites": 150, # Jay: 150 MH sites expansion
            "expansion_rv_sites": 11   # Jay: 11 RV sites expansion
        },
        {
            "id": "madison",
            "name": "Madison RV & Golf Resort / Jet Sites B",
            "type": "RV",
            "cap_rate": 0.055, # Jay Mandate: 5.5% for RV Resorts
            "sites": 95,
            "t12_rev": 1119688.00,
            "t12_exp": 585000.00,
            "mgmt_fee": 65000.00,
            "debt_due_now": 1039000.00,
            "expansion_mh_sites": 0,
            "expansion_rv_sites": 220 # Jay: 220 RV sites expansion
        }
    ]

    # -------------------------------------------------------------
    # 2. In-Place Community Valuation (Forward 12-Month Pro Forma)
    # -------------------------------------------------------------
    in_place_results = []
    
    total_in_place_gav = 0.0
    total_in_place_debt = 0.0
    total_in_place_equity = 0.0
    total_in_place_fwd_noi = 0.0

    for c in communities_base:
        # Jay Formula: Add back management fees
        adj_exp = c["t12_exp"] - c["mgmt_fee"]
        
        # Jay Formula: Forward 12 Months (+3% Revenue, +1% Expenses)
        fwd_rev = c["t12_rev"] * 1.03
        fwd_exp = adj_exp * 1.01
        fwd_noi = fwd_rev - fwd_exp
        
        # Cap Rate handling (Mixed vs Single)
        if c.get("type") == "MIXED":
            # The Bluffs MH (4.0%)
            cap_rate = c["cap_rate_mh"]
            total_sites = c["sites_mh"]
        else:
            cap_rate = c["cap_rate"]
            total_sites = c["sites"]

        # Gross Asset Value = Forward NOI / Cap Rate
        gav = fwd_noi / cap_rate
        debt = c["debt_due_now"]
        equity = gav - debt
        ltv = (debt / gav) * 100 if gav > 0 else 0.0

        # Economics per site for expansions
        rev_per_site = fwd_rev / total_sites if total_sites > 0 else 0.0
        exp_per_site = fwd_exp / total_sites if total_sites > 0 else 0.0
        noi_per_site = fwd_noi / total_sites if total_sites > 0 else 0.0

        item = {
            "id": c["id"],
            "name": c["name"],
            "type": c["type"],
            "existing_sites": total_sites,
            "t12_revenue": c["t12_rev"],
            "t12_expenses": c["t12_exp"],
            "mgmt_fee_addback": c["mgmt_fee"],
            "adjusted_t12_expenses": adj_exp,
            "forward_revenue_plus3pct": round(fwd_rev, 2),
            "forward_expenses_plus1pct": round(fwd_exp, 2),
            "forward_noi": round(fwd_noi, 2),
            "cap_rate": cap_rate,
            "gross_asset_value": round(gav, 2),
            "actual_debt_due_now": round(debt, 2),
            "owners_equity_nav": round(equity, 2),
            "loan_to_value_pct": round(ltv, 1),
            "rev_per_site": round(rev_per_site, 2),
            "exp_per_site": round(exp_per_site, 2),
            "noi_per_site": round(noi_per_site, 2)
        }
        
        in_place_results.append(item)
        total_in_place_gav += gav
        total_in_place_debt += debt
        total_in_place_equity += equity
        total_in_place_fwd_noi += fwd_noi

    # -------------------------------------------------------------
    # 3. Active Expansions Pro Forma (Stabilized 50% Refinance Model)
    # -------------------------------------------------------------
    # Sunkissed: +150 RV
    # Madison: +220 RV
    # The Bluffs: +150 MH & +11 RV
    expansions_base = [
        {
            "community_id": "sunkissed",
            "name": "Sunkissed Village RV Expansion (+150 Sites)",
            "target_property": "Sunkissed Village RV Resort",
            "new_sites": 150,
            "site_type": "RV Sites",
            "cap_rate": 0.055, # Jay: 5.5% for RV
            "parent_id": "sunkissed"
        },
        {
            "community_id": "madison",
            "name": "Madison RV Resort Phase II Expansion (+220 Sites)",
            "target_property": "Madison RV & Golf Resort",
            "new_sites": 220,
            "site_type": "RV Sites",
            "cap_rate": 0.055, # Jay: 5.5% for RV
            "parent_id": "madison"
        },
        {
            "community_id": "the_bluffs_mh",
            "name": "The Bluffs Mobile Home Expansion (+150 Sites)",
            "target_property": "The Bluffs MH & RV Resort",
            "new_sites": 150,
            "site_type": "MH Sites",
            "cap_rate": 0.040, # Jay: 4.0% for The Bluffs MH
            "parent_id": "the_bluffs"
        },
        {
            "community_id": "the_bluffs_rv",
            "name": "The Bluffs RV Expansion (+11 Sites)",
            "target_property": "The Bluffs MH & RV Resort",
            "new_sites": 11,
            "site_type": "RV Sites",
            "cap_rate": 0.055, # Jay: 5.5% for RV
            "parent_id": "the_bluffs"
        }
    ]

    expansion_results = []
    total_exp_gav = 0.0
    total_exp_future_debt = 0.0
    total_exp_cash_returned = 0.0
    total_exp_retained_equity = 0.0
    total_exp_stabilized_noi = 0.0

    in_place_lookup = {x["id"]: x for x in in_place_results}

    for exp in expansions_base:
        parent = in_place_lookup.get(exp["parent_id"])
        new_sites = exp["new_sites"]
        
        # Jay Formula: Take existing revenue & expenses per lot and apply to new lots
        exp_rev = new_sites * parent["rev_per_site"]
        exp_exp = new_sites * parent["exp_per_site"]
        exp_noi = exp_rev - exp_exp

        # Jay Formula: Capitalize at asset cap rate
        cap_rate = exp["cap_rate"]
        exp_gav = exp_noi / cap_rate
        
        # Jay Formula: 50% future debt on entire asset value
        future_debt = exp_gav * 0.50
        
        # Jay Formula: Since self-financed with our own cash, take all money back out as cash
        cash_returned = future_debt
        retained_equity = exp_gav - future_debt

        # Total Value Delivered to Jennings = Retained Equity (50%) + Cash Returned (50%) = 100% GAV
        total_value_delivered = retained_equity + cash_returned

        item = {
            "name": exp["name"],
            "target_property": exp["target_property"],
            "new_sites": new_sites,
            "site_type": exp["site_type"],
            "cap_rate": cap_rate,
            "expansion_stabilized_revenue": round(exp_rev, 2),
            "expansion_stabilized_expenses": round(exp_exp, 2),
            "expansion_stabilized_noi": round(exp_noi, 2),
            "expansion_gross_asset_value": round(exp_gav, 2),
            "future_refinance_debt_50pct": round(future_debt, 2),
            "refi_cash_extracted_to_jennings": round(cash_returned, 2),
            "retained_owners_equity_50pct": round(retained_equity, 2),
            "total_expansion_value_created": round(total_value_delivered, 2),
            "notes": f"Self-financed development. Stabilized @ {cap_rate*100:.1f}% Cap. 50% cash-out recap extracts ${cash_returned:,.0f} tax-free cash while retaining ${retained_equity:,.0f} equity."
        }
        
        expansion_results.append(item)
        total_exp_gav += exp_gav
        total_exp_future_debt += future_debt
        total_exp_cash_returned += cash_returned
        total_exp_retained_equity += retained_equity
        total_exp_stabilized_noi += exp_noi

    # -------------------------------------------------------------
    # 4. Total Community Portfolio Summary (In-Place + Expansion)
    # -------------------------------------------------------------
    grand_total_community_gav = total_in_place_gav + total_exp_gav
    grand_total_future_debt = total_in_place_debt + total_exp_future_debt
    grand_total_retained_equity = total_in_place_equity + total_exp_retained_equity
    
    # Combined Real Estate Value Delivered = In-Place Equity + Expansion Equity + Refi Cash Extracted
    total_re_wealth_delivered = total_in_place_equity + total_exp_retained_equity + total_exp_cash_returned

    result = {
        "as_of_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "formula_mandate": "Jay's Institutional Real Estate & Expansion Pro Forma Model",
        "in_place_communities": {
            "headline_gross_asset_value": round(total_in_place_gav, 2),
            "headline_actual_debt": round(total_in_place_debt, 2),
            "headline_owners_equity": round(total_in_place_equity, 2),
            "headline_forward_noi": round(total_in_place_fwd_noi, 2),
            "blended_ltv_pct": round((total_in_place_debt / total_in_place_gav) * 100, 1),
            "assets": in_place_results
        },
        "expansion_pipeline": {
            "total_new_sites_planned": sum(x["new_sites"] for x in expansion_results),
            "headline_expansion_gav": round(total_exp_gav, 2),
            "headline_future_debt_50pct": round(total_exp_future_debt, 2),
            "headline_refi_cash_returned": round(total_exp_cash_returned, 2),
            "headline_retained_equity": round(total_exp_retained_equity, 2),
            "headline_expansion_noi": round(total_exp_stabilized_noi, 2),
            "projects": expansion_results
        },
        "consolidated_real_estate_totals": {
            "stabilized_portfolio_gav": round(grand_total_community_gav, 2),
            "stabilized_portfolio_debt": round(grand_total_future_debt, 2),
            "stabilized_retained_equity": round(grand_total_retained_equity, 2),
            "total_wealth_created_with_cash_out": round(total_re_wealth_delivered, 2)
        }
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(result, f, indent=2)

    print("=" * 80)
    print("✅ JAY'S REAL ESTATE & EXPANSION VALUATION ENGINE COMPLETE")
    print(f"  1. In-Place Communities GAV:      ${total_in_place_gav:,.2f}")
    print(f"     Actual Debt Due Now:           ${total_in_place_debt:,.2f} ({result['in_place_communities']['blended_ltv_pct']}% LTV)")
    print(f"     Owner's Equity (In-Place NAV): ${total_in_place_equity:,.2f}")
    print("-" * 80)
    print(f"  2. Expansion Pipeline (+{result['expansion_pipeline']['total_new_sites_planned']} Sites):")
    print(f"     Stabilized Expansion GAV:      ${total_exp_gav:,.2f}")
    print(f"     50% Refinance Debt (Cash Out): ${total_exp_cash_returned:,.2f}")
    print(f"     Retained Expansion Equity:     ${total_exp_retained_equity:,.2f}")
    print("-" * 80)
    print(f"  3. Total Stabilized Real Estate:  ${grand_total_community_gav:,.2f} GAV")
    print(f"     Total Wealth Delivered:        ${total_re_wealth_delivered:,.2f} (Equity + Cash Out)")
    print("=" * 80)

    return result

if __name__ == "__main__":
    calculate_jays_valuations()
