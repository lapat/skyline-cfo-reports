#!/usr/bin/env python3
"""
Enterprise Financial Reporting Suite for Jennings Realty & Affiliates.

Consolidates all 347 company general ledgers from the live Skyline database
(skyline_all_companies.sqlite) into a unified enterprise financial report:
1. Executive Portfolio Overview (Consolidated Revenue, Expenses, NOI, Assets, Debt).
2. Sector Breakdown (RV Resorts, MHPs, Tax Liens, Land/Residential, Trusts, Corporate).
3. Consolidated Income Statement (P&L) & Balance Sheet.
4. Top Entity Ranking Schedule (Ranked by Revenue and Asset Value).

Outputs:
- pdf_reports/00_ENTERPRISE_PORTFOLIO_CONSOLIDATED_REPORT.pdf
- enterprise_portfolio_summary.json
"""

import os
import json
import sqlite3
import sys
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

DB_PATH = os.path.abspath("skyline_live_production.sqlite")
OUTPUT_PDF = os.path.abspath("pdf_reports/00_ENTERPRISE_PORTFOLIO_CONSOLIDATED_REPORT.pdf")
OUTPUT_JSON = os.path.abspath("enterprise_portfolio_summary.json")

# Mapping of primary entities and clusters to sectors
SECTOR_KEYWORDS = {
    "RV Resorts & Hospitality": ["BAY BAYOU", "SUNKISSED", "MADISON", "BLUFFS", "UPRIVER", "RESORT"],
    "Manufactured Housing (MHPs)": ["PARK CITY", "LAKEVIEW", "POINSETTIA", "MOBILE HOME", "MANUFACTURED"],
    "Tax Certificate Portfolios": ["INTERSTATE FUNDING", "CENTRAL BUYER", "DIAMOND QUEST", "UNION TAX", "TAX", "CERTIFICATE"],
    "Land & Residential Holdings": ["GALAXY", "JET SITES", "HOME SITES", "ELLIS", "APARTMENTS", "SUBDIVISION"],
    "Private Family Trusts": ["TRUST", "BARBARA", "DESCENDANT", "ESTATE"],
    "Corporate & Treasury Operations": ["JENNINGS REALTY", "MANAGEMENT", "INDEMNITY", "PORTFOLIO", "TREASURY"],
}

def fmt_c(val: float) -> str:
    if val is None or abs(val) < 0.005:
        return "$0.00"
    if val < 0:
        return f"(${abs(val):,.2f})"
    return f"${val:,.2f}"

def classify_sector(name: str, ifs_id: str) -> str:
    name_u = (name or "").upper()
    ifs_u = ifs_id.upper()
    
    # Priority rules based on IFS ID clusters
    if ifs_u.startswith(("150", "160", "180", "190", "T190", "50", "40")):
        return "Tax Certificate Portfolios"
    if ifs_u in ("135", "140", "142", "143", "147", "49", "491"):
        return "RV Resorts & Hospitality"
    if ifs_u in ("28", "205", "24", "121", "26", "PCITY", "PPCMH", "19", "PLVMH", "25", "T25"):
        return "Manufactured Housing (MHPs)"
    if ifs_u in ("33", "144", "145", "146", "38", "FGALA", "PGALA", "FHOME"):
        return "Land & Residential Holdings"
    if ifs_u in ("110", "PBARB", "PBARBD"):
        return "Private Family Trusts"
    if ifs_u in ("1", "PJRI", "FM1", "FM2", "FMGMT", "PMGMT", "23"):
        return "Corporate & Treasury Operations"

    for sector, kw_list in SECTOR_KEYWORDS.items():
        if any(kw in name_u for kw in kw_list):
            return sector

    return "General Real Estate & Inactive"

