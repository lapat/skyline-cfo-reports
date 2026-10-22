#!/usr/bin/env python3
"""
Master 3-Statement Generator for Every Company in Skyline.

Generates:
1. Income Statement (Profit & Loss / P&L)
2. Balance Sheet (Assets, Liabilities, Equity, Netting Residual)
3. Statement of Cash Flows (Cash from Ops, Beginning Cash, Net Change, Ending Cash)

for every operating entity across the entire Jennings Realty & Affiliates enterprise.

Outputs:
- portfolio_complete_3_statements_all_companies.json
- pdf_reports/00_ALL_COMPANIES_COMPLETE_FINANCIAL_STATEMENTS.pdf
- /Users/louislapat/vibe/skyline/reports/all_companies_3_statements_gemini.json
"""

import json
import os
import sqlite3
import sys
import time
from typing import Dict, Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

from build_financial_pdf_reports import (
    process_financials,
    build_pnl_elements,
    build_bs_elements,
    build_cf_elements,
    get_report_styles,
    fmt_curr,
)

DB_PATH = os.path.abspath("skyline_live_production.sqlite")
OUTPUT_JSON = os.path.abspath("portfolio_complete_3_statements_all_companies.json")
OUTPUT_PDF = os.path.abspath("pdf_reports/00_ALL_COMPANIES_COMPLETE_FINANCIAL_STATEMENTS.pdf")
CLAUDE_REPORTS_DIR = "/Users/louislapat/vibe/skyline/reports"

def generate_all_3_statements():
    conn = sqlite3.connect(DB_PATH)
    styles = get_report_styles()

    # Load all registered portfolio companies from Claude's live export and our master map
    claude_export_path = "/Users/louislapat/vibe/skyline/live_build/export/skyline_reports_all_companies_live.json"
    companies_to_process = []

    if os.path.exists(claude_export_path):
        with open(claude_export_path) as f:
            c_data = json.load(f)
        for c in c_data["companies"]:
            companies_to_process.append({
                "name": c["company"],
                "folders": c["skyline_folders"],
                "role": c.get("role", "portfolio")
            })

    print(f"Loaded {len(companies_to_process)} core portfolio clusters to process.")

    all_statements_data = {
        "description": "Complete 3-Statement Financials (P&L, Balance Sheet, Cash Flow) for every company in Skyline.",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "skyline_live_production.sqlite (Extracted from Live Mapped Share)",
        "companies": {}
    }

    pdf_elements = []

    # Title Cover Page for Master PDF
    pdf_elements.append(Paragraph("JENNINGS REALTY & AFFILIATES", styles["title"]))
    pdf_elements.append(Paragraph("COMPLETE FINANCIAL STATEMENTS BOOK", styles["subtitle"]))
    pdf_elements.append(Paragraph("Three Official Financial Statements for Every Portfolio Entity<br/>Income Statement (P&L) | Balance Sheet | Statement of Cash Flows<br/>Compiled Directly from Live SS&C Skyline General Ledger", styles["meta"]))
    pdf_elements.append(Spacer(1, 20))

    t0 = time.time()
    processed_count = 0

    for idx, comp in enumerate(companies_to_process, 1):
        name = comp["name"]
        folders = comp["folders"]
        p = ",".join("?" for _ in folders)

        # Pull raw transactions and chart
        rows = conn.execute(f"""
            SELECT je.date, je.account, coa.account_title, coa.account_type, je.amount
            FROM journal_entries je
            LEFT JOIN chart_of_accounts coa ON je.ifs_id = coa.ifs_id AND je.account = coa.account_number
            WHERE je.ifs_id IN ({p})
            ORDER BY je.account, je.date
        """, folders).fetchall()

        d_row = conn.execute(f"""
            SELECT MIN(date), MAX(date)
            FROM journal_entries
            WHERE ifs_id IN ({p}) AND date != '000000'
        """, folders).fetchone()

        start_date = d_row[0] or "N/A"
        end_date = d_row[1] or "N/A"

        fin = process_financials({"min_date": start_date, "max_date": end_date, "rows": rows})
        bs = fin["balance_sheet"]
        cf = fin["cash_flow"]

        all_statements_data["companies"][name] = {
            "folders": folders,
            "period": (start_date, end_date),
            "income_statement": {
                "total_revenue": round(fin["revenue"]["total"], 2),
                "total_expenses": round(fin["expenses"]["total"], 2),
                "net_income": round(fin["net_income"], 2),
            },
            "balance_sheet": {
                "total_assets": round(bs["total_assets"], 2),
                "current_assets": round(bs["tot_cur_assets"], 2),
                "fixed_assets": round(bs["tot_fix_assets"], 2),
                "accumulated_depreciation": round(bs["tot_accum_dep"], 2),
                "total_liabilities": round(bs["total_liab"], 2),
                "current_liabilities": round(bs["tot_cur_liab"], 2),
                "long_term_debt": round(bs["tot_lt_debt"], 2),
                "prior_equity": round(bs["prior_equity"], 2),
                "current_period_net_income": round(bs["current_net_income"], 2),
                "ledger_residual": round(bs.get("ledger_residual", 0.0), 2),
                "total_equity": round(bs["total_equity"], 2),
                "total_liabilities_and_equity": round(bs["total_liab_equity"], 2),
                "is_balanced": abs(bs["total_assets"] - bs["total_liab_equity"]) < 0.01
            },
            "cash_flow": {
                "net_income": round(cf["net_income"], 2),
                "depreciation_adjustment": round(cf["deprec_exp"], 2),
                "working_capital_changes": round(cf["wc_change"], 2),
                "cash_from_operations": round(cf["cash_from_ops"], 2),
                "cash_beginning": round(cf["cash_beg"], 2),
                "net_cash_change": round(cf["cash_net"], 2),
                "cash_ending": round(cf["cash_end"], 2),
            }
        }

        # Add to Master PDF
        if idx > 1:
            pdf_elements.append(PageBreak())
        
        pdf_elements.extend(build_pnl_elements(name, f"IFS: {', '.join(folders)}", fin, styles))
        pdf_elements.append(PageBreak())
        pdf_elements.extend(build_bs_elements(name, f"IFS: {', '.join(folders)}", fin, styles))
        pdf_elements.append(PageBreak())
        pdf_elements.extend(build_cf_elements(name, f"IFS: {', '.join(folders)}", fin, styles))

        processed_count += 1
        print(f"  [{idx}/{len(companies_to_process)}] Built 3 statements for: {name[:35]:<35} (Assets: {fmt_curr(bs['total_assets']):>14} | Cash End: {fmt_curr(cf['cash_end']):>14})", flush=True)

    conn.close()

    # Save to local JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(all_statements_data, f, indent=2)
    print(f"\n✅ Saved Master 3-Statement JSON: {OUTPUT_JSON}")

    # Also save to Claude's reports folder
    if os.path.exists(CLAUDE_REPORTS_DIR):
        claude_target = os.path.join(CLAUDE_REPORTS_DIR, "all_companies_3_statements_gemini.json")
        with open(claude_target, "w") as f:
            json.dump(all_statements_data, f, indent=2)
        print(f"✅ Exported to Claude's reports directory: {claude_target}")

    # Build Master PDF
    print(f"Building Master 3-Statement PDF Book at: {OUTPUT_PDF}...")
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    doc.build(pdf_elements)
    print(f"✅ Generated Master PDF Book: {OUTPUT_PDF}")
    print(f"Time Elapsed: {time.time() - t0:.2f} seconds")

if __name__ == "__main__":
    generate_all_3_statements()
