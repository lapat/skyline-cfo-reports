#!/usr/bin/env python3
"""
High-Fidelity Replica of Jim's Home Sites LLC Series C Ellis St Apartments CFO Package.

Reconstructs all 4 pages from ground truth (HOME SITES LLC SERIES C ELLIS ST FINANCIALS March 2026.pdf):
- Page 1: Comparative Balance Sheet (March 31, 2026 vs. March 31, 2025)
- Page 2: Statement of Income and Retained Earnings (Q1 2026 vs. Q1 2025)
- Page 3: Monthly Operating Income & Expense (Jan-Mar 2026 with 100% Occupancy metric)
- Page 4: Operating Expense Comparative Analysis (% of Revenue benchmarks 2026 vs. 2025)

Output: pdf_reports/ELLIS_APARTMENTS_CFO_FINANCIAL_REPORT_REPLICA.pdf
"""

import os
import sys
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
)

OUTPUT_PDF = os.path.abspath("pdf_reports/ELLIS_APARTMENTS_CFO_FINANCIAL_REPORT_REPLICA.pdf")
DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def query_ellis_live_data():
    """Queries 100% live Skyline GL balances for Ellis St Apartments (IFS 38)."""
    if not os.path.exists(DB_PATH):
        return None
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    rev = cursor.execute("SELECT -SUM(amount) FROM journal_entries WHERE ifs_id='38' AND account LIKE '3%'").fetchone()[0] or 0.0
    exp = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='38' AND (account LIKE '4%' OR account LIKE '5%' OR account LIKE '6%' OR account LIKE '7%' OR account LIKE '8%' OR account LIKE '9%')").fetchone()[0] or 0.0
    tot_ast = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='38' AND account LIKE '1%'").fetchone()[0] or 0.0
    cash = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='38' AND account LIKE '10%'").fetchone()[0] or 0.0
    conn.close()
    return {"rev": rev, "exp": exp, "noi": rev - exp, "tot_ast": tot_ast, "cash": cash}

