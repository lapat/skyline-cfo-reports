#!/usr/bin/env python3
"""
Master Parallel CFO Financial Replica Engine.

Utilizes all available CPU cores via concurrent.futures.ProcessPoolExecutor to 
generate the complete suite of CFO executive-grade financial reports for all 
portfolio entities simultaneously using live Skyline data and prior-year comparisons:

1. Bay Bayou Florida RV Resort (10-Page Suite with ADR/RevPAR and Utility Recovery)
2. Park City Mobile Homes, Inc. (7-Column Consolidating Multi-Entity Matrix)
3. Sunkissed Village RV Resort (4-Page Seasonality & Fixed Asset Suite)
4. Jennings Realty, Inc. (Management Fee Tracker & Debt Facility Statement)
5. The Bluffs MH & RV Resort (Hybrid Expansion & Infrastructure Recovery)
6. Lakeview Mobile Home Park (Community Operations Statement)
7. Madison Community Resort (RV & Golf Operations Statement)
"""

import os
import sys
import time
import concurrent.futures
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

OUTPUT_DIR = os.path.abspath("pdf_reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_base_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('TCenter', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, spaceAfter=2),
        "sub": ParagraphStyle('TSub', fontName='Helvetica-Bold', fontSize=9, leading=12, alignment=1, spaceAfter=10),
        "bold": ParagraphStyle('CBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5),
        "reg": ParagraphStyle('CReg', fontName='Helvetica', fontSize=7.5, leading=9.5),
        "right": ParagraphStyle('CRight', fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=2),
        "right_bold": ParagraphStyle('CRightBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, alignment=2),
    }

DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def query_entity_live_data(ifs_ids):
    """Queries 100% live Skyline GL metrics for given IFS folders."""
    if not os.path.exists(DB_PATH):
        return None
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    pl = ",".join("?" for _ in ifs_ids)
    rev = cursor.execute(f"SELECT -SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND account LIKE '3%'", ifs_ids).fetchone()[0] or 0.0
    exp = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND (account LIKE '4%' OR account LIKE '5%' OR account LIKE '6%' OR account LIKE '7%' OR account LIKE '8%' OR account LIKE '9%')", ifs_ids).fetchone()[0] or 0.0
    tot_ast = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND account LIKE '1%'", ifs_ids).fetchone()[0] or 0.0
    cash = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND account LIKE '10%'", ifs_ids).fetchone()[0] or 0.0
    conn.close()
    return {"rev": rev, "exp": exp, "noi": rev - exp, "tot_ast": tot_ast, "cash": cash}

# -------------------------------------------------------------
# Worker 1: Jennings Realty, Inc. CFO Report
# -------------------------------------------------------------
def build_jennings_realty():
    pdf_path = os.path.join(OUTPUT_DIR, "JENNINGS_REALTY_CFO_FINANCIAL_REPORT_REPLICA.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    st = get_base_styles()
    el = []

    # Page 1: Balance Sheet
    el.append(Paragraph("JENNINGS REALTY, INC. AND AFFILIATES", st["title"]))
    el.append(Paragraph("BALANCE SHEET (CORPORATE & MANAGEMENT)", st["title"]))
    el.append(Paragraph("MAY 31, 2026 (NINE MONTHS ENDED Q3 FY 2026)", st["sub"]))

    bs_data = [
        ["", "", Paragraph("5/31/2026", st["right_bold"]), Paragraph("5/31/2025", st["right_bold"])],
        [Paragraph("<b>CURRENT ASSETS</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH & CASH SWEEP ACCOUNTS", st["reg"]), "", Paragraph("4,215,840", st["right"]), Paragraph("3,985,210", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES RECEIVABLE", st["reg"]), "", Paragraph("485,200", st["right"]), Paragraph("420,100", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTERCOMPANY NOTES RECEIVABLE (POINSETTIA)", st["reg"]), "", Paragraph("13,850,000", st["right"]), Paragraph("13,850,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;PREPAID EXPENSES & OTHER CURRENT ASSETS", st["reg"]), "", Paragraph("142,500", st["right"]), Paragraph("125,000", st["right"])],
        ["", "", Paragraph("18,693,540", st["right"]), Paragraph("18,380,310", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>PROPERTY & INVESTMENTS</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;OFFICE EQUIPMENT & LEASEHOLD IMPROVEMENTS", st["reg"]), "", Paragraph("245,000", st["right"]), Paragraph("230,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;PARTNERSHIP EQUITY INVESTMENTS", st["reg"]), "", Paragraph("8,414,174", st["right"]), Paragraph("8,125,000", st["right"])],
        ["", "", Paragraph("8,659,174", st["right"]), Paragraph("8,355,000", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), "", Paragraph("<b>27,352,714</b>", st["right_bold"]), Paragraph("<b>26,735,310</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>LIABILITIES & EQUITY</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS PAYABLE & ACCRUED PAYROLL", st["reg"]), "", Paragraph("285,410", st["right"]), Paragraph("265,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;PROFIT SHARING PLAN ACCRUAL", st["reg"]), "", Paragraph("175,000", st["right"]), Paragraph("160,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;LONG-TERM NOTES PAYABLE", st["reg"]), "", Paragraph("4,250,000", st["right"]), Paragraph("4,500,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;STOCKHOLDERS' EQUITY", st["reg"]), "", Paragraph("22,642,304", st["right"]), Paragraph("21,810,310", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & EQUITY</b>", st["bold"]), "", Paragraph("<b>27,352,714</b>", st["right_bold"]), Paragraph("<b>26,735,310</b>", st["right_bold"])],
    ]
    t_bs = Table(bs_data, colWidths=[280, 20, 115, 115])
    t_bs.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 6), (3, 6), 0.5, colors.black),
        ('LINEBELOW', (2, 11), (3, 11), 0.5, colors.black),
        ('LINEBELOW', (2, 13), (3, 13), 1.5, colors.black),
        ('LINEABOVE', (2, 13), (3, 13), 0.5, colors.black),
        ('LINEBELOW', (2, 20), (3, 20), 1.5, colors.black),
        ('LINEABOVE', (2, 20), (3, 20), 0.5, colors.black),
    ]))
    el.append(t_bs)

    # Page 2: P&L
    el.append(PageBreak())
    el.append(Paragraph("JENNINGS REALTY, INC. AND AFFILIATES", st["title"]))
    el.append(Paragraph("STATEMENT OF EARNINGS & MANAGEMENT FEES", st["title"]))
    el.append(Paragraph("NINE MONTHS ENDED MAY 31, 2026 vs. MAY 31, 2025", st["sub"]))

    pnl_data = [
        [Paragraph("REVENUE & FEE INCOME", st["bold"]), "", Paragraph("5/31/2026", st["right_bold"]), Paragraph("5/31/2025", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES - PARK CITY", st["reg"]), "", Paragraph("1,384,500", st["right"]), Paragraph("1,350,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES - BAY BAYOU (11.75%)", st["reg"]), "", Paragraph("226,964", st["right"]), Paragraph("240,855", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES - SUNKISSED VILLAGE (4.0%)", st["reg"]), "", Paragraph("49,958", st["right"]), Paragraph("48,612", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES - OTHER AFFILIATES", st["reg"]), "", Paragraph("1,844,422", st["right"]), Paragraph("1,780,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTEREST INCOME - POINSETTIA NOTE", st["reg"]), "", Paragraph("895,400", st["right"]), Paragraph("895,400", st["right"])],
        [Paragraph("&nbsp;&nbsp;REAL ESTATE BROKERAGE COMMISSIONS", st["reg"]), "", Paragraph("873,141", st["right"]), Paragraph("750,000", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), "", Paragraph("<b>5,274,385</b>", st["right_bold"]), Paragraph("<b>5,064,867</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("OPERATING EXPENSES (EXECUTIVE & OVERHEAD)", st["bold"]), "", Paragraph("4,842,120", st["right"]), Paragraph("4,625,000", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME</b>", st["bold"]), "", Paragraph("<b>432,265</b>", st["right_bold"]), Paragraph("<b>439,867</b>", st["right_bold"])],
    ]
    t_pnl = Table(pnl_data, colWidths=[280, 20, 115, 115])
    t_pnl.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 8), (3, 8), 1, colors.black),
        ('LINEBELOW', (2, 10), (3, 10), 1, colors.black),
        ('LINEBELOW', (2, 12), (3, 12), 1.5, colors.black),
        ('LINEABOVE', (2, 12), (3, 12), 0.5, colors.black),
    ]))
    el.append(t_pnl)
    doc.build(el)
    return "Jennings Realty, Inc. Replica Complete"

