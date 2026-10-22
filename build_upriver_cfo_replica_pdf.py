#!/usr/bin/env python3
"""
High-Fidelity Replica of Jim's Upriver Partners LLP Divestiture & Historical CFO Report.

Reconstructs the executive statement from:
source_documents/Upriver Proceeds Utilized to Date Rev 06 18 2026.pdf & UPRIVER2NDQTRFINANCIALS25.pdf:
- Page 1: Divestiture Proceeds Disposition (May 27, 2026 Sale, Tax Line Paydowns, Partner Distributions)
- Page 2: Historical Comparative Operations (Q2 Prior-Year Benchmark)

Output: pdf_reports/UPRIVER_CFO_FINANCIAL_REPORT_REPLICA.pdf
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

OUTPUT_PDF = os.path.abspath("pdf_reports/UPRIVER_CFO_FINANCIAL_REPORT_REPLICA.pdf")

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
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    st = get_styles()
    el = []

    # ==========================================
    # PAGE 1: PROCEEDS DISPOSITION
    # ==========================================
    el.append(Paragraph("UPRIVER PARTNERS LLP", st["title"]))
    el.append(Paragraph("CAPITAL ASSET SALE & PROCEEDS DISPOSITION", st["title"]))
    el.append(Paragraph("CLOSING DATE: MAY 27, 2026 (FINAL REVISED)", st["sub"]))
    el.append(Paragraph("Prepared by: James A. Adamo, Controller", st["note"]))

    disp_data = [
        ["", "", Paragraph("AMOUNT ($)", st["col_hdr"])],
        [Paragraph("<b>GROSS CAPITAL SALE PROCEEDS (SKYLINE LEDGER)</b>", st["bold"]), "", Paragraph("<b>59,800,000.00</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;Payoff of Existing Senior Mortgage Debt", st["reg"]), "", Paragraph("(36,933,735.08)", st["right"])],
        ["", "", Paragraph("22,866,264.92", st["right_bold"])],
        [Paragraph("<b>NET CASH PROCEEDS RECEIVED AT CLOSING</b>", st["bold"]), "", Paragraph("<b>22,866,264.92</b>", st["right_bold"])],
        ["", "", ""],
        [Paragraph("<b>UTILIZATION & CAPITAL DEPLOYMENT TO DATE</b>", st["bold"]), "", ""],
        [Paragraph("&nbsp;&nbsp;Partner Distribution — JL", st["reg"]), "", Paragraph("(3,500,000.00)", st["right"])],
        [Paragraph("&nbsp;&nbsp;Partner Distribution — LL", st["reg"]), "", Paragraph("(1,000,000.00)", st["right"])],
        [Paragraph("&nbsp;&nbsp;Tax Line Loan Paydown — Old National (6/1/2026)", st["reg"]), "", Paragraph("(4,000,000.00)", st["right"])],
        [Paragraph("&nbsp;&nbsp;Tax Line Loan Paydown — Old National (6/3/2026)", st["reg"]), "", Paragraph("(4,000,000.00)", st["right"])],
        [Paragraph("&nbsp;&nbsp;Tax Line Loan Paydown — Old National (6/9/2026)", st["reg"]), "", Paragraph("(4,000,000.00)", st["right"])],
        ["", "", Paragraph("(16,500,000.00)", st["right_bold"])],
        ["", "", ""],
        [Paragraph("<b>NET BALANCE OF UNUSED PROCEEDS (6/11/2026)</b>", st["bold"]), "", Paragraph("<b>6,366,264.92</b>", st["right_bold"])],
        ["", "", ""],
        [Paragraph("<b>AFFILIATE RE-INVESTMENT & BUYOUTS (JUNE 2026)</b>", st["bold"]), "", ""],
        [Paragraph("&nbsp;&nbsp;Madison RV Resort — Partner Buyout (Mike Berland)", st["reg"]), "", Paragraph("(500,000.00)", st["right"])],
        [Paragraph("&nbsp;&nbsp;The Bluffs MH & RV Resort — Infrastructure Capex", st["reg"]), "", Paragraph("(750,000.00)", st["right"])],
        [Paragraph("&nbsp;&nbsp;Old National Bank Cash Collateral Account", st["reg"]), "", Paragraph("9,400,000.00", st["right"])],
        [Paragraph("&nbsp;&nbsp;Excess Tax Line Collateral Remaining", st["reg"]), "", Paragraph("12,800,000.00", st["right"])],
    ]

    t_disp = Table(disp_data, colWidths=[310, 20, 150])
    t_disp.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (2, 0), (2, 0), 1, colors.black),
        ('LINEBELOW', (2, 3), (2, 3), 1, colors.black),
        ('LINEBELOW', (2, 4), (2, 4), 1.5, colors.black),
        ('LINEABOVE', (2, 4), (2, 4), 0.5, colors.black),
        ('LINEBELOW', (2, 12), (2, 12), 1, colors.black),
        ('LINEBELOW', (2, 14), (2, 14), 1.5, colors.black),
        ('LINEABOVE', (2, 14), (2, 14), 0.5, colors.black),
    ]))
    el.append(t_disp)

    # ==========================================
    # PAGE 2: HISTORICAL COMPARATIVE OPERATIONS
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("UPRIVER PARTNERS LLP", st["title"]))
    el.append(Paragraph("HISTORICAL STATEMENT OF OPERATIONS (PRE-DIVESTITURE)", st["title"]))
    el.append(Paragraph("Q2 THREE MONTHS ENDED JUNE 30, 2025 vs. JUNE 30, 2024", st["sub"]))

    hist_data = [
        ["", "", Paragraph("6/30/2025", st["col_hdr"]), Paragraph("6/30/2024", st["col_hdr"])],
        [Paragraph("RENTAL & RESORT INCOME", st["bold"]), "", Paragraph("1,485,210", st["right"]), Paragraph("1,420,500", st["right"])],
        [Paragraph("UTILITY REIMBURSEMENTS", st["reg"]), "", Paragraph("95,400", st["right"]), Paragraph("88,200", st["right"])],
        ["", "", Paragraph("1,580,610", st["right_bold"]), Paragraph("1,508,700", st["right_bold"])],
        [Paragraph("OPERATING EXPENSES (ON-SITE & PAYROLL)", st["bold"]), "", Paragraph("712,400", st["right"]), Paragraph("685,300", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME (NOI)</b>", st["bold"]), "", Paragraph("<b>868,210</b>", st["right_bold"]), Paragraph("<b>823,400</b>", st["right_bold"])],
        [Paragraph("SENIOR MORTGAGE INTEREST", st["reg"]), "", Paragraph("(345,100)", st["right"]), Paragraph("(352,000)", st["right"])],
        [Paragraph("DEPRECIATION & AMORTIZATION", st["reg"]), "", Paragraph("(185,400)", st["right"]), Paragraph("(180,000)", st["right"])],
        ["", "", Paragraph("(530,500)", st["right_bold"]), Paragraph("(532,000)", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>NET INCOME</b>", st["bold"]), "", Paragraph("<b>337,710</b>", st["right_bold"]), Paragraph("<b>291,400</b>", st["right_bold"])],
    ]

    t_hist = Table(hist_data, colWidths=[260, 20, 125, 125])
    t_hist.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 3), (3, 3), 1, colors.black),
        ('LINEBELOW', (2, 6), (3, 6), 1, colors.black),
        ('LINEBELOW', (2, 9), (3, 9), 1, colors.black),
        ('LINEBELOW', (2, 11), (3, 11), 1.5, colors.black),
        ('LINEABOVE', (2, 11), (3, 11), 0.5, colors.black),
    ]))
    el.append(t_hist)

    doc.build(el)
    print(f"✅ Generated Complete Upriver CFO Replica PDF: {OUTPUT_PDF}")
    return "Upriver Divestiture & Historical Replica Complete"

if __name__ == "__main__":
    build_pdf()
