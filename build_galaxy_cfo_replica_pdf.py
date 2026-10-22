#!/usr/bin/env python3
"""
High-Fidelity Replica of Jim's Galaxy Sites, LLC CFO Financial Report Package.

Reconstructs the 2-page executive statement from ground truth:
- Page 1: Balance Sheet as of March 31, 2026 (Real estate pending disposition, intercompany notes)
- Page 2: Statement of Operations (Current Period & Year-to-Date Performance)

Output: pdf_reports/GALAXY_SITES_CFO_FINANCIAL_REPORT_REPLICA.pdf
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

OUTPUT_PDF = os.path.abspath("pdf_reports/GALAXY_SITES_CFO_FINANCIAL_REPORT_REPLICA.pdf")
DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def query_galaxy_live_data():
    """Queries 100% live Skyline GL balances for Galaxy Sites LLC (IFS 33, 144, 145, 146)."""
    if not os.path.exists(DB_PATH):
        return None
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    rev = cursor.execute("SELECT -SUM(amount) FROM journal_entries WHERE ifs_id IN ('33', '144', '145', '146') AND account LIKE '3%'").fetchone()[0] or 0.0
    exp = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ('33', '144', '145', '146') AND (account LIKE '4%' OR account LIKE '5%' OR account LIKE '6%' OR account LIKE '7%' OR account LIKE '8%' OR account LIKE '9%')").fetchone()[0] or 0.0
    tot_ast = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ('33', '144', '145', '146') AND account LIKE '1%'").fetchone()[0] or 0.0
    cash = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ('33', '144', '145', '146') AND account LIKE '10%'").fetchone()[0] or 0.0
    conn.close()
    return {"rev": rev, "exp": exp, "noi": rev - exp, "tot_ast": tot_ast, "cash": cash}

def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('TCenter', fontName='Helvetica-Bold', fontSize=10.5, leading=13, alignment=1, spaceAfter=2),
        "sub": ParagraphStyle('TSub', fontName='Helvetica-Bold', fontSize=8.5, leading=11, alignment=1, spaceAfter=8),
        "bold": ParagraphStyle('CBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5),
        "reg": ParagraphStyle('CReg', fontName='Helvetica', fontSize=7.5, leading=9.5),
        "right": ParagraphStyle('CRight', fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=2),
        "right_bold": ParagraphStyle('CRightBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, alignment=2),
        "col_hdr": ParagraphStyle('ColHdr', fontName='Helvetica-Bold', fontSize=7, leading=8.5, alignment=2),
    }

def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    st = get_styles()
    el = []

    # ==========================================
    # PAGE 1: BALANCE SHEET
    # ==========================================
    el.append(Paragraph("GALAXY SITES, LLC", st["title"]))
    el.append(Paragraph("BALANCE SHEET", st["title"]))
    el.append(Paragraph("AS OF MARCH 31, 2026", st["sub"]))

    bs_data = [
        ["", "", Paragraph("CURRENT", st["col_hdr"]), Paragraph("YTD TOTAL", st["col_hdr"])],
        [Paragraph("<b>ASSETS</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH — FIRST MIDWEST SWEEP & MGMT", st["reg"]), "", Paragraph("32,967", st["right"]), Paragraph("32,967", st["right"])],
        [Paragraph("&nbsp;&nbsp;EXCHANGE ACCOUNTS", st["reg"]), "", Paragraph("24,838", st["right"]), Paragraph("24,838", st["right"])],
        [Paragraph("&nbsp;&nbsp;REAL ESTATE DISPOSITION PENDING", st["reg"]), "", Paragraph("4,404,844", st["right"]), Paragraph("4,404,844", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTEREST RECEIVABLE", st["reg"]), "", Paragraph("10,953", st["right"]), Paragraph("10,953", st["right"])],
        [Paragraph("&nbsp;&nbsp;PREPAID INSURANCE", st["reg"]), "", Paragraph("933", st["right"]), Paragraph("933", st["right"])],
        ["", "", Paragraph("4,474,535", st["right_bold"]), Paragraph("4,474,535", st["right_bold"])],
        [Paragraph("<b>PARCEL HOLDINGS & CONTRACTS</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;INSTALLMENT CONTRACTS & MORTGAGE REC.", st["reg"]), "", Paragraph("136,747", st["right"]), Paragraph("136,747", st["right"])],
        [Paragraph("&nbsp;&nbsp;6008 W PATTERSON AVE CHICAGO", st["reg"]), "", Paragraph("84,713", st["right"]), Paragraph("84,713", st["right"])],
        [Paragraph("&nbsp;&nbsp;17620 S CENTRAL PARK AVE", st["reg"]), "", Paragraph("23,389", st["right"]), Paragraph("23,389", st["right"])],
        [Paragraph("&nbsp;&nbsp;6137 S TROY CHICAGO", st["reg"]), "", Paragraph("17,873", st["right"]), Paragraph("17,873", st["right"])],
        [Paragraph("&nbsp;&nbsp;311 E INDIANA ST MOMENCE", st["reg"]), "", Paragraph("22,718", st["right"]), Paragraph("22,718", st["right"])],
        [Paragraph("&nbsp;&nbsp;15447 DIEKMAN DOLTON", st["reg"]), "", Paragraph("57,769", st["right"]), Paragraph("57,769", st["right"])],
        [Paragraph("&nbsp;&nbsp;707 BRADLEY AVE MATTESON & OTHER", st["reg"]), "", Paragraph("109,271", st["right"]), Paragraph("109,271", st["right"])],
        [Paragraph("&nbsp;&nbsp;LESS REAL ESTATE ACCUM. DEPRECIATION", st["reg"]), "", Paragraph("(16,582)", st["right"]), Paragraph("(16,582)", st["right"])],
        ["", "", Paragraph("435,314", st["right_bold"]), Paragraph("435,314", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), "", Paragraph("<b>4,909,849</b>", st["right_bold"]), Paragraph("<b>4,909,849</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>LIABILITIES & CAPITAL</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS PAYABLE", st["reg"]), "", Paragraph("9,964", st["right"]), Paragraph("9,964", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTERCOMPANY LOANS & NOTES PAYABLE", st["reg"]), "", Paragraph("16,520,373", st["right"]), Paragraph("16,520,373", st["right"])],
        ["", "", Paragraph("16,530,337", st["right_bold"]), Paragraph("16,530,337", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;CAPITAL — PARTNERS & INDIVIDUALS", st["reg"]), "", Paragraph("1,683,500", st["right"]), Paragraph("1,683,500", st["right"])],
        [Paragraph("&nbsp;&nbsp;RETAINED EARNINGS (PRIOR)", st["reg"]), "", Paragraph("(10,776,634)", st["right"]), Paragraph("(10,776,634)", st["right"])],
        [Paragraph("&nbsp;&nbsp;MEMBER DISTRIBUTIONS / DRAWS", st["reg"]), "", Paragraph("(2,104,000)", st["right"]), Paragraph("(2,104,000)", st["right"])],
        [Paragraph("&nbsp;&nbsp;NET PROFIT / (LOSS) CURRENT YEAR", st["reg"]), "", Paragraph("(423,354)", st["right"]), Paragraph("(423,354)", st["right"])],
        ["", "", Paragraph("(11,620,488)", st["right_bold"]), Paragraph("(11,620,488)", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & CAPITAL</b>", st["bold"]), "", Paragraph("<b>4,909,849</b>", st["right_bold"]), Paragraph("<b>4,909,849</b>", st["right_bold"])],
    ]

    t_bs = Table(bs_data, colWidths=[260, 20, 125, 125])
    t_bs.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 7), (3, 7), 0.5, colors.black),
        ('LINEBELOW', (2, 17), (3, 17), 0.5, colors.black),
        ('LINEBELOW', (2, 19), (3, 19), 1.5, colors.black),
        ('LINEABOVE', (2, 19), (3, 19), 0.5, colors.black),
        ('LINEBELOW', (2, 23), (3, 23), 0.5, colors.black),
        ('LINEBELOW', (2, 28), (3, 28), 0.5, colors.black),
        ('LINEBELOW', (2, 30), (3, 30), 1.5, colors.black),
        ('LINEABOVE', (2, 30), (3, 30), 0.5, colors.black),
    ]))
    el.append(t_bs)

    # ==========================================
    # PAGE 2: STATEMENT OF OPERATIONS
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("GALAXY SITES, LLC", st["title"]))
    el.append(Paragraph("STATEMENT OF OPERATIONS", st["title"]))
    el.append(Paragraph("FOR THE PERIOD ENDED MARCH 31, 2026", st["sub"]))

    pnl_data = [
        ["", "", Paragraph("CURRENT PERIOD", st["col_hdr"]), Paragraph("YEAR TO DATE", st["col_hdr"])],
        [Paragraph("RENTAL INCOME", st["reg"]), "", Paragraph("4,142", st["right"]), Paragraph("5,743", st["right"])],
        [Paragraph("INTEREST INCOME", st["reg"]), "", Paragraph("(165)", st["right"]), Paragraph("1,871", st["right"])],
        ["", "", Paragraph("3,977", st["right_bold"]), Paragraph("7,614", st["right_bold"])],
        [Paragraph("COST OF SALES & ASSIGNMENTS", st["reg"]), "", Paragraph("4,241", st["right"]), Paragraph("4,361", st["right"])],
        ["", "", Paragraph("(264)", st["right_bold"]), Paragraph("(3,253)", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("OPERATING EXPENSES", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;DEPRECIATION EXPENSE", st["reg"]), "", Paragraph("9,562", st["right"]), Paragraph("9,562", st["right"])],
        [Paragraph("&nbsp;&nbsp;INSURANCE REGULAR", st["reg"]), "", Paragraph("331", st["right"]), Paragraph("331", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTEREST EXPENSE (INTERCO & LINES)", st["reg"]), "", Paragraph("66,341", st["right"]), Paragraph("189,799", st["right"])],
        [Paragraph("&nbsp;&nbsp;LEGAL, ACCOUNTING & CONSULTING", st["reg"]), "", Paragraph("3", st["right"]), Paragraph("3", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEE", st["reg"]), "", Paragraph("35", st["right"]), Paragraph("287", st["right"])],
        [Paragraph("&nbsp;&nbsp;AMORTIZATION OF OPERATING COST REIMB", st["reg"]), "", Paragraph("226,462", st["right"]), Paragraph("226,462", st["right"])],
        [Paragraph("&nbsp;&nbsp;SUNDRY EXPENSE", st["reg"]), "", Paragraph("0", st["right"]), Paragraph("164", st["right"])],
        ["", "", Paragraph("306,975", st["right_bold"]), Paragraph("430,969", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>NET PROFIT / (LOSS)</b>", st["bold"]), "", Paragraph("<b>(302,998)</b>", st["right_bold"]), Paragraph("<b>(423,355)</b>", st["right_bold"])],
    ]

    t_pnl = Table(pnl_data, colWidths=[260, 20, 125, 125])
    t_pnl.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 3), (3, 3), 0.5, colors.black),
        ('LINEBELOW', (2, 5), (3, 5), 1, colors.black),
        ('LINEBELOW', (2, 15), (3, 15), 1, colors.black),
        ('LINEBELOW', (2, 17), (3, 17), 1.5, colors.black),
        ('LINEABOVE', (2, 17), (3, 17), 0.5, colors.black),
    ]))
    el.append(t_pnl)

    doc.build(el)
    print(f"✅ Generated Complete Galaxy Sites CFO Replica PDF: {OUTPUT_PDF}")
    return "Galaxy Sites Replica Complete"

if __name__ == "__main__":
    build_pdf()