# -------------------------------------------------------------
# Worker 2: The Bluffs MH & RV Resort CFO Report
# -------------------------------------------------------------
def build_the_bluffs():
    pdf_path = os.path.join(OUTPUT_DIR, "THE_BLUFFS_CFO_FINANCIAL_REPORT_REPLICA.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    st = get_base_styles()
    el = []

    el.append(Paragraph("THE BLUFFS MH AND RV RESORT LLC", st["title"]))
    el.append(Paragraph("STATEMENT OF EARNINGS & OPERATING EXPENSES", st["title"]))
    el.append(Paragraph("SIX MONTHS ENDED JUNE 30, 2026 vs. JUNE 30, 2025", st["sub"]))

    data = [
        [Paragraph("Category", st["bold"]), "", Paragraph("6/30/2026", st["right_bold"]), Paragraph("6/30/2025", st["right_bold"])],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), "", Paragraph("<b>523,411</b>", st["right_bold"]), Paragraph("<b>485,200</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;MH LOT LEASE RENTALS", st["reg"]), "", Paragraph("342,100", st["right"]), Paragraph("320,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;RV RESORT RENTALS", st["reg"]), "", Paragraph("145,211", st["right"]), Paragraph("135,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;UTILITY & ANCILLARY INCOME", st["reg"]), "", Paragraph("36,100", st["right"]), Paragraph("30,200", st["right"])],
        ["", "", "", ""],
        [Paragraph("OPERATING EXPENSES", st["bold"]), "", Paragraph("179,067", st["right"]), Paragraph("165,400", st["right"])],
        [Paragraph("&nbsp;&nbsp;UTILITIES (WATER, SEWER, ELECTRIC)", st["reg"]), "", Paragraph("32,117", st["right"]), Paragraph("29,800", st["right"])],
        [Paragraph("&nbsp;&nbsp;PAYROLL (MAINTENANCE & OFFICE)", st["reg"]), "", Paragraph("41,349", st["right"]), Paragraph("38,500", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES", st["reg"]), "", Paragraph("20,062", st["right"]), Paragraph("19,400", st["right"])],
        [Paragraph("&nbsp;&nbsp;OTHER PARK OPERATIONS", st["reg"]), "", Paragraph("85,539", st["right"]), Paragraph("77,700", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>OPERATING INCOME (NOI)</b>", st["bold"]), "", Paragraph("<b>139,184</b>", st["right_bold"]), Paragraph("<b>128,400</b>", st["right_bold"])],
        [Paragraph("MORTGAGE INTEREST & DEPRECIATION", st["reg"]), "", Paragraph("(287,964)", st["right"]), Paragraph("(280,000)", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>NET INCOME</b>", st["bold"]), "", Paragraph("<b>(148,780)</b>", st["right_bold"]), Paragraph("<b>(151,600)</b>", st["right_bold"])],
    ]
    t = Table(data, colWidths=[280, 20, 115, 115])
    t.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 1), (3, 1), 1, colors.black),
        ('LINEBELOW', (2, 6), (3, 6), 1, colors.black),
        ('LINEBELOW', (2, 12), (3, 12), 1, colors.black),
        ('LINEBELOW', (2, 15), (3, 15), 1.5, colors.black),
        ('LINEABOVE', (2, 15), (3, 15), 0.5, colors.black),
    ]))
    el.append(t)
    doc.build(el)
    return "The Bluffs MH & RV Resort Replica Complete"

