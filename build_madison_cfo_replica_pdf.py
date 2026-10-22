#!/usr/bin/env python3
"""
High-Fidelity Replica of Jim's Madison RV Resort & Jet Sites B (Golf Course) CFO Report Package.

Reconstructs all 3 pages from ground truth (MADISON and JETSITESB FINANCIALSMARCH2026.pdf):
- Page 1: 4-Column Consolidating Balance Sheet (Resort & Golf Combined, Eliminations, RV Resort, Golf Course)
- Page 2: Multi-Department P&L (RV Resort, Golf Operations, Food & Beverage)
- Page 3: Operating Expense Comparative Analysis (% of Revenue by Department)

Output: pdf_reports/MADISON_CFO_FINANCIAL_REPORT_REPLICA.pdf
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

OUTPUT_PDF = os.path.abspath("pdf_reports/MADISON_CFO_FINANCIAL_REPORT_REPLICA.pdf")
DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def query_madison_live_data():
    """Queries 100% live Skyline GL balances for Madison RV Resort & Golf Course (IFS 143)."""
    if not os.path.exists(DB_PATH):
        return None
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    rev = cursor.execute("SELECT -SUM(amount) FROM journal_entries WHERE ifs_id='143' AND account LIKE '3%'").fetchone()[0] or 0.0
    exp = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='143' AND (account LIKE '4%' OR account LIKE '5%' OR account LIKE '6%' OR account LIKE '7%' OR account LIKE '8%' OR account LIKE '9%')").fetchone()[0] or 0.0
    tot_ast = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='143' AND account LIKE '1%'").fetchone()[0] or 0.0
    conn.close()
    return {"rev": rev, "exp": exp, "noi": rev - exp, "tot_ast": tot_ast}

def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('TCenter', fontName='Helvetica-Bold', fontSize=10.5, leading=13, alignment=1, spaceAfter=2),
        "sub": ParagraphStyle('TSub', fontName='Helvetica-Bold', fontSize=8.5, leading=11, alignment=1, spaceAfter=8),
        "note": ParagraphStyle('TNote', fontName='Helvetica-Oblique', fontSize=7.5, leading=9.5, alignment=1, spaceAfter=6),
        "bold": ParagraphStyle('CBold', fontName='Helvetica-Bold', fontSize=7, leading=9),
        "reg": ParagraphStyle('CReg', fontName='Helvetica', fontSize=7, leading=9),
        "right": ParagraphStyle('CRight', fontName='Helvetica', fontSize=7, leading=9, alignment=2),
        "right_bold": ParagraphStyle('CRightBold', fontName='Helvetica-Bold', fontSize=7, leading=9, alignment=2),
        "micro_hdr": ParagraphStyle('MicroHdr', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, alignment=2),
        "micro_bold": ParagraphStyle('MicroBold', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5),
        "micro_reg": ParagraphStyle('MicroReg', fontName='Helvetica', fontSize=6.2, leading=7.5),
        "micro_right": ParagraphStyle('MicroRight', fontName='Helvetica', fontSize=6.2, leading=7.5, alignment=2),
        "micro_right_bold": ParagraphStyle('MicroRightBold', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, alignment=2),
    }

def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=30, bottomMargin=30)
    st = get_styles()
    el = []

    # ==========================================
    # PAGE 1: 4-COLUMN CONSOLIDATING BALANCE SHEET
    # ==========================================
    el.append(Paragraph("MADISON RV RESORT & JET SITES B (GOLF COURSE)", st["title"]))
    el.append(Paragraph("BALANCE SHEET", st["title"]))
    el.append(Paragraph("MARCH 31, 2026", st["sub"]))
    el.append(Paragraph("ASSETS ACQUIRED OCTOBER 22, 2024", st["note"]))

    bs_data = [
        [
            Paragraph("<b>ASSETS</b>", st["bold"]),
            Paragraph("COMBINED<br/>RESORT & GOLF", st["micro_hdr"]),
            Paragraph("COMBINING<br/>ELIMINATIONS", st["micro_hdr"]),
            Paragraph("RV RESORT", st["micro_hdr"]),
            Paragraph("GOLF COURSE", st["micro_hdr"]),
        ],
        [Paragraph("PROPERTY AND EQUIPMENT", st["bold"]), "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;LAND", st["reg"]), Paragraph("1,152,156", st["right"]), Paragraph("0", st["right"]), Paragraph("488,120", st["right"]), Paragraph("664,036", st["right"])],
        [Paragraph("&nbsp;&nbsp;BUILDING AND IMPROVEMENTS", st["reg"]), Paragraph("967,155", st["right"]), Paragraph("0", st["right"]), Paragraph("967,155", st["right"]), Paragraph("0", st["right"])],
        [Paragraph("&nbsp;&nbsp;GOLF COURSE, GROUNDS & RELATED", st["reg"]), Paragraph("1,457,840", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("1,457,840", st["right"])],
        [Paragraph("&nbsp;&nbsp;SITES AND IMPROVEMENTS", st["reg"]), Paragraph("913,622", st["right"]), Paragraph("0", st["right"]), Paragraph("913,622", st["right"]), Paragraph("0", st["right"])],
        [Paragraph("&nbsp;&nbsp;FURNITURE AND EQUIPMENT", st["reg"]), Paragraph("564,776", st["right"]), Paragraph("0", st["right"]), Paragraph("371,691", st["right"]), Paragraph("193,085", st["right"])],
        [Paragraph("&nbsp;&nbsp;CONCRETE", st["reg"]), Paragraph("903", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("903", st["right"])],
        [Paragraph("&nbsp;&nbsp;VEHICLES", st["reg"]), Paragraph("589,582", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("589,582", st["right"])],
        ["", Paragraph("5,646,034", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("2,740,588", st["right_bold"]), Paragraph("2,905,446", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;LESS ACCUMULATED DEPRECIATION", st["reg"]), Paragraph("(569,634)", st["right"]), Paragraph("0", st["right"]), Paragraph("(251,667)", st["right"]), Paragraph("(317,967)", st["right"])],
        ["", Paragraph("5,076,400", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("2,488,921", st["right_bold"]), Paragraph("2,587,479", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("OTHER ASSETS", st["bold"]), "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH", st["reg"]), Paragraph("318,647", st["right"]), Paragraph("0", st["right"]), Paragraph("115,669", st["right"]), Paragraph("202,978", st["right"])],
        [Paragraph("&nbsp;&nbsp;DUE FROM RELATED PARTY", st["reg"]), Paragraph("248,565", st["right"]), Paragraph("0", st["right"]), Paragraph("248,565", st["right"]), Paragraph("0", st["right"])],
        [Paragraph("&nbsp;&nbsp;INVENTORY FOR RESALE", st["reg"]), Paragraph("15,330", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("15,330", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTERCOMPANY INVESTMENTS", st["reg"]), Paragraph("0", st["right"]), Paragraph("(1,813,435)", st["right"]), Paragraph("1,813,435", st["right"]), Paragraph("0", st["right"])],
        [Paragraph("&nbsp;&nbsp;PREPAID EXPENSES", st["reg"]), Paragraph("52,468", st["right"]), Paragraph("0", st["right"]), Paragraph("44,747", st["right"]), Paragraph("7,721", st["right"])],
        [Paragraph("&nbsp;&nbsp;DEPOSITS", st["reg"]), Paragraph("9,750", st["right"]), Paragraph("0", st["right"]), Paragraph("9,750", st["right"]), Paragraph("0", st["right"])],
        ["", Paragraph("644,760", st["right_bold"]), Paragraph("(1,813,435)", st["right_bold"]), Paragraph("2,232,166", st["right_bold"]), Paragraph("226,029", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), Paragraph("<b>5,721,160</b>", st["right_bold"]), Paragraph("<b>(1,813,435)</b>", st["right_bold"]), Paragraph("<b>4,721,087</b>", st["right_bold"]), Paragraph("<b>2,813,508</b>", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("<b>LIABILITIES AND PARTNERS' CAPITAL</b>", st["bold"]), "", "", "", ""],
        [Paragraph("LIABILITIES", st["bold"]), "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS PAYABLE", st["reg"]), Paragraph("46,811", st["right"]), Paragraph("0", st["right"]), Paragraph("28,436", st["right"]), Paragraph("18,375", st["right"])],
        [Paragraph("&nbsp;&nbsp;ACCRUED EXPENSES", st["reg"]), Paragraph("15,091", st["right"]), Paragraph("0", st["right"]), Paragraph("7,614", st["right"]), Paragraph("7,477", st["right"])],
        [Paragraph("&nbsp;&nbsp;LOAN PAYABLE", st["reg"]), Paragraph("82,923", st["right"]), Paragraph("0", st["right"]), Paragraph("82,923", st["right"]), Paragraph("0", st["right"])],
        [Paragraph("&nbsp;&nbsp;NOTES PAYABLE TO RELATED PARTIES", st["reg"]), Paragraph("1,318,000", st["right"]), Paragraph("0", st["right"]), Paragraph("671,000", st["right"]), Paragraph("647,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;SALES TAXES PAYABLE", st["reg"]), Paragraph("11,327", st["right"]), Paragraph("0", st["right"]), Paragraph("7,784", st["right"]), Paragraph("3,543", st["right"])],
        [Paragraph("&nbsp;&nbsp;DUE TO RELATED PARTY", st["reg"]), Paragraph("247,565", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("247,565", st["right"])],
        ["", Paragraph("1,721,717", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("714,834", st["right_bold"]), Paragraph("1,006,883", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("PARTNERS' CAPITAL — JENNINGS REALTY", st["reg"]), Paragraph("250,000", st["right"]), Paragraph("0", st["right"]), Paragraph("250,000", st["right"]), Paragraph("0", st["right"])],
        [Paragraph("PARTNERS' CAPITAL — JET SITES, LLC", st["reg"]), Paragraph("4,250,000", st["right"]), Paragraph("0", st["right"]), Paragraph("4,250,000", st["right"]), Paragraph("0", st["right"])],
        [Paragraph("PARTNERS' CAPITAL — GOLFRV, LLC", st["reg"]), Paragraph("500,000", st["right"]), Paragraph("0", st["right"]), Paragraph("500,000", st["right"]), Paragraph("0", st["right"])],
        [Paragraph("PARTNERS' CAPITAL — MADISON RV RESORT LLC", st["reg"]), Paragraph("0", st["right"]), Paragraph("(2,487,857)", st["right"]), Paragraph("0", st["right"]), Paragraph("2,487,857", st["right"])],
        [Paragraph("PARTNERS' CAPITAL — BARBARA DESC. TRUST", st["reg"]), Paragraph("1", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("1", st["right"])],
        [Paragraph("RETAINED EARNINGS", st["reg"]), Paragraph("(1,000,558)", st["right"]), Paragraph("674,422", st["right"]), Paragraph("(993,747)", st["right"]), Paragraph("(681,233)", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & CAPITAL</b>", st["bold"]), Paragraph("<b>5,721,160</b>", st["right_bold"]), Paragraph("<b>(1,813,435)</b>", st["right_bold"]), Paragraph("<b>4,721,087</b>", st["right_bold"]), Paragraph("<b>2,813,508</b>", st["right_bold"])],
    ]

    t_bs = Table(bs_data, colWidths=[200, 85, 85, 85, 85])
    t_bs.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 9), (-1, 9), 0.5, colors.black),
        ('LINEBELOW', (1, 11), (-1, 11), 0.5, colors.black),
        ('LINEBELOW', (1, 20), (-1, 20), 0.5, colors.black),
        ('LINEBELOW', (1, 22), (-1, 22), 1.5, colors.black),
        ('LINEABOVE', (1, 22), (-1, 22), 0.5, colors.black),
        ('LINEBELOW', (1, 32), (-1, 32), 0.5, colors.black),
        ('LINEBELOW', (1, 41), (-1, 41), 1.5, colors.black),
        ('LINEABOVE', (1, 41), (-1, 41), 0.5, colors.black),
    ]))
    el.append(t_bs)

    # ==========================================
    # PAGE 2: STATEMENT OF INCOME & RETAINED EARNINGS
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("MADISON RV RESORT & JET SITES B (GOLF COURSE)", st["title"]))
    el.append(Paragraph("STATEMENT OF INCOME AND RETAINED EARNINGS", st["title"]))
    el.append(Paragraph("QUARTER ENDED MARCH 31, 2026", st["sub"]))
    el.append(Paragraph("ASSETS ACQUIRED OCTOBER 22, 2024", st["note"]))

    pnl_data = [
        [
            Paragraph("<b>REVENUE & CATEGORY</b>", st["bold"]),
            Paragraph("3/31/2026<br/>COMBINED", st["micro_hdr"]),
            Paragraph("ELIMINATIONS", st["micro_hdr"]),
            Paragraph("RV RESORT", st["micro_hdr"]),
            Paragraph("GOLF TOTAL", st["micro_hdr"]),
            Paragraph("GOLF OPS", st["micro_hdr"]),
            Paragraph("F&B", st["micro_hdr"]),
        ],
        [Paragraph("RENTAL INCOME", st["micro_reg"]), Paragraph("169,304", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("169,304", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("LAUNDRY INCOME", st["micro_reg"]), Paragraph("470", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("470", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("PROPANE GAS SALES", st["micro_reg"]), Paragraph("2,576", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("2,576", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("GOLF CART RENTAL", st["micro_reg"]), Paragraph("3,396", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("3,396", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("STORE TAXABLE INCOME", st["micro_reg"]), Paragraph("2,449", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("2,449", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("ELECTRIC INCOME", st["micro_reg"]), Paragraph("9,414", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("9,414", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("GREEN FEES", st["micro_reg"]), Paragraph("36,610", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("36,610", st["micro_right"]), Paragraph("36,610", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("RV GREEN FEES", st["micro_reg"]), Paragraph("52,541", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("52,541", st["micro_right"]), Paragraph("52,541", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("BEER SALES", st["micro_reg"]), Paragraph("18,761", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("18,761", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("18,761", st["micro_right"])],
        [Paragraph("BEVERAGE SALES", st["micro_reg"]), Paragraph("2,879", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("2,879", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("2,879", st["micro_right"])],
        [Paragraph("SNACK SALES", st["micro_reg"]), Paragraph("2,509", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("2,509", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("2,509", st["micro_right"])],
        [Paragraph("LIQUOR SALES", st["micro_reg"]), Paragraph("15,668", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("15,668", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("15,668", st["micro_right"])],
        [Paragraph("ICE SALES", st["micro_reg"]), Paragraph("288", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("288", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("288", st["micro_right"])],
        [Paragraph("MEMBER DUES", st["micro_reg"]), Paragraph("6,567", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("6,567", st["micro_right"]), Paragraph("6,567", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("TOURNAMENT FEES", st["micro_reg"]), Paragraph("8,475", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("8,475", st["micro_right"]), Paragraph("8,475", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("MERCHANDISE SALES", st["micro_reg"]), Paragraph("4,997", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("4,997", st["micro_right"]), Paragraph("4,997", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("OTHER / FACILITIES", st["micro_reg"]), Paragraph("5,136", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("4,500", st["micro_right"]), Paragraph("636", st["micro_right"]), Paragraph("636", st["micro_right"]), Paragraph("0", st["micro_right"])],
        ["", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), Paragraph("<b>342,040</b>", st["micro_right_bold"]), Paragraph("<b>0</b>", st["micro_right_bold"]), Paragraph("<b>192,109</b>", st["micro_right_bold"]), Paragraph("<b>149,931</b>", st["micro_right_bold"]), Paragraph("<b>109,826</b>", st["micro_right_bold"]), Paragraph("<b>40,105</b>", st["micro_right_bold"])],
        ["", "", "", "", "", "", ""],
        [Paragraph("OPERATING EXPENSES", st["bold"]), Paragraph("317,615", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("168,748", st["micro_right"]), Paragraph("148,867", st["micro_right"]), Paragraph("103,815", st["micro_right"]), Paragraph("45,052", st["micro_right"])],
        ["", "", "", "", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME</b>", st["bold"]), Paragraph("<b>24,425</b>", st["micro_right_bold"]), Paragraph("<b>0</b>", st["micro_right_bold"]), Paragraph("<b>23,361</b>", st["micro_right_bold"]), Paragraph("<b>1,064</b>", st["micro_right_bold"]), Paragraph("<b>6,011</b>", st["micro_right_bold"]), Paragraph("<b>(4,947)</b>", st["micro_right_bold"])],
        ["", "", "", "", "", "", ""],
        [Paragraph("DEPRECIATION", st["micro_reg"]), Paragraph("(105,956)", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("(44,641)", st["micro_right"]), Paragraph("(61,315)", st["micro_right"]), Paragraph("(61,315)", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("INTEREST EXPENSE", st["micro_reg"]), Paragraph("(14,216)", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("(7,024)", st["micro_right"]), Paragraph("(7,192)", st["micro_right"]), Paragraph("(7,192)", st["micro_right"]), Paragraph("0", st["micro_right"])],
        [Paragraph("PARTNERSHIP INCOME (ELIM.)", st["micro_reg"]), Paragraph("0", st["micro_right"]), Paragraph("66,769", st["micro_right"]), Paragraph("(66,769)", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0", st["micro_right"])],
        ["", "", "", "", "", "", ""],
        [Paragraph("<b>NET INCOME</b>", st["bold"]), Paragraph("<b>(95,747)</b>", st["micro_right_bold"]), Paragraph("<b>66,769</b>", st["micro_right_bold"]), Paragraph("<b>(95,073)</b>", st["micro_right_bold"]), Paragraph("<b>(67,443)</b>", st["micro_right_bold"]), Paragraph("<b>(62,496)</b>", st["micro_right_bold"]), Paragraph("<b>(4,947)</b>", st["micro_right_bold"])],
    ]

    t_pnl = Table(pnl_data, colWidths=[150, 62, 58, 58, 58, 58, 58])
    t_pnl.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 18), (-1, 18), 1, colors.black),
        ('LINEBELOW', (1, 20), (-1, 20), 1, colors.black),
        ('LINEBELOW', (1, 22), (-1, 22), 1, colors.black),
        ('LINEBELOW', (1, 27), (-1, 27), 1.5, colors.black),
        ('LINEABOVE', (1, 27), (-1, 27), 0.5, colors.black),
    ]))
    el.append(t_pnl)

    # ==========================================
    # PAGE 3: OPERATING EXPENSE COMPARATIVE ANALYSIS (PART 1)
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("MADISON RV RESORT & JET SITES B (GOLF COURSE)", st["title"]))
    el.append(Paragraph("OPERATING EXPENSE COMPARATIVE ANALYSIS — PART 1", st["title"]))
    el.append(Paragraph("QUARTER ENDED MARCH 31, 2026", st["sub"]))
    el.append(Paragraph("ASSETS ACQUIRED OCTOBER 22, 2024", st["note"]))

    exp_data_p1 = [
        [
            Paragraph("<b>Expense Category</b>", st["bold"]),
            Paragraph("Total ($)", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
            Paragraph("RV Resort", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
            Paragraph("Golf Total", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
            Paragraph("Golf Ops", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
            Paragraph("F&B", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
        ],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), Paragraph("342,040", st["micro_right_bold"]), Paragraph("100.0%", st["micro_right_bold"]), Paragraph("192,109", st["micro_right_bold"]), Paragraph("100.0%", st["micro_right_bold"]), Paragraph("149,931", st["micro_right_bold"]), Paragraph("100.0%", st["micro_right_bold"]), Paragraph("109,824", st["micro_right_bold"]), Paragraph("100.0%", st["micro_right_bold"]), Paragraph("40,107", st["micro_right_bold"]), Paragraph("100.0%", st["micro_right_bold"])],
        [Paragraph("ADVERTISING", st["micro_reg"]), Paragraph("12,464", st["micro_right"]), Paragraph("3.64%", st["micro_right"]), Paragraph("9,208", st["micro_right"]), Paragraph("4.79%", st["micro_right"]), Paragraph("3,256", st["micro_right"]), Paragraph("2.17%", st["micro_right"]), Paragraph("3,256", st["micro_right"]), Paragraph("2.96%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("AUTOMOBILE EXPENSES", st["micro_reg"]), Paragraph("5,230", st["micro_right"]), Paragraph("1.53%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("5,230", st["micro_right"]), Paragraph("3.49%", st["micro_right"]), Paragraph("5,230", st["micro_right"]), Paragraph("4.76%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("CABLE TV", st["micro_reg"]), Paragraph("3,887", st["micro_right"]), Paragraph("1.14%", st["micro_right"]), Paragraph("3,887", st["micro_right"]), Paragraph("2.02%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("COST OF F&B FOR RESALE", st["micro_reg"]), Paragraph("3,786", st["micro_right"]), Paragraph("1.11%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("3,786", st["micro_right"]), Paragraph("2.53%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("3,786", st["micro_right"]), Paragraph("9.44%", st["micro_right"])],
        [Paragraph("COST OF LIQUOR FOR RESALE", st["micro_reg"]), Paragraph("10,474", st["micro_right"]), Paragraph("3.06%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("10,474", st["micro_right"]), Paragraph("6.99%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("10,474", st["micro_right"]), Paragraph("26.12%", st["micro_right"])],
        [Paragraph("CREDIT CARD CHARGES", st["micro_reg"]), Paragraph("11,137", st["micro_right"]), Paragraph("3.26%", st["micro_right"]), Paragraph("5,622", st["micro_right"]), Paragraph("2.93%", st["micro_right"]), Paragraph("5,515", st["micro_right"]), Paragraph("3.68%", st["micro_right"]), Paragraph("5,515", st["micro_right"]), Paragraph("5.02%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("GOLF CART RENTAL EXPENSE", st["micro_reg"]), Paragraph("11,541", st["micro_right"]), Paragraph("3.37%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("11,541", st["micro_right"]), Paragraph("7.70%", st["micro_right"]), Paragraph("11,541", st["micro_right"]), Paragraph("10.51%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("INSURANCE", st["micro_reg"]), Paragraph("11,344", st["micro_right"]), Paragraph("3.32%", st["micro_right"]), Paragraph("8,723", st["micro_right"]), Paragraph("4.54%", st["micro_right"]), Paragraph("2,621", st["micro_right"]), Paragraph("1.75%", st["micro_right"]), Paragraph("2,621", st["micro_right"]), Paragraph("2.39%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("MANAGEMENT FEES (4.0%)", st["micro_bold"]), Paragraph("13,681", st["micro_right_bold"]), Paragraph("4.00%", st["micro_right_bold"]), Paragraph("7,684", st["micro_right_bold"]), Paragraph("4.00%", st["micro_right_bold"]), Paragraph("5,997", st["micro_right_bold"]), Paragraph("4.00%", st["micro_right_bold"]), Paragraph("4,393", st["micro_right_bold"]), Paragraph("4.00%", st["micro_right_bold"]), Paragraph("1,604", st["micro_right_bold"]), Paragraph("4.00%", st["micro_right_bold"])],
    ]

    t_exp_p1 = Table(exp_data_p1, colWidths=[120, 42, 38, 42, 38, 42, 38, 42, 38, 42, 38])
    t_exp_p1.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
    ]))
    el.append(t_exp_p1)

    # ==========================================
    # PAGE 4: OPERATING EXPENSE COMPARATIVE ANALYSIS (PART 2 & TOTALS)
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("MADISON RV RESORT & JET SITES B (GOLF COURSE)", st["title"]))
    el.append(Paragraph("OPERATING EXPENSE COMPARATIVE ANALYSIS — PART 2 & TOTALS", st["title"]))
    el.append(Paragraph("QUARTER ENDED MARCH 31, 2026", st["sub"]))
    el.append(Paragraph("ASSETS ACQUIRED OCTOBER 22, 2024", st["note"]))

    exp_data_p2 = [
        [
            Paragraph("<b>Expense Category (Continued)</b>", st["bold"]),
            Paragraph("Total ($)", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
            Paragraph("RV Resort", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
            Paragraph("Golf Total", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
            Paragraph("Golf Ops", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
            Paragraph("F&B", st["micro_hdr"]),
            Paragraph("% Rev", st["micro_hdr"]),
        ],
        [Paragraph("PAYROLL — HOUSEKEEPING", st["micro_reg"]), Paragraph("3,079", st["micro_right"]), Paragraph("0.90%", st["micro_right"]), Paragraph("3,079", st["micro_right"]), Paragraph("1.60%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("PAYROLL — OFFICE", st["micro_reg"]), Paragraph("38,193", st["micro_right"]), Paragraph("11.17%", st["micro_right"]), Paragraph("38,193", st["micro_right"]), Paragraph("19.88%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("PAYROLL — RV GROUNDS", st["micro_reg"]), Paragraph("20,124", st["micro_right"]), Paragraph("5.88%", st["micro_right"]), Paragraph("20,124", st["micro_right"]), Paragraph("10.48%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("PAYROLL — GOLF BAR", st["micro_reg"]), Paragraph("27,114", st["micro_right"]), Paragraph("7.93%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("27,114", st["micro_right"]), Paragraph("18.08%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("27,114", st["micro_right"]), Paragraph("67.60%", st["micro_right"])],
        [Paragraph("PAYROLL — GOLF GROUNDS", st["micro_reg"]), Paragraph("38,901", st["micro_right"]), Paragraph("11.37%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("38,901", st["micro_right"]), Paragraph("25.95%", st["micro_right"]), Paragraph("38,901", st["micro_right"]), Paragraph("35.42%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("REPAIRS AND MAINTENANCE", st["micro_reg"]), Paragraph("21,213", st["micro_right"]), Paragraph("6.20%", st["micro_right"]), Paragraph("6,713", st["micro_right"]), Paragraph("3.49%", st["micro_right"]), Paragraph("14,500", st["micro_right"]), Paragraph("9.67%", st["micro_right"]), Paragraph("14,500", st["micro_right"]), Paragraph("13.20%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("TAXES (PAYROLL & RE)", st["micro_reg"]), Paragraph("17,459", st["micro_right"]), Paragraph("5.10%", st["micro_right"]), Paragraph("8,653", st["micro_right"]), Paragraph("4.51%", st["micro_right"]), Paragraph("8,806", st["micro_right"]), Paragraph("5.87%", st["micro_right"]), Paragraph("6,732", st["micro_right"]), Paragraph("6.13%", st["micro_right"]), Paragraph("2,074", st["micro_right"]), Paragraph("5.17%", st["micro_right"])],
        [Paragraph("TOURNAMENT EXPENSE", st["micro_reg"]), Paragraph("7,114", st["micro_right"]), Paragraph("2.08%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("7,114", st["micro_right"]), Paragraph("4.74%", st["micro_right"]), Paragraph("7,114", st["micro_right"]), Paragraph("6.48%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("UTILITIES", st["micro_reg"]), Paragraph("31,282", st["micro_right"]), Paragraph("9.15%", st["micro_right"]), Paragraph("31,282", st["micro_right"]), Paragraph("16.28%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        [Paragraph("OTHER OPERATING COSTS", st["micro_reg"]), Paragraph("39,949", st["micro_right"]), Paragraph("11.68%", st["micro_right"]), Paragraph("32,708", st["micro_right"]), Paragraph("17.03%", st["micro_right"]), Paragraph("7,241", st["micro_right"]), Paragraph("4.83%", st["micro_right"]), Paragraph("7,241", st["micro_right"]), Paragraph("6.59%", st["micro_right"]), Paragraph("0", st["micro_right"]), Paragraph("0.00%", st["micro_right"])],
        ["", "", "", "", "", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL OPERATING EXPENSE</b>", st["bold"]), Paragraph("<b>317,615</b>", st["micro_right_bold"]), Paragraph("<b>92.86%</b>", st["micro_right_bold"]), Paragraph("<b>168,748</b>", st["micro_right_bold"]), Paragraph("<b>87.84%</b>", st["micro_right_bold"]), Paragraph("<b>148,867</b>", st["micro_right_bold"]), Paragraph("<b>99.29%</b>", st["micro_right_bold"]), Paragraph("<b>103,815</b>", st["micro_right_bold"]), Paragraph("<b>94.53%</b>", st["micro_right_bold"]), Paragraph("<b>45,052</b>", st["micro_right_bold"]), Paragraph("<b>112.33%</b>", st["micro_right_bold"])],
    ]

    t_exp_p2 = Table(exp_data_p2, colWidths=[120, 42, 38, 42, 38, 42, 38, 42, 38, 42, 38])
    t_exp_p2.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 10), (-1, 10), 0.5, colors.black),
        ('LINEBELOW', (0, 12), (-1, 12), 1.5, colors.black),
        ('LINEABOVE', (0, 12), (-1, 12), 0.5, colors.black),
    ]))
    el.append(t_exp_p2)

    doc.build(el)
    print(f"✅ Generated Complete Madison CFO Replica PDF: {OUTPUT_PDF}")
    return "Madison RV Resort & Golf Course Replica Complete"

if __name__ == "__main__":
    build_pdf()
