#!/usr/bin/env python3
"""
High-Fidelity Replica of Jim's Barbara Descendant's Trust CFO Financial Report Package.

Reconstructs the executive multi-entity trust package from:
source_documents/BARBARADESCTR 06302025pdf.pdf:
- Page 1: Consolidating Balance Sheet (Park City Plaza, Rental Properties, Parent & Other, Combined)
- Page 2: Consolidating Income Statement (Park City Plaza, Rental Properties, Parent & Other, Combined)
- Page 3: Operating Expense Breakdown by Division (Landscaping, Management Fees, RE Taxes, Utilities)

Output: pdf_reports/BARBARA_TRUST_CFO_FINANCIAL_REPORT_REPLICA.pdf
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

OUTPUT_PDF = os.path.abspath("pdf_reports/BARBARA_TRUST_CFO_FINANCIAL_REPORT_REPLICA.pdf")
DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def query_barbara_trust_live_data():
    """Queries 100% live Skyline GL balances for Barbara Descendant's Trust (IFS 110)."""
    if not os.path.exists(DB_PATH):
        return None
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    rev = cursor.execute("SELECT -SUM(amount) FROM journal_entries WHERE ifs_id='110' AND account LIKE '3%'").fetchone()[0] or 0.0
    exp = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='110' AND (account LIKE '4%' OR account LIKE '5%' OR account LIKE '6%' OR account LIKE '7%' OR account LIKE '8%' OR account LIKE '9%')").fetchone()[0] or 0.0
    tot_ast = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='110' AND account LIKE '1%'").fetchone()[0] or 0.0
    cash = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='110' AND account LIKE '10%'").fetchone()[0] or 0.0
    conn.close()
    return {"rev": rev, "exp": exp, "noi": rev - exp, "tot_ast": tot_ast, "cash": cash}

def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('TCenter', fontName='Helvetica-Bold', fontSize=10.5, leading=13, alignment=1, spaceAfter=2),
        "sub": ParagraphStyle('TSub', fontName='Helvetica-Bold', fontSize=8.5, leading=11, alignment=1, spaceAfter=8),
        "bold": ParagraphStyle('CBold', fontName='Helvetica-Bold', fontSize=7, leading=9),
        "reg": ParagraphStyle('CReg', fontName='Helvetica', fontSize=7, leading=9),
        "right": ParagraphStyle('CRight', fontName='Helvetica', fontSize=7, leading=9, alignment=2),
        "right_bold": ParagraphStyle('CRightBold', fontName='Helvetica-Bold', fontSize=7, leading=9, alignment=2),
        "col_hdr": ParagraphStyle('ColHdr', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=2),
    }

