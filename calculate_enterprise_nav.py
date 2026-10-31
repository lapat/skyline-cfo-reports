#!/usr/bin/env python3
"""
calculate_enterprise_nav.py — Master Enterprise Valuation & Net Asset Value (NAV) Engine.

Fully incorporates Jay's exact valuation directives:
1. In-Place MH & RV Communities:
   - T12 Income Statement (Revenue - Expenses)
   - Add back management fees
   - Forward 12 Months: +3% Gross Revenue, +1% Expenses
   - Cap Rates: 4.5% Lakeview, 4.0% Park City & Bluffs (MH), 5.5% RV Resorts (Bay Bayou, Sunkissed, Madison, Bluffs RV)
   - GAV = Forward NOI / Cap Rate
   - Net Asset Value = GAV - Actual Debt Due Now

2. Active Expansion Pipeline (Self-Financed Recapitalization Model):
   - Sunkissed: +150 RV Sites
   - Madison: +220 RV Sites
   - The Bluffs: +150 MH Sites & +11 RV Sites
   - Forward Revenue & Expenses per site applied to new sites
   - 50% LTV Refinance Cash-Out returned to Jennings (since self-financed with cash)
   - Total Expansion Value = Retained Equity (50%) + Cash Out (50%) = 100% GAV

3. Total Enterprise Net Asset Value (NAV):
   - Real Estate Communities (In-Place + Expansion)
   - Tax Certificate Investment Portfolio ($40.6M)
   - Cook County Indemnity Judgments Book ($10.2M)
   - Operating Bank Cash ($16.4M)
   - Cook County Escrow ($750k)
   - Modular Notes ($1.8M)
   Less: Total Enterprise Debt
"""

import os
import sys
import json
import time

OUTPUT_JSON = os.path.abspath("enterprise_nav_summary.json")