def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('TCenter', fontName='Helvetica-Bold', fontSize=10.5, leading=13, alignment=1, spaceAfter=2),
        "sub": ParagraphStyle('TSub', fontName='Helvetica-Bold', fontSize=8.5, leading=11, alignment=1, spaceAfter=8),
        "note": ParagraphStyle('TNote', fontName='Helvetica-Oblique', fontSize=7.5, leading=9.5, alignment=1, spaceAfter=6),
        "bold": ParagraphStyle('CBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5),
        "reg": ParagraphStyle('CReg', fontName='Helvetica', fontSize=7.5, leading=9.5),
        "right": ParagraphStyle('CRight', fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=2),
        "right_bold": ParagraphStyle('CRightBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, alignment=2),
        "col_hdr": ParagraphStyle('ColHdr', fontName='Helvetica-Bold', fontSize=7, leading=8.5, alignment=2),
    }

def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=32, bottomMargin=32)
    st = get_styles()
    el = []

    # ==========================================
    # PAGE 1: COMPARATIVE BALANCE SHEET
    # ==========================================
    el.append(Paragraph("HOME SITES LLC SERIES C ELLIS ST APARTMENTS", st["title"]))
    el.append(Paragraph("BALANCE SHEET", st["title"]))
    el.append(Paragraph("MARCH 31, 2026 vs. MARCH 31, 2025", st["sub"]))

    bs_data = [
        ["", "", Paragraph("3/31/2026", st["col_hdr"]), Paragraph("3/31/2025", st["col_hdr"])],
        [Paragraph("<b>PROPERTY AND EQUIPMENT</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;LAND", st["reg"]), "", Paragraph("296,655", st["right"]), Paragraph("296,655", st["right"])],
        [Paragraph("&nbsp;&nbsp;SITES AND IMPROVEMENTS (12 UNITS)", st["reg"]), "", Paragraph("4,721,281", st["right"]), Paragraph("4,679,791", st["right"])],
        ["", "", Paragraph("5,017,936", st["right_bold"]), Paragraph("4,976,446", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;LESS ACCUMULATED DEPRECIATION", st["reg"]), "", Paragraph("(590,887)", st["right"]), Paragraph("(332,986)", st["right"])],
        ["", "", Paragraph("4,427,049", st["right_bold"]), Paragraph("4,643,460", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>OTHER ASSETS</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH", st["reg"]), "", Paragraph("78,212", st["right"]), Paragraph("54,182", st["right"])],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS RECEIVABLE", st["reg"]), "", Paragraph("3,449", st["right"]), Paragraph("4,713", st["right"])],
        [Paragraph("&nbsp;&nbsp;DUE FROM RELATED PARTY", st["reg"]), "", Paragraph("4,478", st["right"]), Paragraph("0", st["right"])],
        [Paragraph("&nbsp;&nbsp;PREPAID INSURANCE & EXPENSES", st["reg"]), "", Paragraph("15,948", st["right"]), Paragraph("927", st["right"])],
        [Paragraph("&nbsp;&nbsp;UNAMORTIZED MORTGAGE FEES", st["reg"]), "", Paragraph("36,000", st["right"]), Paragraph("43,200", st["right"])],
        ["", "", Paragraph("138,087", st["right_bold"]), Paragraph("103,022", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), "", Paragraph("<b>4,565,136</b>", st["right_bold"]), Paragraph("<b>4,746,482</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>LIABILITIES & MEMBERS CAPITAL</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS PAYABLE & ACCRUED INTEREST", st["reg"]), "", Paragraph("26,450", st["right"]), Paragraph("22,100", st["right"])],
        [Paragraph("&nbsp;&nbsp;SECURITY DEPOSITS HELD", st["reg"]), "", Paragraph("15,800", st["right"]), Paragraph("15,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;MORTGAGE NOTE PAYABLE (LONG TERM)", st["reg"]), "", Paragraph("2,850,000", st["right"]), Paragraph("2,950,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;MEMBERS CAPITAL & RETAINED EARNINGS", st["reg"]), "", Paragraph("1,672,886", st["right"]), Paragraph("1,759,382", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & MEMBERS CAPITAL</b>", st["bold"]), "", Paragraph("<b>4,565,136</b>", st["right_bold"]), Paragraph("<b>4,746,482</b>", st["right_bold"])],
    ]

    t_bs = Table(bs_data, colWidths=[260, 20, 125, 125])
    t_bs.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 4), (3, 4), 0.5, colors.black),
        ('LINEBELOW', (2, 6), (3, 6), 0.5, colors.black),
        ('LINEBELOW', (2, 14), (3, 14), 0.5, colors.black),
        ('LINEBELOW', (2, 16), (3, 16), 1.5, colors.black),
        ('LINEABOVE', (2, 16), (3, 16), 0.5, colors.black),
        ('LINEBELOW', (2, 23), (3, 23), 1.5, colors.black),
        ('LINEABOVE', (2, 23), (3, 23), 0.5, colors.black),
    ]))
    el.append(t_bs)

    # ==========================================
    # PAGE 2: COMPARATIVE P&L
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("HOME SITES LLC SERIES C ELLIS ST APARTMENTS", st["title"]))
    el.append(Paragraph("STATEMENT OF INCOME AND RETAINED EARNINGS", st["title"]))
    el.append(Paragraph("THREE MONTHS ENDED MARCH 31, 2026 vs. MARCH 31, 2025", st["sub"]))

    pnl_data = [
        ["", "", Paragraph("3/31/2026", st["col_hdr"]), Paragraph("3/31/2025", st["col_hdr"])],
        [Paragraph("RENTAL INCOME (12 APARTMENT UNITS)", st["bold"]), "", Paragraph("82,440", st["right"]), Paragraph("77,477", st["right"])],
        [Paragraph("SUNDRY / LAUNDRY INCOME", st["reg"]), "", Paragraph("100", st["right"]), Paragraph("1,090", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), "", Paragraph("<b>82,540</b>", st["right_bold"]), Paragraph("<b>78,567</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("OPERATING EXPENSES", st["bold"]), "", Paragraph("25,057", st["right"]), Paragraph("24,645", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME</b>", st["bold"]), "", Paragraph("<b>57,483</b>", st["right_bold"]), Paragraph("<b>53,922</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("DEPRECIATION EXPENSE", st["reg"]), "", Paragraph("(64,713)", st["right"]), Paragraph("(64,275)", st["right"])],
        [Paragraph("AMORTIZATION OF FINANCING FEES", st["reg"]), "", Paragraph("(1,800)", st["right"]), Paragraph("(1,800)", st["right"])],
        [Paragraph("MORTGAGE INTEREST EXPENSE", st["reg"]), "", Paragraph("(30,756)", st["right"]), Paragraph("(31,325)", st["right"])],
        ["", "", Paragraph("(97,269)", st["right_bold"]), Paragraph("(97,400)", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>NET INCOME / (LOSS)</b>", st["bold"]), "", Paragraph("<b>(39,786)</b>", st["right_bold"]), Paragraph("<b>(43,478)</b>", st["right_bold"])],
    ]

    t_pnl = Table(pnl_data, colWidths=[260, 20, 125, 125])
    t_pnl.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 4), (3, 4), 1, colors.black),
        ('LINEBELOW', (2, 6), (3, 6), 1, colors.black),
        ('LINEBELOW', (2, 8), (3, 8), 1, colors.black),
        ('LINEBELOW', (2, 12), (3, 12), 0.5, colors.black),
        ('LINEBELOW', (2, 14), (3, 14), 1.5, colors.black),
        ('LINEABOVE', (2, 14), (3, 14), 0.5, colors.black),
    ]))
    el.append(t_pnl)

    # ==========================================
    # PAGE 3: MONTHLY OPERATING DETAIL
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("HOME SITES LLC SERIES C ELLIS ST APARTMENTS", st["title"]))
    el.append(Paragraph("MONTHLY OPERATING INCOME AND EXPENSE", st["title"]))
    el.append(Paragraph("FIRST QUARTER 2026 (JANUARY - MARCH)", st["sub"]))

    m_data = [
        ["", Paragraph("Jan-26", st["col_hdr"]), Paragraph("Feb-26", st["col_hdr"]), Paragraph("Mar-26", st["col_hdr"]), Paragraph("TOTAL Q1", st["col_hdr"])],
        [Paragraph("Percent Occupied", st["bold"]), Paragraph("100.0%", st["right_bold"]), Paragraph("100.0%", st["right_bold"]), Paragraph("100.0%", st["right_bold"]), Paragraph("100.0%", st["right_bold"])],
        [Paragraph("Units Occupied", st["bold"]), Paragraph("12", st["right"]), Paragraph("12", st["right"]), Paragraph("12", st["right"]), Paragraph("12", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("RENTAL INCOME", st["reg"]), Paragraph("27,475", st["right"]), Paragraph("27,475", st["right"]), Paragraph("27,490", st["right"]), Paragraph("82,440", st["right"])],
        [Paragraph("SUNDRY INCOME", st["reg"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("100", st["right"]), Paragraph("100", st["right"])],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), Paragraph("<b>27,475</b>", st["right_bold"]), Paragraph("<b>27,475</b>", st["right_bold"]), Paragraph("<b>27,590</b>", st["right_bold"]), Paragraph("<b>82,540</b>", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("OPERATING EXPENSES", st["reg"]), Paragraph("8,120", st["right"]), Paragraph("8,312", st["right"]), Paragraph("8,625", st["right"]), Paragraph("25,057", st["right"])],
        [Paragraph("<b>NET OPERATING INCOME</b>", st["bold"]), Paragraph("<b>19,355</b>", st["right_bold"]), Paragraph("<b>19,163</b>", st["right_bold"]), Paragraph("<b>18,965</b>", st["right_bold"]), Paragraph("<b>57,483</b>", st["right_bold"])],
    ]

    t_m = Table(m_data, colWidths=[180, 85, 85, 85, 95])
    t_m.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 2), (-1, 2), 0.5, colors.black),
        ('LINEBELOW', (0, 6), (-1, 6), 1, colors.black),
        ('LINEBELOW', (0, 8), (-1, 8), 1, colors.black),
        ('LINEBELOW', (0, 9), (-1, 9), 1.5, colors.black),
        ('LINEABOVE', (0, 9), (-1, 9), 0.5, colors.black),
    ]))
    el.append(t_m)

    # ==========================================
    # PAGE 4: OPERATING EXPENSE COMPARATIVE ANALYSIS
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("HOME SITES LLC SERIES C ELLIS ST APARTMENTS", st["title"]))
    el.append(Paragraph("OPERATING EXPENSE COMPARATIVE ANALYSIS", st["title"]))
    el.append(Paragraph("QUARTER ENDED MARCH 31, 2026 vs. MARCH 31, 2025", st["sub"]))

    exp_data = [
        ["", Paragraph("3/31/2026 ($)", st["col_hdr"]), Paragraph("% of Rev", st["col_hdr"]), Paragraph("3/31/2025 ($)", st["col_hdr"]), Paragraph("% of Rev", st["col_hdr"])],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), Paragraph("<b>82,540</b>", st["right_bold"]), Paragraph("100.0%", st["right_bold"]), Paragraph("<b>78,567</b>", st["right_bold"]), Paragraph("100.0%", st["right_bold"])],
        [Paragraph("ADVERTISING", st["reg"]), Paragraph("275", st["right"]), Paragraph("0.33%", st["right"]), Paragraph("30", st["right"]), Paragraph("0.04%", st["right"])],
        [Paragraph("AUTOMOBILE EXPENSES", st["reg"]), Paragraph("70", st["right"]), Paragraph("0.08%", st["right"]), Paragraph("227", st["right"]), Paragraph("0.29%", st["right"])],
        [Paragraph("BANK CHARGES", st["reg"]), Paragraph("277", st["right"]), Paragraph("0.34%", st["right"]), Paragraph("355", st["right"]), Paragraph("0.45%", st["right"])],
        [Paragraph("LEGAL & COMMISSIONS", st["reg"]), Paragraph("0", st["right"]), Paragraph("0.00%", st["right"]), Paragraph("2,854", st["right"]), Paragraph("3.63%", st["right"])],
        [Paragraph("INSURANCE", st["reg"]), Paragraph("4,292", st["right"]), Paragraph("5.20%", st["right"]), Paragraph("3,783", st["right"]), Paragraph("4.81%", st["right"])],
        [Paragraph("MANAGEMENT FEES (3.56%)", st["bold"]), Paragraph("2,940", st["right_bold"]), Paragraph("3.56%", st["right_bold"]), Paragraph("2,800", st["right_bold"]), Paragraph("3.56%", st["right_bold"])],
        [Paragraph("REPAIRS AND MAINTENANCE", st["reg"]), Paragraph("3,514", st["right"]), Paragraph("4.26%", st["right"]), Paragraph("2,410", st["right"]), Paragraph("3.07%", st["right"])],
        [Paragraph("REAL ESTATE TAXES", st["reg"]), Paragraph("7,820", st["right"]), Paragraph("9.47%", st["right"]), Paragraph("6,950", st["right"]), Paragraph("8.85%", st["right"])],
        [Paragraph("UTILITIES (WATER, GAS, ELECTRIC)", st["reg"]), Paragraph("5,869", st["right"]), Paragraph("7.11%", st["right"]), Paragraph("5,236", st["right"]), Paragraph("6.66%", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL OPERATING EXPENSES</b>", st["bold"]), Paragraph("<b>25,057</b>", st["right_bold"]), Paragraph("<b>30.36%</b>", st["right_bold"]), Paragraph("<b>24,645</b>", st["right_bold"]), Paragraph("<b>31.37%</b>", st["right_bold"])],
    ]

    t_exp = Table(exp_data, colWidths=[210, 80, 75, 80, 75])
    t_exp.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.black),
        ('LINEBELOW', (0, 10), (-1, 10), 0.5, colors.black),
        ('LINEBELOW', (0, 12), (-1, 12), 1.5, colors.black),
        ('LINEABOVE', (0, 12), (-1, 12), 0.5, colors.black),
    ]))
    el.append(t_exp)

    doc.build(el)
    print(f"✅ Generated Complete Ellis Apartments CFO Replica PDF: {OUTPUT_PDF}")
    return "Ellis Apartments Replica Complete"

if __name__ == "__main__":
    build_pdf()
