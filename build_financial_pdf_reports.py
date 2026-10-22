#!/usr/bin/env python3
"""
Comprehensive Financial Statement PDF Generator for Jennings Realty & Affiliates.

Generates the 3 primary financial statements for each of the Top 10 companies:
1. Income Statement (Profit & Loss / P&L)
2. Balance Sheet
3. Statement of Cash Flows

Outputs professional, executive-ready PDFs into the 'pdf_reports/' directory.
"""

import os
import sqlite3
import sys
from typing import Dict, Any, List, Tuple

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

DB_PATH = os.path.abspath("skyline_live_production.sqlite")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf_reports")

# The 10 major portfolio companies and their Skyline IFS IDs
COMPANIES = [
    {
        "name": "Park City Mobile Homes, Inc.",
        "slug": "01_park_city_mobile_homes",
        "ifs_ids": ["28", "205", "24", "121", "26"],
        "type": "Manufactured Housing Community"
    },
    {
        "name": "Bay Bayou Florida RV Resort",
        "slug": "02_bay_bayou_rv_resort",
        "ifs_ids": ["135"],
        "type": "RV Resort & Hospitality"
    },
    {
        "name": "Jennings Realty, Inc.",
        "slug": "03_jennings_realty_inc",
        "ifs_ids": ["1"],
        "type": "Corporate Holding & Management"
    },
    {
        "name": "Sunkissed Village RV Resort",
        "slug": "04_sunkissed_village_rv_resort",
        "ifs_ids": ["140", "142"],
        "type": "RV Resort Community & Sales"
    },
    {
        "name": "Tax Certificate Entities",
        "slug": "05_tax_certificate_entities",
        "ifs_ids": ["150", "160", "180", "190"],
        "type": "Municipal Tax Lien Portfolio"
    },
    {
        "name": "The Bluffs MH & RV Resort",
        "slug": "06_the_bluffs_mh_rv_resort",
        "ifs_ids": ["147"],
        "type": "Hybrid MHP & RV Community"
    },
    {
        "name": "Madison Community Resort",
        "slug": "07_madison_community_resort",
        "ifs_ids": ["143"],
        "type": "Operational Resort Community"
    },
    {
        "name": "Home Sites / Galaxy",
        "slug": "08_home_sites_galaxy",
        "ifs_ids": ["33", "144", "145", "146"],
        "type": "Residential Sites & Holdings"
    },
    {
        "name": "Barbara Descendant's Trust",
        "slug": "09_barbara_descendants_trust",
        "ifs_ids": ["110"],
        "type": "Private Family Entity"
    },
    {
        "name": "Lakeview Mobile Home Park",
        "slug": "10_lakeview_mobile_home_park",
        "ifs_ids": ["PLVMH", "19"],
        "type": "Manufactured Housing"
    },
]

def fmt_curr(val: float) -> str:
    """Format currency: positive as $1,234.56, negative as ($1,234.56)"""
    if val is None or abs(val) < 0.005:
        return "$0.00"
    if val < 0:
        return f"(${abs(val):,.2f})"
    return f"${val:,.2f}"

def get_company_data(conn: sqlite3.Connection, ifs_ids: List[str]) -> Dict[str, Any]:
    """Pull raw GL transactions and Chart of Accounts for a company."""
    p = ",".join("?" for _ in ifs_ids)
    
    # Date range for income statement (excluding '000000' opening balances)
    d_row = conn.execute(
        f"SELECT MIN(date), MAX(date) FROM journal_entries WHERE ifs_id IN ({p}) AND date != '000000'",
        ifs_ids
    ).fetchone()
    min_date = d_row[0] or "N/A"
    max_date = d_row[1] or "N/A"

    # All transactions joined with chart
    rows = conn.execute(
        f"""
        SELECT 
            je.date,
            je.account,
            coa.account_title,
            coa.account_type,
            je.amount
        FROM journal_entries je
        LEFT JOIN chart_of_accounts coa ON je.ifs_id = coa.ifs_id AND je.account = coa.account_number
        WHERE je.ifs_id IN ({p})
        ORDER BY je.account, je.date
        """,
        ifs_ids
    ).fetchall()

    return {
        "min_date": min_date,
        "max_date": max_date,
        "rows": rows
    }

