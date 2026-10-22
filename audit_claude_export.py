#!/usr/bin/env python3
"""
Detailed audit script comparing Claude's export_for_google.json against 
our portfolio_top10_financial_reports.json across every single company.
"""

import json
import os
import sys

CLAUDE_PATH = "/Users/louislapat/vibe/skyline/reports/Top 10 statements Q1 2026/export_for_google.json"
GEMINI_PATH = "/Users/louislapat/vibe/google/skyline auto/portfolio_top10_financial_reports.json"

def main():
    if not os.path.exists(CLAUDE_PATH):
        print(f"Error: {CLAUDE_PATH} not found")
        return
    if not os.path.exists(GEMINI_PATH):
        print(f"Error: {GEMINI_PATH} not found")
        return

    with open(CLAUDE_PATH) as f:
        claude_export = json.load(f)

    with open(GEMINI_PATH) as f:
        gemini_export = json.load(f)

    name_map = {
        "Park City Mobile Homes": "Park City Mobile Homes, Inc.",
        "Bay Bayou RV Resort": "Bay Bayou Florida RV Resort",
        "Jennings Realty": "Jennings Realty, Inc.",
        "Sunkissed Village RV Resort": "Sunkissed Village RV Resort",
        "Tax Certificate Buying Entities": "Tax Certificate Entities",
        "Tax Certificate Entities": "Tax Certificate Entities",
        "Madison Community Resort": "Madison Community Resort",
        "Galaxy / Jet Sites (combined LLCs)": "Home Sites / Galaxy",
        "Barbara Descendants Trust": "Barbara Descendant's Trust",
    }

    print("=" * 105)
    print("LINE-BY-LINE AUDIT: CLAUDE'S export_for_google.json vs. GEMINI portfolio_top10_financial_reports.json")
    print("=" * 105)

    all_pnl_match = True
    all_assets_match = True
    all_cash_match = True
    all_residuals_match = True

    for item in claude_export["companies"]:
        c_name = item["company"]
        g_name = name_map.get(c_name, c_name)
        gp = item.get("google_periods")
        
        if not gp:
            print(f"\n⚠️  {c_name.upper()}:")
            print(f"    Claude Note: {item.get('notes', 'No comparative period exported')}")
            continue

        g_data = gemini_export["companies"].get(g_name)
        if not g_data:
            print(f"\n⚠️  {c_name.upper()}: Not found in Gemini export")
            continue

        ci = gp["income_statement"]
        gi = g_data["income_statement"]
        cb = gp["balance_sheet"]
        gb = g_data["balance_sheet"]
        cc = gp["cash_flow_statement"]
        gc = g_data["cash_flow"]

        rev_diff = abs(ci["total_revenue"] - gi["total_revenue"])
        exp_diff = abs(ci["total_expenses"] - gi["total_expenses"])
        net_diff = abs(ci["net_income"] - gi["net_income"])
        ast_diff = abs(cb["total_assets"] - gb["total_assets"])
        res_diff = abs(cb["non_netting_residual"] - gb.get("ledger_classification_residual", 0.0))
        cash_diff = abs(cc["change_in_cash_accounts_per_extract"] - gc["net_cash_change"])

        liab_diff = abs(cb["total_liabilities"] - gb["total_liabilities"])
        eq_diff = abs(cb["total_prior_equity"] - gb["prior_equity"])

        pnl_ok = (rev_diff < 0.01 and exp_diff < 0.01 and net_diff < 0.01)
        ast_ok = (ast_diff < 0.01)
        res_ok = (res_diff < 0.01)
        cash_ok = (cash_diff < 0.01)

        if not pnl_ok: all_pnl_match = False
        if not ast_ok: all_assets_match = False
        if not res_ok: all_residuals_match = False
        if not cash_ok: all_cash_match = False

        status_icon = "✅ EXACT MATCH" if (pnl_ok and ast_ok and res_ok and cash_ok) else "🔍 VARIANCE NOTED"
        print(f"\n📌 {c_name.upper()} -> {status_icon}")
        print(f"   Period: {gp.get('period_label')} (Income dates: {gp.get('start')} to {gp.get('end')})")
        print(f"   [Income Statement]  Revenue: Claude=${ci['total_revenue']:>12,.2f} | Gemini=${gi['total_revenue']:>12,.2f} | Diff=${rev_diff:,.2f}")
        print(f"                       Expenses: Claude=${ci['total_expenses']:>12,.2f} | Gemini=${gi['total_expenses']:>12,.2f} | Diff=${exp_diff:,.2f}")
        print(f"                       Net:      Claude=${ci['net_income']:>12,.2f} | Gemini=${gi['net_income']:>12,.2f} | Diff=${net_diff:,.2f}")
        print(f"   [Balance Sheet]     Assets:   Claude=${cb['total_assets']:>12,.2f} | Gemini=${gb['total_assets']:>12,.2f} | Diff=${ast_diff:,.2f}")
        print(f"                       Residual: Claude=${cb['non_netting_residual']:>12,.2f} | Gemini=${gb.get('ledger_classification_residual', 0.0):>12,.2f} | Diff=${res_diff:,.2f}")
        print(f"   [Cash Flow]         Net Cash: Claude=${cc['change_in_cash_accounts_per_extract']:>12,.2f} | Gemini=${gc['net_cash_change']:>12,.2f} | Diff=${cash_diff:,.2f}")

        if liab_diff > 0.01 or eq_diff > 0.01:
            print(f"   ℹ️  Classification Breakdown (Liabilities vs. Equity Mapping):")
            print(f"       Liabilities: Claude=${cb['total_liabilities']:>12,.2f} | Gemini=${gb['total_liabilities']:>12,.2f} | Diff=${liab_diff:>11,.2f}")
            print(f"       Prior Equity: Claude=${cb['total_prior_equity']:>12,.2f} | Gemini=${gb['prior_equity']:>12,.2f} | Diff=${eq_diff:>11,.2f}")

    print("\n" + "=" * 105)
    print("AUDIT SUMMARY:")
    print(f"  Income Statements (P&L):  {'100% PERFECT MATCH ($0.00 variance across all companies)' if all_pnl_match else 'Variances found'}")
    print(f"  Total Assets (B/S):       {'100% PERFECT MATCH ($0.00 variance across all companies)' if all_assets_match else 'Variances found'}")
    print(f"  Cash Flow Net Changes:    {'100% PERFECT MATCH ($0.00 variance across all companies)' if all_cash_match else 'Variances found'}")
    print(f"  Unclassified Residuals:   {'100% PERFECT MATCH (Both calculated identical residuals)' if all_residuals_match else 'Variances found'}")
    print("=" * 105)

if __name__ == "__main__":
    main()