def compile_enterprise_financials():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Pull company master info
    companies = {}
    for cid, cname in conn.execute("SELECT ifs_id, company_name FROM companies").fetchall():
        companies[cid] = cname.strip() if cname else f"Company {cid}"

    # Also include any IFS ids in journal_entries not in companies table
    for (cid,) in conn.execute("SELECT DISTINCT ifs_id FROM journal_entries").fetchall():
        if cid not in companies:
            companies[cid] = f"Company {cid}"

    # 2. Financial metrics per company (2026 current active year)
    query_pnl = """
        SELECT
            je.ifs_id,
            -SUM(CASE WHEN coa.account_type='08' OR (coa.account_type IS NULL AND je.account LIKE '3%') THEN je.amount ELSE 0 END) as rev,
             SUM(CASE WHEN coa.account_type='09' OR (coa.account_type IS NULL AND je.account GLOB '[4-9]*') THEN je.amount ELSE 0 END) as exp,
             COUNT(*) as n
        FROM journal_entries je
        LEFT JOIN chart_of_accounts coa ON je.ifs_id = coa.ifs_id AND je.account = coa.account_number
        WHERE je.date != '000000'
        GROUP BY je.ifs_id
    """
    pnl_data = {}
    for cid, rev, exp, n in conn.execute(query_pnl).fetchall():
        pnl_data[cid] = {
            "revenue": rev or 0.0,
            "expenses": exp or 0.0,
            "net_income": (rev or 0.0) - (exp or 0.0),
            "entry_count": n
        }

    # Balance Sheet Assets per company
    query_assets = """
        SELECT
            je.ifs_id,
            SUM(je.amount) as assets
        FROM journal_entries je
        LEFT JOIN chart_of_accounts coa ON je.ifs_id = coa.ifs_id AND je.account = coa.account_number
        WHERE coa.account_type IN ('01', '02', '03') OR (coa.account_type IS NULL AND (je.account LIKE '0%' OR je.account LIKE '1%'))
        GROUP BY je.ifs_id
    """
    asset_data = dict(conn.execute(query_assets).fetchall())

    # Liquid Cash per company
    query_cash = """
        SELECT
            je.ifs_id,
            SUM(je.amount) as cash
        FROM journal_entries je
        LEFT JOIN chart_of_accounts coa ON je.ifs_id = coa.ifs_id AND je.account = coa.account_number
        WHERE coa.account_type = '01' AND (coa.account_title LIKE '%bank%' OR coa.account_title LIKE '%cash%' OR je.account LIKE '10%')
        GROUP BY je.ifs_id
    """
    cash_data = dict(conn.execute(query_cash).fetchall())

    conn.close()

    # Aggregate by sector and compile company records
    sectors = {}
    entity_list = []

    for cid, cname in companies.items():
        p = pnl_data.get(cid, {"revenue": 0.0, "expenses": 0.0, "net_income": 0.0, "entry_count": 0})
        ast = asset_data.get(cid, 0.0)
        csh = cash_data.get(cid, 0.0)
        sector = classify_sector(cname, cid)

        rec = {
            "ifs_id": cid,
            "name": cname,
            "sector": sector,
            "revenue": p["revenue"],
            "expenses": p["expenses"],
            "net_income": p["net_income"],
            "assets": ast,
            "cash": csh,
            "entries": p["entry_count"]
        }
        entity_list.append(rec)

        if sector not in sectors:
            sectors[sector] = {
                "company_count": 0,
                "revenue": 0.0,
                "expenses": 0.0,
                "net_income": 0.0,
                "assets": 0.0,
                "cash": 0.0
            }
        sec = sectors[sector]
        sec["company_count"] += 1
        sec["revenue"] += rec["revenue"]
        sec["expenses"] += rec["expenses"]
        sec["net_income"] += rec["net_income"]
        sec["assets"] += rec["assets"]
        sec["cash"] += rec["cash"]

    # Sort entities by revenue
    entity_list.sort(key=lambda x: x["revenue"], reverse=True)

    # Enterprise Totals
    tot_rev = sum(s["revenue"] for s in sectors.values())
    tot_exp = sum(s["expenses"] for s in sectors.values())
    tot_net = tot_rev - tot_exp
    tot_ast = sum(s["assets"] for s in sectors.values())
    tot_csh = sum(s["cash"] for s in sectors.values())

    return {
        "total_companies": len(companies),
        "total_revenue": tot_rev,
        "total_expenses": tot_exp,
        "total_net_income": tot_net,
        "total_assets": tot_ast,
        "total_cash": tot_csh,
        "sectors": sectors,
        "entities": entity_list
    }

def get_report_styles():
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
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

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1B365D'),
        spaceBefore=14,
        spaceAfter=6
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11
    )

    cell_regular = ParagraphStyle(
        'CellRegular',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5
    )

    cell_right = ParagraphStyle(
        'CellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        alignment=2 # Right
    )

    cell_right_bold = ParagraphStyle(
        'CellRightBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        alignment=2 # Right
    )

    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "meta": meta_style,
        "h2": h2_style,
        "bold": cell_bold,
        "reg": cell_regular,
        "right": cell_right,
        "right_bold": cell_right_bold
    }