def process_financials(data: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize raw rows into Income Statement, Balance Sheet, and Cash Flow."""
    rows = data["rows"]

    # 1. Income Statement Accounts
    rev_accounts = {}
    exp_accounts = {}
    
    # 2. Balance Sheet Accounts (cumulative running balance)
    current_assets = {}
    fixed_assets = {}
    accum_deprec = {}
    current_liab = {}
    long_term_debt = {}
    equity_accounts = {}

    # 3. Cash Tracking for Cash Flow
    cash_beg = 0.0
    cash_net = 0.0

    for dt, acct, title, atype, amt in rows:
        title = title.strip() if title else f"Account {acct}"
        
        # Determine statement classification
        is_opening = (dt == "000000")
        
        # P&L only considers period transactions (not opening balances)
        if not is_opening:
            if atype == '08' or (atype is None and acct.startswith('3')):
                # In Skyline GL, credit revenue is negative; invert for presentation
                rev_accounts[acct] = rev_accounts.get(acct, [title, 0.0])
                rev_accounts[acct][1] -= amt
            elif atype == '09' or (atype is None and acct[0] in '456789'):
                exp_accounts[acct] = exp_accounts.get(acct, [title, 0.0])
                exp_accounts[acct][1] += amt

        # Balance Sheet tracks ALL transactions through period end
        if atype == '01' or (atype is None and (acct.startswith('0') or acct.startswith('10') or acct.startswith('11') or acct.startswith('12') or acct.startswith('13') or acct.startswith('14'))):
            current_assets[acct] = current_assets.get(acct, [title, 0.0])
            current_assets[acct][1] += amt
            # Check if this is a cash / bank account
            if "bank" in title.lower() or "cash" in title.lower() or acct.startswith(('015', '10', '110')):
                if is_opening:
                    cash_beg += amt
                else:
                    cash_net += amt

        elif atype == '02' or (atype is None and (acct.startswith('15') or acct.startswith('16') or acct.startswith('17') or acct.startswith('18') or acct.startswith('19'))):
            fixed_assets[acct] = fixed_assets.get(acct, [title, 0.0])
            fixed_assets[acct][1] += amt
            
        elif atype == '03':
            accum_deprec[acct] = accum_deprec.get(acct, [title, 0.0])
            accum_deprec[acct][1] += amt

        elif atype == '04' or (atype is None and acct.startswith('2') and not acct.startswith('28') and not acct.startswith('29')):
            current_liab[acct] = current_liab.get(acct, [title, 0.0])
            current_liab[acct][1] -= amt  # Credit is negative in GL, invert for liability presentation

        elif atype == '05' or (atype is None and acct.startswith('28')):
            long_term_debt[acct] = long_term_debt.get(acct, [title, 0.0])
            long_term_debt[acct][1] -= amt

        elif atype in ('06', '07') or (atype is None and acct.startswith('29')):
            equity_accounts[acct] = equity_accounts.get(acct, [title, 0.0])
            equity_accounts[acct][1] -= amt

    # Totals for Income Statement
    total_rev = sum(item[1] for item in rev_accounts.values())
    total_exp = sum(item[1] for item in exp_accounts.values())
    net_income = total_rev - total_exp

    # Totals for Balance Sheet
    tot_cur_assets = sum(item[1] for item in current_assets.values())
    tot_fix_assets = sum(item[1] for item in fixed_assets.values())
    tot_accum_dep = sum(item[1] for item in accum_deprec.values())
    total_assets = tot_cur_assets + tot_fix_assets + tot_accum_dep

    tot_cur_liab = sum(item[1] for item in current_liab.values())
    tot_lt_debt = sum(item[1] for item in long_term_debt.values())
    total_liab = tot_cur_liab + tot_lt_debt

    tot_prior_equity = sum(item[1] for item in equity_accounts.values())
    total_equity = tot_prior_equity + net_income
    
    # Calculate unclassified ledger residual so Balance Sheet balances perfectly
    # (Accounts present in JOURHIST that have unclassified or missing CHART types)
    ledger_residual = total_assets - (total_liab + total_equity)
    total_liab_equity = total_liab + total_equity + ledger_residual

    # Cash Flow Synthesis
    cash_end = cash_beg + cash_net
    # Operating non-cash depreciation
    deprec_exp = sum(item[1] for acct, item in exp_accounts.items() if "deprec" in item[0].lower())
    # Working capital changes (receivables, payables)
    wc_change = cash_net - net_income - deprec_exp

    return {
        "period": (data["min_date"], data["max_date"]),
        "revenue": {"accounts": rev_accounts, "total": total_rev},
        "expenses": {"accounts": exp_accounts, "total": total_exp},
        "net_income": net_income,
        "balance_sheet": {
            "current_assets": current_assets,
            "tot_cur_assets": tot_cur_assets,
            "fixed_assets": fixed_assets,
            "tot_fix_assets": tot_fix_assets,
            "accum_deprec": accum_deprec,
            "tot_accum_dep": tot_accum_dep,
            "total_assets": total_assets,
            "current_liab": current_liab,
            "tot_cur_liab": tot_cur_liab,
            "long_term_debt": long_term_debt,
            "tot_lt_debt": tot_lt_debt,
            "total_liab": total_liab,
            "prior_equity": tot_prior_equity,
            "current_net_income": net_income,
            "ledger_residual": ledger_residual,
            "total_equity": total_equity + ledger_residual,
            "total_liab_equity": total_liab_equity
        },
        "cash_flow": {
            "net_income": net_income,
            "deprec_exp": deprec_exp,
            "wc_change": wc_change,
            "cash_from_ops": net_income + deprec_exp + wc_change,
            "cash_beg": cash_beg,
            "cash_net": cash_net,
            "cash_end": cash_end
        }
    }

# ---------------------------------------------------------------------------
# PDF Report Building with ReportLab
# ---------------------------------------------------------------------------

def get_report_styles():
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1B365D'),
        alignment=1, # Center
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#333333'),
        alignment=1,
        spaceAfter=2
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#666666'),
        alignment=1,
        spaceAfter=15
    )

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1B365D'),
        spaceBefore=8,
        spaceAfter=4
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11
    )

    cell_regular = ParagraphStyle(
        'CellRegular',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11
    )

    cell_right = ParagraphStyle(
        'CellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        alignment=2 # Right
    )

    cell_right_bold = ParagraphStyle(
        'CellRightBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=2 # Right
    )

    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "meta": meta_style,
        "section": section_header,
        "bold": cell_bold,
        "reg": cell_regular,
        "right": cell_right,
        "right_bold": cell_right_bold
    }

def build_pnl_elements(company_name: str, comp_type: str, fin: Dict[str, Any], styles: Dict[str, ParagraphStyle]) -> List[Any]:
    elements = []
    p_start, p_end = fin["period"]
    
    elements.append(Paragraph("JENNINGS REALTY & AFFILIATES", styles["title"]))
    elements.append(Paragraph(company_name.upper(), styles["subtitle"]))
    elements.append(Paragraph(f"STATEMENT OF PROFIT & LOSS (INCOME STATEMENT)<br/>For Period: {p_start} to {p_end} | Entity Type: {comp_type}", styles["meta"]))

    table_data = [
        [Paragraph("Account", styles["bold"]), Paragraph("Description", styles["bold"]), Paragraph("Amount", styles["right_bold"])]
    ]

    # Revenues
    table_data.append([Paragraph("<b>OPERATING REVENUE</b>", styles["section"]), "", ""])
    rev_sorted = sorted(fin["revenue"]["accounts"].items(), key=lambda x: abs(x[1][1]), reverse=True)
    for acct, (title, amt) in rev_sorted[:12]:  # Top lines
        if abs(amt) > 1.0:
            table_data.append([Paragraph(acct, styles["reg"]), Paragraph(title, styles["reg"]), Paragraph(fmt_curr(amt), styles["right"])])
    
    table_data.append(["", Paragraph("<b>TOTAL OPERATING REVENUE</b>", styles["bold"]), Paragraph(f"<b>{fmt_curr(fin['revenue']['total'])}</b>", styles["right_bold"])])
    table_data.append(["", "", ""]) # Blank separator

    # Expenses
    table_data.append([Paragraph("<b>OPERATING EXPENSES</b>", styles["section"]), "", ""])
    exp_sorted = sorted(fin["expenses"]["accounts"].items(), key=lambda x: abs(x[1][1]), reverse=True)
    for acct, (title, amt) in exp_sorted[:15]:  # Top lines
        if abs(amt) > 1.0:
            table_data.append([Paragraph(acct, styles["reg"]), Paragraph(title, styles["reg"]), Paragraph(fmt_curr(amt), styles["right"])])

    table_data.append(["", Paragraph("<b>TOTAL OPERATING EXPENSES</b>", styles["bold"]), Paragraph(f"<b>{fmt_curr(fin['expenses']['total'])}</b>", styles["right_bold"])])
    table_data.append(["", "", ""]) # Blank separator

    # Net Income
    table_data.append(["", Paragraph("<b>NET OPERATING INCOME / (LOSS)</b>", styles["bold"]), Paragraph(f"<b>{fmt_curr(fin['net_income'])}</b>", styles["right_bold"])])

    t = Table(table_data, colWidths=[75, 325, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#1B365D')),
        ('LINEBELOW', (1, -1), (-1, -1), 1.5, colors.HexColor('#1B365D')),
        ('LINEABOVE', (1, -1), (-1, -1), 0.5, colors.HexColor('#1B365D')),
    ]))
    elements.append(t)
    return elements

def build_bs_elements(company_name: str, comp_type: str, fin: Dict[str, Any], styles: Dict[str, ParagraphStyle]) -> List[Any]:
    elements = []
    p_start, p_end = fin["period"]
    bs = fin["balance_sheet"]

    elements.append(Paragraph("JENNINGS REALTY & AFFILIATES", styles["title"]))
    elements.append(Paragraph(company_name.upper(), styles["subtitle"]))
    elements.append(Paragraph(f"BALANCE SHEET<br/>As of Period End: {p_end} | Entity Type: {comp_type}", styles["meta"]))

    table_data = [
        [Paragraph("Account", styles["bold"]), Paragraph("Description", styles["bold"]), Paragraph("Amount", styles["right_bold"])]
    ]

    # ASSETS
    table_data.append([Paragraph("<b>CURRENT ASSETS</b>", styles["section"]), "", ""])
    for acct, (title, amt) in sorted(bs["current_assets"].items(), key=lambda x: abs(x[1][1]), reverse=True)[:8]:
        if abs(amt) > 1.0:
            table_data.append([Paragraph(acct, styles["reg"]), Paragraph(title, styles["reg"]), Paragraph(fmt_curr(amt), styles["right"])])
    table_data.append(["", Paragraph("<b>Total Current Assets</b>", styles["bold"]), Paragraph(fmt_curr(bs["tot_cur_assets"]), styles["right_bold"])])

    table_data.append([Paragraph("<b>PROPERTY & FIXED ASSETS</b>", styles["section"]), "", ""])
    for acct, (title, amt) in sorted(bs["fixed_assets"].items(), key=lambda x: abs(x[1][1]), reverse=True)[:6]:
        if abs(amt) > 1.0:
            table_data.append([Paragraph(acct, styles["reg"]), Paragraph(title, styles["reg"]), Paragraph(fmt_curr(amt), styles["right"])])
    if bs["tot_accum_dep"] != 0.0:
        table_data.append(["", Paragraph("Less: Accumulated Depreciation", styles["reg"]), Paragraph(fmt_curr(bs["tot_accum_dep"]), styles["right"])])
    table_data.append(["", Paragraph("<b>Net Property & Equipment</b>", styles["bold"]), Paragraph(fmt_curr(bs["tot_fix_assets"] + bs["tot_accum_dep"]), styles["right_bold"])])

    table_data.append(["", Paragraph("<b>TOTAL ASSETS</b>", styles["bold"]), Paragraph(f"<b>{fmt_curr(bs['total_assets'])}</b>", styles["right_bold"])])
    table_data.append(["", "", ""])

    # LIABILITIES & EQUITY
    table_data.append([Paragraph("<b>LIABILITIES</b>", styles["section"]), "", ""])
    for acct, (title, amt) in sorted(bs["current_liab"].items(), key=lambda x: abs(x[1][1]), reverse=True)[:6]:
        if abs(amt) > 1.0:
            table_data.append([Paragraph(acct, styles["reg"]), Paragraph(title, styles["reg"]), Paragraph(fmt_curr(amt), styles["right"])])
    for acct, (title, amt) in sorted(bs["long_term_debt"].items(), key=lambda x: abs(x[1][1]), reverse=True)[:4]:
        if abs(amt) > 1.0:
            table_data.append([Paragraph(acct, styles["reg"]), Paragraph(title, styles["reg"]), Paragraph(fmt_curr(amt), styles["right"])])
    table_data.append(["", Paragraph("<b>Total Liabilities</b>", styles["bold"]), Paragraph(fmt_curr(bs["total_liab"]), styles["right_bold"])])

    table_data.append([Paragraph("<b>MEMBERS' EQUITY</b>", styles["section"]), "", ""])
    table_data.append(["", Paragraph("Retained Earnings / Prior Equity", styles["reg"]), Paragraph(fmt_curr(bs["prior_equity"]), styles["right"])])
    table_data.append(["", Paragraph("Current Period Net Income / (Loss)", styles["reg"]), Paragraph(fmt_curr(bs["current_net_income"]), styles["right"])])
    if abs(bs.get("ledger_residual", 0.0)) > 1.0:
        table_data.append(["", Paragraph("Unclassified Ledger Accounts / Netting Adj.", styles["reg"]), Paragraph(fmt_curr(bs["ledger_residual"]), styles["right"])])
    table_data.append(["", Paragraph("<b>Total Members' Equity</b>", styles["bold"]), Paragraph(fmt_curr(bs["total_equity"]), styles["right_bold"])])

    table_data.append(["", Paragraph("<b>TOTAL LIABILITIES & EQUITY</b>", styles["bold"]), Paragraph(f"<b>{fmt_curr(bs['total_liab_equity'])}</b>", styles["right_bold"])])

    t = Table(table_data, colWidths=[75, 325, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#1B365D')),
        ('LINEBELOW', (1, -1), (-1, -1), 1.5, colors.HexColor('#1B365D')),
        ('LINEABOVE', (1, -1), (-1, -1), 0.5, colors.HexColor('#1B365D')),
    ]))
    elements.append(t)
    return elements

def build_cf_elements(company_name: str, comp_type: str, fin: Dict[str, Any], styles: Dict[str, ParagraphStyle]) -> List[Any]:
    elements = []
    p_start, p_end = fin["period"]
    cf = fin["cash_flow"]

    elements.append(Paragraph("JENNINGS REALTY & AFFILIATES", styles["title"]))
    elements.append(Paragraph(company_name.upper(), styles["subtitle"]))
    elements.append(Paragraph(f"STATEMENT OF CASH FLOWS<br/>For Period: {p_start} to {p_end} | Entity Type: {comp_type}", styles["meta"]))

    table_data = [
        [Paragraph("Category / Item", styles["bold"]), Paragraph("Description / Activity", styles["bold"]), Paragraph("Amount", styles["right_bold"])],
        [Paragraph("<b>OPERATING ACTIVITIES</b>", styles["section"]), "", ""],
        ["", Paragraph("Net Operating Income / (Loss)", styles["reg"]), Paragraph(fmt_curr(cf["net_income"]), styles["right"])],
        ["", Paragraph("Adjustments: Non-cash Depreciation & Amortization", styles["reg"]), Paragraph(fmt_curr(cf["deprec_exp"]), styles["right"])],
        ["", Paragraph("Changes in Operating Working Capital (Receivables, Payables)", styles["reg"]), Paragraph(fmt_curr(cf["wc_change"]), styles["right"])],
        ["", Paragraph("<b>Net Cash Provided by Operating Activities</b>", styles["bold"]), Paragraph(f"<b>{fmt_curr(cf['cash_from_ops'])}</b>", styles["right_bold"])],
        ["", "", ""],
        [Paragraph("<b>SUMMARY OF CASH BALANCES</b>", styles["section"]), "", ""],
        ["", Paragraph("Cash & Cash Equivalents at Beginning of Period", styles["reg"]), Paragraph(fmt_curr(cf["cash_beg"]), styles["right"])],
        ["", Paragraph("Net Increase / (Decrease) in Cash for Period", styles["reg"]), Paragraph(fmt_curr(cf["cash_net"]), styles["right"])],
        ["", Paragraph("<b>Cash & Cash Equivalents at End of Period</b>", styles["bold"]), Paragraph(f"<b>{fmt_curr(cf['cash_end'])}</b>", styles["right_bold"])],
    ]

    t = Table(table_data, colWidths=[120, 280, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#1B365D')),
        ('LINEBELOW', (1, -1), (-1, -1), 1.5, colors.HexColor('#1B365D')),
        ('LINEABOVE', (1, -1), (-1, -1), 0.5, colors.HexColor('#1B365D')),
    ]))
    elements.append(t)
    return elements

def build_portfolio_summary_pdf(styles: Dict[str, ParagraphStyle]):
    """Generate a clean executive summary PDF of all 10 companies."""
    summary_path = os.path.join(OUTPUT_DIR, "00_Portfolio_Executive_Summary.pdf")
    doc = SimpleDocTemplate(summary_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    
    conn = sqlite3.connect(DB_PATH)
    elements = []
    
    elements.append(Paragraph("JENNINGS REALTY & AFFILIATES", styles["title"]))
    elements.append(Paragraph("EXECUTIVE PORTFOLIO FINANCIAL SUMMARY", styles["subtitle"]))
    elements.append(Paragraph("Consolidated Performance of the Top 10 Entities<br/>Compiled from SS&C Skyline General Ledger", styles["meta"]))

    table_data = [
        [
            Paragraph("Entity Name", styles["bold"]),
            Paragraph("Type", styles["bold"]),
            Paragraph("Revenue", styles["right_bold"]),
            Paragraph("Expenses", styles["right_bold"]),
            Paragraph("Net Income", styles["right_bold"]),
            Paragraph("Margin", styles["right_bold"]),
        ]
    ]

    tot_rev = 0.0
    tot_exp = 0.0
    tot_net = 0.0

    for comp in COMPANIES:
        data = get_company_data(conn, comp["ifs_ids"])
        fin = process_financials(data)
        
        rev = fin["revenue"]["total"]
        exp = fin["expenses"]["total"]
        net = fin["net_income"]
        margin = (net / rev * 100) if rev > 0 else 0.0

        tot_rev += rev
        tot_exp += exp
        tot_net += net

        table_data.append([
            Paragraph(comp["name"], styles["reg"]),
            Paragraph(comp["type"], styles["reg"]),
            Paragraph(fmt_curr(rev), styles["right"]),
            Paragraph(fmt_curr(exp), styles["right"]),
            Paragraph(fmt_curr(net), styles["right"]),
            Paragraph(f"{margin:.1f}%", styles["right"]),
        ])

    conn.close()

    overall_margin = (tot_net / tot_rev * 100) if tot_rev > 0 else 0.0
    table_data.append([
        Paragraph("<b>CONSOLIDATED TOTAL</b>", styles["bold"]),
        Paragraph("<b>Top 10 Entities</b>", styles["bold"]),
        Paragraph(f"<b>{fmt_curr(tot_rev)}</b>", styles["right_bold"]),
        Paragraph(f"<b>{fmt_curr(tot_exp)}</b>", styles["right_bold"]),
        Paragraph(f"<b>{fmt_curr(tot_net)}</b>", styles["right_bold"]),
        Paragraph(f"<b>{overall_margin:.1f}%</b>", styles["right_bold"]),
    ])

    t = Table(table_data, colWidths=[160, 110, 75, 75, 75, 45])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#1B365D')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#1B365D')),
        ('LINEABOVE', (0, -1), (-1, -1), 1.0, colors.HexColor('#1B365D')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))
    elements.append(t)
    doc.build(elements)
    print(f"✅ Generated Portfolio Executive Summary: {summary_path}")

def generate_all_reports():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    styles = get_report_styles()

    print("\n=======================================================")
    print("Generating Financial Statement PDF Packages (Top 10)")
    print("=======================================================")

    build_portfolio_summary_pdf(styles)

    for comp in COMPANIES:
        name = comp["name"]
        slug = comp["slug"]
        c_type = comp["type"]
        ifs_ids = comp["ifs_ids"]

        comp_folder = os.path.join(OUTPUT_DIR, slug)
        os.makedirs(comp_folder, exist_ok=True)

        data = get_company_data(conn, ifs_ids)
        fin = process_financials(data)

        # 1. Income Statement PDF
        pnl_path = os.path.join(comp_folder, f"{slug}_Income_Statement.pdf")
        doc_pnl = SimpleDocTemplate(pnl_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        doc_pnl.build(build_pnl_elements(name, c_type, fin, styles))

        # 2. Balance Sheet PDF
        bs_path = os.path.join(comp_folder, f"{slug}_Balance_Sheet.pdf")
        doc_bs = SimpleDocTemplate(bs_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        doc_bs.build(build_bs_elements(name, c_type, fin, styles))

        # 3. Cash Flow PDF
        cf_path = os.path.join(comp_folder, f"{slug}_Cash_Flow.pdf")
        doc_cf = SimpleDocTemplate(cf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        doc_cf.build(build_cf_elements(name, c_type, fin, styles))

        # 4. Consolidated 3-Statement Package PDF
        combo_path = os.path.join(comp_folder, f"{slug}_Complete_Financial_Statements.pdf")
        doc_combo = SimpleDocTemplate(combo_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        combo_elements = []
        combo_elements.extend(build_pnl_elements(name, c_type, fin, styles))
        combo_elements.append(PageBreak())
        combo_elements.extend(build_bs_elements(name, c_type, fin, styles))
        combo_elements.append(PageBreak())
        combo_elements.extend(build_cf_elements(name, c_type, fin, styles))
        doc_combo.build(combo_elements)

        print(f"✅ Generated 4 PDFs for: {name} (in pdf_reports/{slug}/)")

    conn.close()
    print("\n✨ All PDF financial statements successfully generated in:")
    print(OUTPUT_DIR)

if __name__ == "__main__":
    generate_all_reports()