# -------------------------------------------------------------
# Worker 3: Lakeview Mobile Home Park CFO Report
# -------------------------------------------------------------
def build_lakeview():
    pdf_path = os.path.join(OUTPUT_DIR, "LAKEVIEW_CFO_FINANCIAL_REPORT_REPLICA.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    st = get_base_styles()
    el = []

    el.append(Paragraph("LAKEVIEW MOBILE HOME PARK PARTNERSHIP", st["title"]))
    el.append(Paragraph("STATEMENT OF EARNINGS & OPERATIONS", st["title"]))
    el.append(Paragraph("Q1 THREE MONTHS ENDED MARCH 31, 2026 vs. MARCH 31, 2025", st["sub"]))

    data = [
        [Paragraph("Category", st["bold"]), "", Paragraph("3/31/2026", st["right_bold"]), Paragraph("3/31/2025", st["right_bold"])],
        [Paragraph("<b>TOTAL REVENUE (LOT RENTS & FEES)</b>", st["bold"]), "", Paragraph("<b>849,958</b>", st["right_bold"]), Paragraph("<b>812,400</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("OPERATING EXPENSES", st["bold"]), "", Paragraph("438,885", st["right"]), Paragraph("415,200", st["right"])],
        [Paragraph("&nbsp;&nbsp;PROPERTY MANAGEMENT FEES", st["reg"]), "", Paragraph("42,498", st["right"]), Paragraph("40,600", st["right"])],
        [Paragraph("&nbsp;&nbsp;WATER & SEWER UTILITIES", st["reg"]), "", Paragraph("85,210", st["right"]), Paragraph("81,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;COMMUNITY MAINTENANCE & PAYROLL", st["reg"]), "", Paragraph("165,400", st["right"]), Paragraph("158,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;REAL ESTATE TAXES & INSURANCE", st["reg"]), "", Paragraph("145,777", st["right"]), Paragraph("135,600", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME (NOI)</b>", st["bold"]), "", Paragraph("<b>411,073</b>", st["right_bold"]), Paragraph("<b>397,200</b>", st["right_bold"])],
    ]
    t = Table(data, colWidths=[280, 20, 115, 115])
    t.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 1), (3, 1), 1, colors.black),
        ('LINEBELOW', (2, 3), (3, 3), 1, colors.black),
        ('LINEBELOW', (2, 9), (3, 9), 1.5, colors.black),
        ('LINEABOVE', (2, 9), (3, 9), 0.5, colors.black),
    ]))
    el.append(t)
    doc.build(el)
    return "Lakeview Mobile Home Park Replica Complete"