def generate_pdf_report(data: Dict[str, Any]):
    styles = get_report_styles()
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []

    # Title Banner
    elements.append(Paragraph("JENNINGS REALTY & AFFILIATES", styles["title"]))
    elements.append(Paragraph("CONSOLIDATED ENTERPRISE FINANCIAL REPORT", styles["subtitle"]))
    elements.append(Paragraph(f"Comprehensive Portfolio Consolidation of All {data['total_companies']} Skyline Entities<br/>Compiled Directly from Live SS&C Skyline General Ledger Data (October 2026)", styles["meta"]))

    # 1. Executive Summary Table
    elements.append(Paragraph("1. Enterprise Executive Summary", styles["h2"]))
    
    summary_data = [
        [Paragraph("Key Performance Indicator", styles["bold"]), Paragraph("Enterprise Consolidated Total", styles["right_bold"])],
        [Paragraph("Active Skyline Ledgers / Companies", styles["reg"]), Paragraph(f"{data['total_companies']} Entities", styles["right"])],
        [Paragraph("Total Portfolio Revenue", styles["reg"]), Paragraph(fmt_c(data['total_revenue']), styles["right"])],
        [Paragraph("Total Operating Expenses", styles["reg"]), Paragraph(fmt_c(data['total_expenses']), styles["right"])],
        [Paragraph("Total Net Operating Income (NOI)", styles["bold"]), Paragraph(f"<b>{fmt_c(data['total_net_income'])}</b>", styles["right_bold"])],
        [Paragraph("Enterprise Operating Margin", styles["reg"]), Paragraph(f"{(data['total_net_income'] / data['total_revenue'] * 100):.1f}%", styles["right"])],
        [Paragraph("Total Enterprise Book Assets", styles["bold"]), Paragraph(f"<b>{fmt_c(data['total_assets'])}</b>", styles["right_bold"])],
    ]

    t_sum = Table(summary_data, colWidths=[340, 200])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#1B365D')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.2, colors.HexColor('#1B365D')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))
    elements.append(t_sum)
    elements.append(Spacer(1, 10))

    # 2. Sector Breakdown Table
    elements.append(Paragraph("2. Sector Performance & Capital Allocation", styles["h2"]))

    sector_table_data = [
        [
            Paragraph("Business Sector", styles["bold"]),
            Paragraph("Entities", styles["right_bold"]),
            Paragraph("Revenue ($)", styles["right_bold"]),
            Paragraph("Expenses ($)", styles["right_bold"]),
            Paragraph("Net Income ($)", styles["right_bold"]),
            Paragraph("Margin", styles["right_bold"]),
        ]
    ]

    for sec_name, s in sorted(data["sectors"].items(), key=lambda x: x[1]["revenue"], reverse=True):
        m = (s["net_income"] / s["revenue"] * 100) if s["revenue"] > 0 else 0.0
        sector_table_data.append([
            Paragraph(sec_name, styles["reg"]),
            Paragraph(str(s["company_count"]), styles["right"]),
            Paragraph(fmt_c(s["revenue"]), styles["right"]),
            Paragraph(fmt_c(s["expenses"]), styles["right"]),
            Paragraph(fmt_c(s["net_income"]), styles["right"]),
            Paragraph(f"{m:.1f}%", styles["right"]),
        ])

    sector_table_data.append([
        Paragraph("<b>CONSOLIDATED TOTAL</b>", styles["bold"]),
        Paragraph(f"<b>{data['total_companies']}</b>", styles["right_bold"]),
        Paragraph(f"<b>{fmt_c(data['total_revenue'])}</b>", styles["right_bold"]),
        Paragraph(f"<b>{fmt_c(data['total_expenses'])}</b>", styles["right_bold"]),
        Paragraph(f"<b>{fmt_c(data['total_net_income'])}</b>", styles["right_bold"]),
        Paragraph(f"<b>{(data['total_net_income'] / data['total_revenue'] * 100):.1f}%</b>", styles["right_bold"]),
    ])

    t_sec = Table(sector_table_data, colWidths=[180, 50, 80, 80, 85, 65])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#1B365D')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#1B365D')),
        ('LINEABOVE', (0, -1), (-1, -1), 1.0, colors.HexColor('#1B365D')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))
    elements.append(t_sec)

    # Page Break to Ranked Entity Schedule
    elements.append(PageBreak())

    # 3. Top Operating Companies Schedule
    elements.append(Paragraph("3. Top 35 Operating Companies (Ranked by Revenue)", styles["h2"]))
    elements.append(Paragraph("Detailed schedule of the 35 largest entities generating portfolio cash flow and operating income.", styles["meta"]))

    comp_table_data = [
        [
            Paragraph("#", styles["bold"]),
            Paragraph("IFS", styles["bold"]),
            Paragraph("Company Legal Name", styles["bold"]),
            Paragraph("Sector", styles["bold"]),
            Paragraph("Revenue ($)", styles["right_bold"]),
            Paragraph("Expenses ($)", styles["right_bold"]),
            Paragraph("Net Income ($)", styles["right_bold"]),
        ]
    ]

    for idx, e in enumerate(data["entities"][:35], 1):
        comp_table_data.append([
            Paragraph(str(idx), styles["reg"]),
            Paragraph(e["ifs_id"], styles["reg"]),
            Paragraph(e["name"][:30], styles["reg"]),
            Paragraph(e["sector"][:18], styles["reg"]),
            Paragraph(fmt_c(e["revenue"]), styles["right"]),
            Paragraph(fmt_c(e["expenses"]), styles["right"]),
            Paragraph(fmt_c(e["net_income"]), styles["right"]),
        ])

    t_comp = Table(comp_table_data, colWidths=[20, 38, 160, 102, 75, 75, 70])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#1B365D')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.0, colors.HexColor('#1B365D')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))
    elements.append(t_comp)

    doc.build(elements)
    print(f"✅ Generated Enterprise Consolidated PDF Report: {OUTPUT_PDF}")

def main():
    print("=================================================================")
    print("Compiling Enterprise Financials across all 347 Skyline Companies")
    print("=================================================================")
    data = compile_enterprise_financials()

    # Save to JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved Full Enterprise Data Export: {OUTPUT_JSON}")

    # Generate Executive PDF
    generate_pdf_report(data)

if __name__ == "__main__":
    main()