def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=30, bottomMargin=30)
    st = get_styles()
    el = []

    # ==========================================
    # PAGE 1: CONSOLIDATING BALANCE SHEET
    # ==========================================
    el.append(Paragraph("BARBARA DESCENDANT'S TRUST", st["title"]))
    el.append(Paragraph("CONSOLIDATING BALANCE SHEET", st["title"]))
    el.append(Paragraph("JUNE 30, 2025 (FYE / Q4 BENCHMARK)", st["sub"]))

    bs_data = [
        [
            Paragraph("<b>ASSETS & LIABILITIES</b>", st["bold"]),
            Paragraph("PARK CITY<br/>PLAZA", st["col_hdr"]),
            Paragraph("RENTAL<br/>PROPERTIES", st["col_hdr"]),
            Paragraph("PARENT &<br/>OTHER", st["col_hdr"]),
            Paragraph("COMBINED<br/>TOTAL", st["col_hdr"]),
        ],
        [Paragraph("PROPERTY AND EQUIPMENT", st["bold"]), "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;LAND", st["reg"]), Paragraph("34,275", st["right"]), Paragraph("1,303,273", st["right"]), Paragraph("0", st["right"]), Paragraph("1,337,548", st["right"])],
        [Paragraph("&nbsp;&nbsp;REAL ESTATE", st["reg"]), Paragraph("843,078", st["right"]), Paragraph("383,628", st["right"]), Paragraph("0", st["right"]), Paragraph("1,226,706", st["right"])],
        [Paragraph("&nbsp;&nbsp;MOBILE HOME SITES & IMPROVEMENTS", st["reg"]), Paragraph("286,650", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("286,650", st["right"])],
        [Paragraph("&nbsp;&nbsp;FURNITURE AND EQUIPMENT", st["reg"]), Paragraph("44,469", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("44,469", st["right"])],
        [Paragraph("&nbsp;&nbsp;PAVING & LANDSCAPING", st["reg"]), Paragraph("0", st["right"]), Paragraph("73,683", st["right"]), Paragraph("0", st["right"]), Paragraph("73,683", st["right"])],
        [Paragraph("&nbsp;&nbsp;STREET LIGHTS", st["reg"]), Paragraph("0", st["right"]), Paragraph("52,561", st["right"]), Paragraph("0", st["right"]), Paragraph("52,561", st["right"])],
        ["", Paragraph("1,208,472", st["right_bold"]), Paragraph("1,813,145", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("3,021,617", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;LESS ACCUMULATED DEPRECIATION", st["reg"]), Paragraph("(477,382)", st["right"]), Paragraph("(194,540)", st["right"]), Paragraph("0", st["right"]), Paragraph("(671,921)", st["right"])],
        ["", Paragraph("731,090", st["right_bold"]), Paragraph("1,618,606", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("2,349,696", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("OTHER ASSETS (CASH & RECEIVABLES)", st["bold"]), Paragraph("30,734", st["right"]), Paragraph("13,821", st["right"]), Paragraph("534,079", st["right"]), Paragraph("578,634", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), Paragraph("<b>761,824</b>", st["right_bold"]), Paragraph("<b>1,632,427</b>", st["right_bold"]), Paragraph("<b>534,079</b>", st["right_bold"]), Paragraph("<b>2,928,330</b>", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("LIABILITIES (AP & DUE TO RELATED)", st["bold"]), Paragraph("125,400", st["right"]), Paragraph("48,210", st["right"]), Paragraph("1,850,000", st["right"]), Paragraph("2,023,610", st["right"])],
        [Paragraph("TRUST CAPITAL & RETAINED EARNINGS", st["bold"]), Paragraph("636,424", st["right"]), Paragraph("1,584,217", st["right"]), Paragraph("(1,315,921)", st["right"]), Paragraph("904,720", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & TRUST CAPITAL</b>", st["bold"]), Paragraph("<b>761,824</b>", st["right_bold"]), Paragraph("<b>1,632,427</b>", st["right_bold"]), Paragraph("<b>534,079</b>", st["right_bold"]), Paragraph("<b>2,928,330</b>", st["right_bold"])],
    ]

    t_bs = Table(bs_data, colWidths=[230, 75, 75, 75, 85])
    t_bs.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 7), (-1, 7), 0.5, colors.black),
        ('LINEBELOW', (1, 9), (-1, 9), 0.5, colors.black),
        ('LINEBELOW', (1, 13), (-1, 13), 1.5, colors.black),
        ('LINEABOVE', (1, 13), (-1, 13), 0.5, colors.black),
        ('LINEBELOW', (1, 18), (-1, 18), 1.5, colors.black),
        ('LINEABOVE', (1, 18), (-1, 18), 0.5, colors.black),
    ]))
    el.append(t_bs)

    # ==========================================
    # PAGE 2: CONSOLIDATING INCOME STATEMENT
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("BARBARA DESCENDANT'S TRUST", st["title"]))
    el.append(Paragraph("CONSOLIDATING STATEMENT OF INCOME", st["title"]))
    el.append(Paragraph("QUARTER ENDED JUNE 30, 2025", st["sub"]))

    pnl_data = [
        [
            Paragraph("<b>Category</b>", st["bold"]),
            Paragraph("PARK CITY<br/>PLAZA", st["col_hdr"]),
            Paragraph("RENTAL<br/>PROPERTIES", st["col_hdr"]),
            Paragraph("PARENT &<br/>OTHER", st["col_hdr"]),
            Paragraph("COMBINED<br/>TOTAL", st["col_hdr"]),
        ],
        [Paragraph("RENTAL INCOME", st["bold"]), Paragraph("149,753", st["right"]), Paragraph("31,434", st["right"]), Paragraph("0", st["right"]), Paragraph("181,187", st["right"])],
        [Paragraph("OPERATING EXPENSES", st["bold"]), Paragraph("52,428", st["right"]), Paragraph("28,365", st["right"]), Paragraph("327,813", st["right"]), Paragraph("408,606", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME</b>", st["bold"]), Paragraph("<b>97,325</b>", st["right_bold"]), Paragraph("<b>3,069</b>", st["right_bold"]), Paragraph("<b>(327,813)</b>", st["right_bold"]), Paragraph("<b>(227,419)</b>", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("DEPRECIATION EXPENSE", st["reg"]), Paragraph("(19,161)", st["right"]), Paragraph("(7,878)", st["right"]), Paragraph("0", st["right"]), Paragraph("(27,040)", st["right"])],
        [Paragraph("INTEREST INCOME / (EXPENSE)", st["reg"]), Paragraph("(4,483)", st["right"]), Paragraph("0", st["right"]), Paragraph("(255,757)", st["right"]), Paragraph("(260,240)", st["right"])],
        [Paragraph("DIVIDEND INCOME", st["reg"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("4,721", st["right"]), Paragraph("4,721", st["right"])],
        [Paragraph("GAIN / (LOSS) ON SALE OF R.E.", st["reg"]), Paragraph("0", st["right"]), Paragraph("(21,843)", st["right"]), Paragraph("0", st["right"]), Paragraph("(21,843)", st["right"])],
        ["", Paragraph("(23,644)", st["right_bold"]), Paragraph("(29,721)", st["right_bold"]), Paragraph("(251,036)", st["right_bold"]), Paragraph("(304,401)", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("<b>NET INCOME / (LOSS)</b>", st["bold"]), Paragraph("<b>73,681</b>", st["right_bold"]), Paragraph("<b>(26,653)</b>", st["right_bold"]), Paragraph("<b>(578,849)</b>", st["right_bold"]), Paragraph("<b>(531,820)</b>", st["right_bold"])],
    ]

    t_pnl = Table(pnl_data, colWidths=[230, 75, 75, 75, 85])
    t_pnl.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 2), (-1, 2), 0.5, colors.black),
        ('LINEBELOW', (1, 4), (-1, 4), 1, colors.black),
        ('LINEBELOW', (1, 9), (-1, 9), 0.5, colors.black),
        ('LINEBELOW', (1, 11), (-1, 11), 1.5, colors.black),
        ('LINEABOVE', (1, 11), (-1, 11), 0.5, colors.black),
    ]))
    el.append(t_pnl)

    # ==========================================
    # PAGE 3: OPERATING EXPENSE BREAKDOWN
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("BARBARA DESCENDANT'S TRUST", st["title"]))
    el.append(Paragraph("OPERATING EXPENSE BREAKDOWN BY DIVISION", st["title"]))
    el.append(Paragraph("QUARTER ENDED JUNE 30, 2025", st["sub"]))

    exp_data = [
        [
            Paragraph("<b>Expense Category</b>", st["bold"]),
            Paragraph("PARK CITY<br/>PLAZA", st["col_hdr"]),
            Paragraph("RENTAL<br/>PROPERTIES", st["col_hdr"]),
            Paragraph("PARENT &<br/>OTHER", st["col_hdr"]),
            Paragraph("COMBINED<br/>TOTAL", st["col_hdr"]),
        ],
        [Paragraph("ADVERTISING", st["reg"]), Paragraph("0", st["right"]), Paragraph("750", st["right"]), Paragraph("0", st["right"]), Paragraph("750", st["right"])],
        [Paragraph("BANK CHARGES", st["reg"]), Paragraph("0", st["right"]), Paragraph("21", st["right"]), Paragraph("3", st["right"]), Paragraph("24", st["right"])],
        [Paragraph("INSURANCE", st["reg"]), Paragraph("597", st["right"]), Paragraph("237", st["right"]), Paragraph("0", st["right"]), Paragraph("834", st["right"])],
        [Paragraph("LANDSCAPING", st["reg"]), Paragraph("0", st["right"]), Paragraph("14,806", st["right"]), Paragraph("0", st["right"]), Paragraph("14,806", st["right"])],
        [Paragraph("MANAGEMENT FEES", st["reg"]), Paragraph("10,793", st["right"]), Paragraph("1,336", st["right"]), Paragraph("322,413", st["right"]), Paragraph("334,542", st["right"])],
        [Paragraph("PROFESSIONAL FEES", st["reg"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("5,244", st["right"]), Paragraph("5,244", st["right"])],
        [Paragraph("REPAIRS AND MAINTENANCE", st["reg"]), Paragraph("3,292", st["right"]), Paragraph("2,785", st["right"]), Paragraph("0", st["right"]), Paragraph("6,077", st["right"])],
        [Paragraph("REAL ESTATE TAXES", st["reg"]), Paragraph("30,735", st["right"]), Paragraph("6,208", st["right"]), Paragraph("0", st["right"]), Paragraph("36,943", st["right"])],
        [Paragraph("OTHER TAXES", st["reg"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("153", st["right"]), Paragraph("153", st["right"])],
        [Paragraph("UTILITIES", st["reg"]), Paragraph("7,011", st["right"]), Paragraph("2,222", st["right"]), Paragraph("0", st["right"]), Paragraph("9,233", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL OPERATING EXPENSES</b>", st["bold"]), Paragraph("<b>52,428</b>", st["right_bold"]), Paragraph("<b>28,365</b>", st["right_bold"]), Paragraph("<b>327,813</b>", st["right_bold"]), Paragraph("<b>408,606</b>", st["right_bold"])],
    ]

    t_exp = Table(exp_data, colWidths=[230, 75, 75, 75, 85])
    t_exp.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 10), (-1, 10), 0.5, colors.black),
        ('LINEBELOW', (1, 12), (-1, 12), 1.5, colors.black),
        ('LINEABOVE', (1, 12), (-1, 12), 0.5, colors.black),
    ]))
    el.append(t_exp)

    doc.build(el)
    print(f"✅ Generated Complete Barbara Trust CFO Replica PDF: {OUTPUT_PDF}")
    return "Barbara Trust Consolidating Replica Complete"

if __name__ == "__main__":
    build_pdf()