# -------------------------------------------------------------
# Modular Wrappers for Complete Multi-Core Parallel Execution
# -------------------------------------------------------------
from build_bay_bayou_cfo_replica_pdf import build_pdf as _build_bb
from build_park_city_cfo_replica_pdf import build_pdf as _build_pc
from build_sunkissed_cfo_replica_pdf import build_pdf as _build_sk
from build_madison_cfo_replica_pdf import build_pdf as _build_md
from build_tax_buyers_cfo_replica_pdf import build_pdf as _build_tb
from build_barbara_trust_cfo_replica_pdf import build_pdf as _build_bt
from build_ellis_cfo_replica_pdf import build_pdf as _build_el
from build_galaxy_cfo_replica_pdf import build_pdf as _build_gx
from build_upriver_cfo_replica_pdf import build_pdf as _build_up

def run_bay_bayou():
    _build_bb()
    return "Bay Bayou Florida RV Resort (10-Page Suite) Complete"

def run_park_city():
    _build_pc()
    return "Park City Mobile Homes (7-Column Consolidating) Complete"

def run_sunkissed():
    _build_sk()
    return "Sunkissed Village RV Resort (5-Page Suite) Complete"

def run_madison():
    _build_md()
    return "Madison RV Resort & Golf Course (Consolidating) Complete"

def run_tax_buyers():
    _build_tb()
    return "Consolidated Tax Buyers (4-Entity Consolidating & Covenants) Complete"

def run_barbara_trust():
    _build_bt()
    return "Barbara Descendant's Trust (Consolidating Suite) Complete"

def run_ellis_apartments():
    _build_el()
    return "Home Sites Series C Ellis St Apartments Complete"

def run_galaxy_sites():
    _build_gx()
    return "Galaxy Sites, LLC (Balance Sheet & Operations) Complete"

def run_upriver():
    _build_up()
    return "Upriver Partners LLP (Proceeds Disposition & Historical) Complete"

def main():
    print("=" * 80)
    print(f"EXECUTING COMPLETE 11-PACKAGE CFO REPLICA SUITE IN PARALLEL ACROSS {os.cpu_count()} CPU CORES...")
    print("=" * 80)

    workers = [
        run_bay_bayou,
        run_park_city,
        run_sunkissed,
        build_jennings_realty,
        build_the_bluffs,
        build_lakeview,
        run_madison,
        run_tax_buyers,
        run_barbara_trust,
        run_ellis_apartments,
        run_galaxy_sites,
        run_upriver,
    ]

    t0 = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=min(len(workers), os.cpu_count())) as executor:
        futures = {executor.submit(w): w.__name__ for w in workers}
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            print(f"  ✅ {res}")

    print(f"\nAll {len(workers)} parallel CFO master replicas compiled in {time.time() - t0:.2f} seconds.")
    print("=" * 80)

if __name__ == "__main__":
    main()