def calculate_nav(verbose=True):
    t0 = time.time()

    # 1. Execute Jay's Real Estate & Expansion Engine
    import jays_valuation_engine
    re_data = jays_valuation_engine.calculate_jays_valuations()

    in_place = re_data["in_place_communities"]
    expansion = re_data["expansion_pipeline"]
    re_totals = re_data["consolidated_real_estate_totals"]

    re_in_place_gav = in_place["headline_gross_asset_value"]
    re_in_place_debt = in_place["headline_actual_debt"]
    re_in_place_equity = in_place["headline_owners_equity"]

    # 2. Tax Certificate Investment Portfolio
    tax_summary_file = os.path.abspath("tax_activity_summary.json")
    tax_assets = 40622612.00
    tax_debt = 30224314.00
    tax_equity = 10398298.00

    if os.path.exists(tax_summary_file):
        try:
            with open(tax_summary_file) as f:
                ts = json.load(f)
            cs = ts.get("capital_stack", {})
            tax_assets = float(cs.get("total_tax_assets", tax_assets))
            tax_debt = float(cs.get("bank_debt_outstanding", tax_debt))
            tax_equity = float(cs.get("jennings_total_equity", tax_equity))
        except Exception:
            pass

    # 3. Cook County Indemnity Judgments Book
    indemnity_file = "/Users/louislapat/vibe/jim report viewer/data/indemnity_forecast.json"
    indemnity_value = 10219898.81
    indemnity_cost = 4460515.54
    indemnity_face = 8620415.43
    indemnity_count = 40

    if os.path.exists(indemnity_file):
        try:
            with open(indemnity_file) as f:
                ind = json.load(f)
            indemnity_value = float(ind.get("face_plus_6pct_if_paid_today", indemnity_value))
            bk = ind.get("book", {})
            indemnity_cost = float(bk.get("cost_basis", indemnity_cost))
            indemnity_face = float(bk.get("face_value", indemnity_face))
            indemnity_count = int(bk.get("judgments", indemnity_count))
        except Exception:
            pass

    # 4. Physical Operating Bank Cash (Friday Close)
    cash_flash_file = os.path.abspath("cash_flash_summary.json")
    mary_bank_cash = 9004813.54
    if os.path.exists(cash_flash_file):
        try:
            with open(cash_flash_file) as f:
                cf = json.load(f)
            mary_bank_cash = float(cf.get("total_bank_cash", mary_bank_cash))
        except Exception:
            pass
    # Total physical cash = Mary's operating cash ($9.00M) + Jennings tax cash ($7.38M)
    bank_cash = mary_bank_cash + 7375866.60

    # 5. Cook County Administrative Escrow (Jay's Note)
    cook_county_escrow = 750000.00

    # 6. Park City Modular Notes Book
    notes_file = os.path.abspath("park_city_notes_summary.json")
    pc_notes_book = 1842500.00
    if os.path.exists(notes_file):
        try:
            with open(notes_file) as f:
                nt = json.load(f)
            pc_notes_book = float(nt.get("total_notes_receivable", pc_notes_book))
        except Exception:
            pass

    # Other ancillary real estate (Ellis Apartments + Galaxy Land Book)
    ancillary_re_gav = 6000000.00   # Ellis $3.5M + Galaxy $2.5M
    ancillary_re_debt = 2100000.00  # Ellis Byline loan

    # =========================================================================
    # IN-PLACE TOTAL ENTERPRISE RECONCILIATION
    # =========================================================================
    total_in_place_gav = (
        re_in_place_gav
        + ancillary_re_gav
        + tax_assets
        + indemnity_value
        + bank_cash
        + cook_county_escrow
        + pc_notes_book
    )

    total_in_place_debt = re_in_place_debt + ancillary_re_debt + tax_debt
    total_in_place_nav = total_in_place_gav - total_in_place_debt
    in_place_ltv = round((total_in_place_debt / total_in_place_gav) * 100, 1)

    # =========================================================================
    # STABILIZED PRO FORMA EXPANSION SUMMATION
    # =========================================================================
    expansion_gav = expansion["headline_expansion_gav"]
    expansion_refi_cash = expansion["headline_refi_cash_returned"]
    expansion_retained_equity = expansion["headline_retained_equity"]
    total_expansion_value = expansion_refi_cash + expansion_retained_equity

    total_stabilized_gav = total_in_place_gav + expansion_gav
    total_stabilized_debt = total_in_place_debt + expansion["headline_future_debt_50pct"]
    total_stabilized_nav = total_in_place_nav + total_expansion_value
    stabilized_ltv = round((total_stabilized_debt / total_stabilized_gav) * 100, 1)

    pillars = [
        {
            "pillar_num": 1,
            "title": "Operating MH & RV Communities (Jay's Forward 12M Cap Rate Model)",
            "value": round(re_in_place_gav, 2),
            "share_of_gav": round((re_in_place_gav / total_in_place_gav) * 100, 1),
            "methodology": "Jay's Mandate: T12 Revenue (+3% growth), T12 Expenses after mgmt fee addback (+1% inflation). Cap rates: Lakeview 4.5%, Park City 4.0%, The Bluffs MH 4.0%, RV Resorts 5.5%.",
            "sub_items": [
                {
                    "name": f"{x['name']} ({x['existing_sites']} sites @ {x['cap_rate']*100:.1f}% Cap)",
                    "amount": x["gross_asset_value"],
                    "noi": x["forward_noi"],
                    "debt": x["actual_debt_due_now"],
                    "equity": x["owners_equity_nav"],
                    "ltv": x["loan_to_value_pct"]
                }
                for x in in_place["assets"]
            ]
        },
        {
            "pillar_num": 2,
            "title": "Tax Certificate Investment Portfolio",
            "value": round(tax_assets, 2),
            "share_of_gav": round((tax_assets / total_in_place_gav) * 100, 1),
            "methodology": "Total active tax certificates across 6 tax entities (Interstate, Central Buyer, Diamond Quest, Union Tax, National Indemnity, Mutual Fidelity) carrying 12% statutory carry.",
            "sub_items": [
                {"name": "Total Tax Certificate Book Value", "amount": round(tax_assets, 2)},
                {"name": "Bank Debt Borrowed on Collateral (95% advance)", "amount": round(-tax_debt, 2)},
                {"name": "Net Jennings Tax Equity", "amount": round(tax_equity, 2)}
            ]
        },
        {
            "pillar_num": 3,
            "title": "Physical Operating Bank Cash (Friday Close)",
            "value": round(bank_cash, 2),
            "share_of_gav": round((bank_cash / total_in_place_gav) * 100, 1),
            "methodology": f"Cleared operating bank cash ($9.00M Mary's sheet + $7.38M Jennings unencumbered tax equity). J R Management at $3.67M, Byline at $1.19M.",
            "sub_items": [
                {"name": "Mary's Operating Cash Ledger (32 accounts)", "amount": round(mary_bank_cash, 2)},
                {"name": "Jennings Tax Equity Cash in Clearing", "amount": 7375866.60}
            ]
        },
        {
            "pillar_num": 4,
            "title": "Cook County Indemnity Judgments Book",
            "value": round(indemnity_value, 2),
            "share_of_gav": round((indemnity_value / total_in_place_gav) * 100, 1),
            "methodology": f"40 active court judgment claims purchased at a discount ({indemnity_count} judgments, ${indemnity_cost:,.0f} cost, ${indemnity_face:,.0f} face). Earning 6.0% simple statutory interest.",
            "sub_items": [
                {"name": f"Active Judgment Face Value ({indemnity_count} claims)", "amount": round(indemnity_face, 2)},
                {"name": "Accrued 6.0% Statutory Interest", "amount": round(indemnity_value - indemnity_face, 2)},
                {"name": "Total Value if Disbursed Today", "amount": round(indemnity_value, 2)}
            ]
        },
        {
            "pillar_num": 5,
            "title": "Park City Modular Home Installment Notes",
            "value": round(pc_notes_book, 2),
            "share_of_gav": round((pc_notes_book / total_in_place_gav) * 100, 1),
            "methodology": "64 performing seller-financed modular home installment loans at Park City. Generates $28.5k/mo cashflow with 1.8% delinquency.",
            "sub_items": [
                {"name": "Total Active Performing Notes Receivable", "amount": round(pc_notes_book, 2)}
            ]
        },
        {
            "pillar_num": 6,
            "title": "Cook County Frozen Administrative Escrow",
            "value": round(cook_county_escrow, 2),
            "share_of_gav": round((cook_county_escrow / total_in_place_gav) * 100, 1),
            "methodology": "Jay's Directive: Completed taxpayer redemptions sitting in Cook County escrow awaiting administrative disbursement checks.",
            "sub_items": [
                {"name": "Cook County Redemption Checks Pending", "amount": round(cook_county_escrow, 2)}
            ]
        },
        {
            "pillar_num": 7,
            "title": "Ancillary Real Estate Holdings (Ellis Apts & Galaxy Land)",
            "value": round(ancillary_re_gav, 2),
            "share_of_gav": round((ancillary_re_gav / total_in_place_gav) * 100, 1),
            "methodology": "Ellis Street Apartments (Byline Bank collateral, $3.5M FMV, $2.1M debt) + Galaxy Sites unencumbered residential land book ($2.5M).",
            "sub_items": [
                {"name": "Ellis Street Apartments (Home Sites Series C)", "amount": 3500000.00},
                {"name": "Galaxy Sites Residential Land Parcels", "amount": 2500000.00}
            ]
        }
    ]

    result = {
        "as_of_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "date_display": time.strftime("%B %d, %Y"),
        "valuation_framework": "Jay Lapat's Institutional Real Estate & Expansion Pro Forma Model",
        "in_place_summary": {
            "net_asset_value": round(total_in_place_nav, 2),
            "gross_asset_value": round(total_in_place_gav, 2),
            "total_enterprise_debt": round(total_in_place_debt, 2),
            "loan_to_value_ratio_pct": in_place_ltv
        },
        "stabilized_expansion_summary": {
            "stabilized_gross_asset_value": round(total_stabilized_gav, 2),
            "stabilized_total_debt": round(total_stabilized_debt, 2),
            "stabilized_net_enterprise_value": round(total_stabilized_nav, 2),
            "total_expansion_value_created": round(total_expansion_value, 2),
            "expansion_refi_cash_extracted": round(expansion_refi_cash, 2),
            "expansion_retained_equity": round(expansion_retained_equity, 2),
            "stabilized_ltv_pct": stabilized_ltv
        },
        "jays_communities_schedule": in_place["assets"],
        "jays_expansions_schedule": expansion["projects"],
        "pillars": pillars
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(result, f, indent=2)

    if verbose:
        print("=" * 80)
        print("JENNINGS REALTY — JAY'S ENTERPRISE VALUATION & RECAP ENGINE")
        print(f"  1. In-Place Gross Asset Value (GAV):    ${total_in_place_gav:,.2f}")
        print(f"     Total In-Place Debt:                 ${total_in_place_debt:,.2f} ({in_place_ltv}% LTV)")
        print(f"     IN-PLACE NET ASSET VALUE (NAV):      ${total_in_place_nav:,.2f}")
        print("-" * 80)
        print(f"  2. Expansion Pipeline (+{expansion['total_new_sites_planned']} Sites):")
        print(f"     Stabilized Expansion GAV:            ${expansion_gav:,.2f}")
        print(f"     50% Refinance Cash Returned to Firm: ${expansion_refi_cash:,.2f}")
        print(f"     Retained Expansion Equity (50%):     ${expansion_retained_equity:,.2f}")
        print("-" * 80)
        print(f"  3. TOTAL STABILIZED ENTERPRISE VALUE:   ${total_stabilized_nav:,.2f} NAV")
        print(f"     Total Stabilized GAV:                ${total_stabilized_gav:,.2f} ({stabilized_ltv}% LTV)")
        print(f"     Saved structured model ->            {OUTPUT_JSON}")
        print("=" * 80)

    return result

if __name__ == "__main__":
    calculate_nav(verbose=True)
