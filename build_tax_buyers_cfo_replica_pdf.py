#!/usr/bin/env python3
"""
High-Fidelity Replica of Jim's Consolidated Tax Buyers CFO Financial Report Package.

Reconstructs the executive multi-company consolidating package from:
source_documents/COMBINED TAX BUYERS Q1 2026 Consol Financials.pdf:
- Page 1: Consolidating Balance Sheet (Interstate, Central Buyer, Diamond Quest, Union Tax, Combined)
- Page 2: Consolidating Income Statement (Revenues, OPEX, NOI, Debt Interest, Net Income)
- Page 3: 2026 vs. 2025 Comparative Income Statement (Q1 Three Months Ended 3/31/2026 vs 3/31/2025 with Variance)
- Page 4: Bank Loan Portfolio & Bank Covenants (Old National, Byline, First Bank Chicago DSCR 1.81x)

Output: pdf_reports/TAX_BUYERS_CFO_CONSOLIDATING_STATEMENTS_REPLICA.pdf
"""

import os
import sys
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

OUTPUT_PDF = os.path.abspath("pdf_reports/TAX_BUYERS_CFO_CONSOLIDATING_STATEMENTS_REPLICA.pdf")
DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def query_tax_buyers_live_data():
    """Queries 100% live Skyline GL balances across Tax Buyer entities (150, 160, 180, 190)."""
    if not os.path.exists(DB_PATH):
        return None
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    def get_e(ifs):
        rev = cursor.execute("SELECT -SUM(amount) FROM journal_entries WHERE ifs_id=? AND account LIKE '3%'", (ifs,)).fetchone()[0] or 0.0
        exp = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id=? AND (account LIKE '4%' OR account LIKE '5%' OR account LIKE '6%' OR account LIKE '7%' OR account LIKE '8%' OR account LIKE '9%')", (ifs,)).fetchone()[0] or 0.0
        ast = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id=? AND account LIKE '1%'", (ifs,)).fetchone()[0] or 0.0
        cash = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id=? AND account LIKE '10%'", (ifs,)).fetchone()[0] or 0.0
        return {"rev": rev, "exp": exp, "noi": rev - exp, "ast": ast, "cash": cash}

    res = {
        "150": get_e('150'),
        "160": get_e('160'),
        "180": get_e('180'),
        "190": get_e('190'),
    }
    conn.close()
    return res

def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('TCenter', fontName='Helvetica-Bold', fontSize=10.5, leading=13, alignment=1, spaceAfter=2),
        "sub": ParagraphStyle('TSub', fontName='Helvetica-Bold', fontSize=8.5, leading=11, alignment=1, spaceAfter=8),
        "note": ParagraphStyle('TNote', fontName='Helvetica-Oblique', fontSize=7, leading=9, alignment=1, spaceAfter=6),
        "bold": ParagraphStyle('CBold', fontName='Helvetica-Bold', fontSize=6.8, leading=8.5),
        "reg": ParagraphStyle('CReg', fontName='Helvetica', fontSize=6.8, leading=8.5),
        "right": ParagraphStyle('CRight', fontName='Helvetica', fontSize=6.8, leading=8.5, alignment=2),
        "right_bold": ParagraphStyle('CRightBold', fontName='Helvetica-Bold', fontSize=6.8, leading=8.5, alignment=2),
        "col_hdr": ParagraphStyle('ColHdr', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=2),
    }

def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=landscape(letter), leftMargin=36, rightMargin=36, topMargin=28, bottomMargin=28)
    st = get_styles()
    el = []

    # ==========================================
    # PAGE 1: CONSOLIDATING BALANCE SHEET
    # ==========================================
    el.append(Paragraph("CONSOLIDATED TAX BUYERS", st["title"]))
    el.append(Paragraph("CONSOLIDATING BALANCE SHEET", st["title"]))
    el.append(Paragraph("AS OF MARCH 31, 2026", st["sub"]))
    el.append(Paragraph("Prepared by: James A. Adamo, Controller", st["note"]))

    bs_data = [
        [
            Paragraph("<b>ASSETS & LIABILITIES</b>", st["bold"]),
            Paragraph("INTERSTATE<br/>FUNDING (150)", st["col_hdr"]),
            Paragraph("CENTRAL<br/>BUYER (160)", st["col_hdr"]),
            Paragraph("DIAMOND<br/>QUEST (180)", st["col_hdr"]),
            Paragraph("UNION TAX<br/>INVESTORS (190)", st["col_hdr"]),
            Paragraph("COMBINED<br/>TOTAL", st["col_hdr"]),
        ],
        [Paragraph("CURRENT ASSETS", st["bold"]), "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH", st["reg"]), Paragraph("294,338", st["right"]), Paragraph("236,371", st["right"]), Paragraph("229,211", st["right"]), Paragraph("94,545", st["right"]), Paragraph("854,465", st["right"])],
        [Paragraph("&nbsp;&nbsp;CERTIFICATES OF PURCHASE", st["reg"]), Paragraph("14,558,289", st["right"]), Paragraph("17,198,505", st["right"]), Paragraph("1,796,296", st["right"]), Paragraph("644,573", st["right"]), Paragraph("34,197,662", st["right"])],
        [Paragraph("&nbsp;&nbsp;NOTES RECEIVABLE FROM RELATED PARTIES", st["reg"]), Paragraph("2,197,000", st["right"]), Paragraph("1,764,480", st["right"]), Paragraph("872,000", st["right"]), Paragraph("676,000", st["right"]), Paragraph("5,509,480", st["right"])],
        [Paragraph("&nbsp;&nbsp;RECEIVABLE FROM SHAREHOLDERS", st["reg"]), Paragraph("50,023", st["right"]), Paragraph("3,589", st["right"]), Paragraph("149", st["right"]), Paragraph("0", st["right"]), Paragraph("53,761", st["right"])],
        [Paragraph("&nbsp;&nbsp;INCOME TAX RECEIVABLE", st["reg"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("7,570", st["right"]), Paragraph("7,570", st["right"])],
        ["", Paragraph("17,099,650", st["right_bold"]), Paragraph("19,202,944", st["right_bold"]), Paragraph("2,897,656", st["right_bold"]), Paragraph("1,422,688", st["right_bold"]), Paragraph("40,622,937", st["right_bold"])],
        ["", "", "", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), Paragraph("<b>17,099,650</b>", st["right_bold"]), Paragraph("<b>19,202,944</b>", st["right_bold"]), Paragraph("<b>2,897,656</b>", st["right_bold"]), Paragraph("<b>1,422,688</b>", st["right_bold"]), Paragraph("<b>40,622,937</b>", st["right_bold"])],
        ["", "", "", "", "", ""],
        [Paragraph("CURRENT LIABILITIES", st["bold"]), "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS PAYABLE & ACCRUED EXPENSES", st["reg"]), Paragraph("92,108", st["right"]), Paragraph("31,643", st["right"]), Paragraph("8,675", st["right"]), Paragraph("5,888", st["right"]), Paragraph("138,314", st["right"])],
        [Paragraph("&nbsp;&nbsp;BANK LOANS PAYABLE (CURRENT PORTION)", st["reg"]), Paragraph("156,494", st["right"]), Paragraph("104,188", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("260,682", st["right"])],
        [Paragraph("&nbsp;&nbsp;NOTES PAYABLE TO RELATED PARTIES", st["reg"]), Paragraph("16,367", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("16,367", st["right"])],
        ["", Paragraph("264,969", st["right_bold"]), Paragraph("135,831", st["right_bold"]), Paragraph("8,675", st["right_bold"]), Paragraph("5,888", st["right_bold"]), Paragraph("415,363", st["right_bold"])],
        ["", "", "", "", "", ""],
        [Paragraph("LONG-TERM DEBT (BYLINE / FIRST BANK / OLD NATL)", st["bold"]), Paragraph("10,902,672", st["right"]), Paragraph("16,790,315", st["right"]), Paragraph("1,901,593", st["right"]), Paragraph("629,734", st["right"]), Paragraph("30,224,314", st["right"])],
        [Paragraph("STOCKHOLDERS EQUITY / CAPITAL", st["bold"]), Paragraph("5,932,009", st["right"]), Paragraph("2,276,798", st["right"]), Paragraph("987,388", st["right"]), Paragraph("787,066", st["right"]), Paragraph("9,983,260", st["right"])],
        ["", "", "", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & EQUITY</b>", st["bold"]), Paragraph("<b>17,099,650</b>", st["right_bold"]), Paragraph("<b>19,202,944</b>", st["right_bold"]), Paragraph("<b>2,897,656</b>", st["right_bold"]), Paragraph("<b>1,422,688</b>", st["right_bold"]), Paragraph("<b>40,622,937</b>", st["right_bold"])],
    ]

    t_bs = Table(bs_data, colWidths=[240, 95, 95, 95, 95, 95])
    t_bs.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 7), (-1, 7), 0.5, colors.black),
        ('LINEBELOW', (1, 9), (-1, 9), 1.5, colors.black),
        ('LINEABOVE', (1, 9), (-1, 9), 0.5, colors.black),
        ('LINEBELOW', (1, 15), (-1, 15), 0.5, colors.black),
        ('LINEBELOW', (1, 20), (-1, 20), 1.5, colors.black),
        ('LINEABOVE', (1, 20), (-1, 20), 0.5, colors.black),
    ]))
    el.append(t_bs)

    # ==========================================
    # PAGE 2: CONSOLIDATING INCOME STATEMENT
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("CONSOLIDATED TAX BUYERS", st["title"]))
    el.append(Paragraph("CONSOLIDATING INCOME STATEMENT", st["title"]))
    el.append(Paragraph("THREE MONTHS ENDED MARCH 31, 2026", st["sub"]))
    el.append(Paragraph("Prepared by: James A. Adamo, Controller", st["note"]))

    pnl_data = [
        [
            Paragraph("<b>REVENUES & EXPENSES</b>", st["bold"]),
            Paragraph("INTERSTATE<br/>FUNDING (150)", st["col_hdr"]),
            Paragraph("CENTRAL<br/>BUYER (160)", st["col_hdr"]),
            Paragraph("DIAMOND<br/>QUEST (180)", st["col_hdr"]),
            Paragraph("UNION TAX<br/>INVESTORS (190)", st["col_hdr"]),
            Paragraph("COMBINED<br/>TOTAL", st["col_hdr"]),
        ],
        [Paragraph("CERTIFICATES OF PURCHASE REVENUE", st["bold"]), Paragraph("487,448", st["right"]), Paragraph("670,991", st["right"]), Paragraph("33,111", st["right"]), Paragraph("34,734", st["right"]), Paragraph("1,226,285", st["right"])],
        [Paragraph("&nbsp;&nbsp;Operating Cost Reimbursement", st["reg"]), Paragraph("110,550", st["right"]), Paragraph("181,179", st["right"]), Paragraph("3,663", st["right"]), Paragraph("11,040", st["right"]), Paragraph("306,432", st["right"])],
        [Paragraph("&nbsp;&nbsp;Certificate Interest (Accrued & Redeemed)", st["reg"]), Paragraph("376,898", st["right"]), Paragraph("489,812", st["right"]), Paragraph("29,448", st["right"]), Paragraph("23,694", st["right"]), Paragraph("919,853", st["right"])],
        ["", "", "", "", "", ""],
        [Paragraph("OPERATING EXPENSES", st["bold"]), Paragraph("134,815", st["right"]), Paragraph("153,922", st["right"]), Paragraph("8,706", st["right"]), Paragraph("18,822", st["right"]), Paragraph("316,265", st["right"])],
        [Paragraph("&nbsp;&nbsp;Management Fees", st["reg"]), Paragraph("92,691", st["right"]), Paragraph("114,723", st["right"]), Paragraph("2,523", st["right"]), Paragraph("8,373", st["right"]), Paragraph("218,310", st["right"])],
        [Paragraph("&nbsp;&nbsp;Loan & Line Fees", st["reg"]), Paragraph("250", st["right"]), Paragraph("250", st["right"]), Paragraph("250", st["right"]), Paragraph("250", st["right"]), Paragraph("1,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;Legal, Accounting & Bank Charges", st["reg"]), Paragraph("41,874", st["right"]), Paragraph("38,949", st["right"]), Paragraph("5,933", st["right"]), Paragraph("10,199", st["right"]), Paragraph("96,955", st["right"])],
        ["", "", "", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME</b>", st["bold"]), Paragraph("<b>352,633</b>", st["right_bold"]), Paragraph("<b>517,069</b>", st["right_bold"]), Paragraph("<b>24,405</b>", st["right_bold"]), Paragraph("<b>15,912</b>", st["right_bold"]), Paragraph("<b>910,020</b>", st["right_bold"])],
        ["", "", "", "", "", ""],
        [Paragraph("OTHER INCOME & (EXPENSE)", st["bold"]), "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;INTEREST INCOME", st["reg"]), Paragraph("24,813", st["right"]), Paragraph("23,687", st["right"]), Paragraph("7,208", st["right"]), Paragraph("6,081", st["right"]), Paragraph("61,789", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTEREST EXPENSE (BANK FACILITIES)", st["reg"]), Paragraph("(181,770)", st["right"]), Paragraph("(281,424)", st["right"]), Paragraph("(29,881)", st["right"]), Paragraph("(10,424)", st["right"]), Paragraph("(503,499)", st["right"])],
        ["", Paragraph("(156,957)", st["right_bold"]), Paragraph("(257,737)", st["right_bold"]), Paragraph("(22,673)", st["right_bold"]), Paragraph("(4,343)", st["right_bold"]), Paragraph("(441,710)", st["right_bold"])],
        ["", "", "", "", "", ""],
        [Paragraph("<b>NET INCOME</b>", st["bold"]), Paragraph("<b>195,676</b>", st["right_bold"]), Paragraph("<b>259,332</b>", st["right_bold"]), Paragraph("<b>1,732</b>", st["right_bold"]), Paragraph("<b>11,569</b>", st["right_bold"]), Paragraph("<b>468,309</b>", st["right_bold"])],
    ]

    t_pnl = Table(pnl_data, colWidths=[240, 95, 95, 95, 95, 95])
    t_pnl.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 1), (-1, 1), 0.5, colors.black),
        ('LINEBELOW', (1, 5), (-1, 5), 0.5, colors.black),
        ('LINEBELOW', (1, 10), (-1, 10), 1, colors.black),
        ('LINEBELOW', (1, 15), (-1, 15), 0.5, colors.black),
        ('LINEBELOW', (1, 17), (-1, 17), 1.5, colors.black),
        ('LINEABOVE', (1, 17), (-1, 17), 0.5, colors.black),
    ]))
    el.append(t_pnl)

    # ==========================================
    # PAGE 3: 2026 vs 2025 COMPARATIVE P&L
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("CONSOLIDATED TAX BUYERS", st["title"]))
    el.append(Paragraph("COMPARATIVE INCOME STATEMENT (2026 vs. 2025)", st["title"]))
    el.append(Paragraph("THREE MONTHS ENDED MARCH 31, 2026 vs. MARCH 31, 2025", st["sub"]))

    comp_data = [
        [
            Paragraph("<b>Category</b>", st["bold"]),
            Paragraph("3/31/2026<br/>COMBINED", st["col_hdr"]),
            Paragraph("3/31/2025<br/>COMBINED", st["col_hdr"]),
            Paragraph("DOLLAR<br/>VARIANCE", st["col_hdr"]),
            Paragraph("TTM 12 MO<br/>3/31/2026", st["col_hdr"]),
            Paragraph("TTM 12 MO<br/>3/31/2025", st["col_hdr"]),
        ],
        [Paragraph("CERTIFICATES OF PURCHASE REVENUE", st["bold"]), Paragraph("1,226,285", st["right"]), Paragraph("1,265,091", st["right"]), Paragraph("(38,806)", st["right"]), Paragraph("4,849,725", st["right"]), Paragraph("3,615,311", st["right"])],
        [Paragraph("OPERATING EXPENSES", st["bold"]), Paragraph("316,265", st["right"]), Paragraph("375,286", st["right"]), Paragraph("59,021", st["right"]), Paragraph("1,174,318", st["right"]), Paragraph("1,022,831", st["right"])],
        ["", "", "", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME</b>", st["bold"]), Paragraph("<b>910,020</b>", st["right_bold"]), Paragraph("<b>889,805</b>", st["right_bold"]), Paragraph("<b>20,215</b>", st["right_bold"]), Paragraph("<b>3,675,407</b>", st["right_bold"]), Paragraph("<b>2,592,480</b>", st["right_bold"])],
        ["", "", "", "", "", ""],
        [Paragraph("INTEREST INCOME", st["reg"]), Paragraph("61,789", st["right"]), Paragraph("25,126", st["right"]), Paragraph("36,663", st["right"]), Paragraph("176,747", st["right"]), Paragraph("61,608", st["right"])],
        [Paragraph("INTEREST EXPENSE", st["reg"]), Paragraph("(503,499)", st["right"]), Paragraph("(530,772)", st["right"]), Paragraph("27,273", st["right"]), Paragraph("(1,972,268)", st["right"]), Paragraph("(1,430,082)", st["right"])],
        ["", "", "", "", "", ""],
        [Paragraph("<b>NET INCOME</b>", st["bold"]), Paragraph("<b>468,309</b>", st["right_bold"]), Paragraph("<b>384,159</b>", st["right_bold"]), Paragraph("<b>84,151</b>", st["right_bold"]), Paragraph("<b>1,879,886</b>", st["right_bold"]), Paragraph("<b>1,224,006</b>", st["right_bold"])],
        ["", "", "", "", "", ""],
        [Paragraph("DISTRIBUTION TO SHAREHOLDERS", st["reg"]), Paragraph("(250,000)", st["right"]), Paragraph("(150,000)", st["right"]), Paragraph("(100,000)", st["right"]), Paragraph("(1,796,411)", st["right"]), Paragraph("(947,442)", st["right"])],
        [Paragraph("RETAINED EARNINGS — BEGINNING", st["reg"]), Paragraph("9,764,951", st["right"]), Paragraph("9,400,994", st["right"]), Paragraph("363,957", st["right"]), Paragraph("9,912,153", st["right"]), Paragraph("9,635,589", st["right"])],
        [Paragraph("<b>RETAINED EARNINGS — ENDING</b>", st["bold"]), Paragraph("<b>9,983,260</b>", st["right_bold"]), Paragraph("<b>9,635,153</b>", st["right_bold"]), Paragraph("<b>348,107</b>", st["right_bold"]), Paragraph("<b>9,995,628</b>", st["right_bold"]), Paragraph("<b>9,912,153</b>", st["right_bold"])],
    ]

    t_comp = Table(comp_data, colWidths=[240, 95, 95, 95, 95, 95])
    t_comp.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 2), (-1, 2), 0.5, colors.black),
        ('LINEBELOW', (1, 4), (-1, 4), 1, colors.black),
        ('LINEBELOW', (1, 7), (-1, 7), 0.5, colors.black),
        ('LINEBELOW', (1, 9), (-1, 9), 1.5, colors.black),
        ('LINEABOVE', (1, 9), (-1, 9), 0.5, colors.black),
        ('LINEBELOW', (1, 13), (-1, 13), 1.5, colors.black),
    ]))
    el.append(t_comp)

    # ==========================================
    # PAGE 4: BANK COVENANTS & DEBT PORTFOLIO
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("CONSOLIDATED TAX BUYERS", st["title"]))
    el.append(Paragraph("BANK COVENANT COMPLIANCE & LOAN SCHEDULE", st["title"]))
    el.append(Paragraph("AS OF MARCH 31, 2026", st["sub"]))
    el.append(Paragraph("Certified by: James A. Adamo, Controller, Jennings Realty Inc.", st["note"]))

    cov_data = [
        [Paragraph("<b>Covenant / Bank Metric</b>", st["bold"]), Paragraph("Actual (3/31/26)", st["col_hdr"]), Paragraph("Required Ratio", st["col_hdr"]), Paragraph("Status", st["col_hdr"]), Paragraph("Lender / Credit Line", st["col_hdr"])],
        [Paragraph("Debt Service Coverage Ratio (Section 8.4D)", st["reg"]), Paragraph("1.81x", st["right_bold"]), Paragraph("1.00x", st["right"]), Paragraph("IN COMPLIANCE (YES)", st["right_bold"]), Paragraph("Byline Bank ($17.0M)", st["reg"])],
        [Paragraph("Tangible Net Worth (Section 6.3)", st["reg"]), Paragraph("$9,938,298", st["right_bold"]), Paragraph("$8,000,000", st["right"]), Paragraph("IN COMPLIANCE (YES)", st["right_bold"]), Paragraph("First Bank Chicago ($15.0M)", st["reg"])],
        [Paragraph("Affiliate Transactions / Loans Limit", st["reg"]), Paragraph("$5,509,480", st["right_bold"]), Paragraph("< $6,000,000", st["right"]), Paragraph("IN COMPLIANCE (YES)", st["right_bold"]), Paragraph("Byline Bank / First Bank", st["reg"])],
        ["", "", "", "", ""],
        [Paragraph("<b>BANK LOANS PAYABLE BY LENDER</b>", st["bold"]), Paragraph("Interstate (150)", st["col_hdr"]), Paragraph("Central (160)", st["col_hdr"]), Paragraph("Diamond & Union", st["col_hdr"]), Paragraph("Combined Debt", st["col_hdr"])],
        [Paragraph("&nbsp;&nbsp;Byline Bank (Maturity 5/19/2028)", st["reg"]), Paragraph("3,746,365", st["right"]), Paragraph("6,198,420", st["right"]), Paragraph("1,250,000", st["right"]), Paragraph("11,194,785", st["right"])],
        [Paragraph("&nbsp;&nbsp;First Bank Chicago (Maturity 7/1/2027)", st["reg"]), Paragraph("885,479", st["right"]), Paragraph("4,321,067", st["right"]), Paragraph("750,000", st["right"]), Paragraph("5,956,546", st["right"])],
        [Paragraph("&nbsp;&nbsp;Old National Bank (Maturity 2/28/2029)", st["reg"]), Paragraph("6,270,828", st["right"]), Paragraph("6,270,828", st["right"]), Paragraph("531,327", st["right"]), Paragraph("13,072,983", st["right"])],
        ["", Paragraph("10,902,672", st["right_bold"]), Paragraph("16,790,315", st["right_bold"]), Paragraph("2,531,327", st["right_bold"]), Paragraph("30,224,314", st["right_bold"])],
    ]

    t_cov = Table(cov_data, colWidths=[240, 115, 115, 125, 120])
    t_cov.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 3), (-1, 3), 1, colors.black),
        ('LINEBELOW', (0, 4), (-1, 4), 1, colors.black),
        ('LINEBELOW', (1, 8), (-1, 8), 0.5, colors.black),
        ('LINEBELOW', (1, 9), (-1, 9), 1.5, colors.black),
        ('LINEABOVE', (1, 9), (-1, 9), 0.5, colors.black),
    ]))
    el.append(t_cov)

    doc.build(el)
    print(f"✅ Generated Complete Tax Buyers CFO Replica PDF: {OUTPUT_PDF}")
    return "Tax Buyers Consolidating Replica Complete"

if __name__ == "__main__":
    build_pdf()
