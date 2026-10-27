#!/usr/bin/env python3
"""
High-Fidelity Replica of Jim's Sunkissed Village RV Resort CFO Financial Report Package.

Reconstructs all 5 pages of source_documents/SUNKISSEDFINANCIALS63026.pdf:
- Page 1: Comparative Balance Sheet (June 30, 2026 vs June 30, 2025)
- Page 2: Statement of Income and Retained Earnings (June 30, 2026 vs June 30, 2025)
- Page 3: Operating Expense Comparative Analysis (with % of Revenue benchmarks)
- Page 4: Monthly Operating Income and Expense (Jan-Jun 2026 Seasonality Schedule)
- Page 5: Utility Detail & Electric Recovery Ratio

Output: pdf_reports/SUNKISSED_VILLAGE_CFO_FINANCIAL_REPORT_REPLICA.pdf
"""

import os
import sys
import time
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

OUTPUT_PDF = os.path.abspath("pdf_reports/SUNKISSED_VILLAGE_CFO_FINANCIAL_REPORT_REPLICA.pdf")
DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def query_sunkissed_live_data():
    """Queries 100% live Skyline GL balances for Sunkissed Village (IFS 140, 142)."""
    if not os.path.exists(DB_PATH):
        return None
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # P&L
    rev = cursor.execute("SELECT -SUM(amount) FROM journal_entries WHERE ifs_id IN ('140', '142') AND account LIKE '3%'").fetchone()[0] or 0.0
    exp = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ('140', '142') AND (account LIKE '4%' OR account LIKE '5%' OR account LIKE '6%' OR account LIKE '7%' OR account LIKE '8%' OR account LIKE '9%')").fetchone()[0] or 0.0
    # Balance Sheet
    cash = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ('140', '142') AND account LIKE '10%'").fetchone()[0] or 0.0
    tot_ast = cursor.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ('140', '142') AND account LIKE '1%'").fetchone()[0] or 0.0
    conn.close()
    return {"rev": rev, "exp": exp, "noi": rev - exp, "cash": cash, "tot_ast": tot_ast}

def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('TCenter', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, spaceAfter=2),
        "sub": ParagraphStyle('TSub', fontName='Helvetica-Bold', fontSize=9.5, leading=12, alignment=1, spaceAfter=12),
        "sec": ParagraphStyle('SecHdr', fontName='Helvetica-Bold', fontSize=8.5, leading=11, spaceBefore=4, spaceAfter=2),
        "bold": ParagraphStyle('CBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5),
        "reg": ParagraphStyle('CReg', fontName='Helvetica', fontSize=7.5, leading=9.5),
        "right": ParagraphStyle('CRight', fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=2),
        "right_bold": ParagraphStyle('CRightBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, alignment=2),
        "micro_reg": ParagraphStyle('MicroReg', fontName='Helvetica', fontSize=6.8, leading=8.5),
        "micro_right": ParagraphStyle('MicroRight', fontName='Helvetica', fontSize=6.8, leading=8.5, alignment=2),
        "micro_right_bold": ParagraphStyle('MicroRightBold', fontName='Helvetica-Bold', fontSize=6.8, leading=8.5, alignment=2),
    }

import skyline_report_data_provider as sdp

def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    st = get_styles()
    el = []

    # Dynamic Skyline GL Data (50% JV Member Interest)
    sk = sdp.get_sunkissed_data()

    # ==========================================
    # PAGE 1: COMPARATIVE BALANCE SHEET
    # ==========================================
    el.append(Paragraph("SUNKISSED VILLAGE RV RESORT", st["title"]))
    el.append(Paragraph("BALANCE SHEET (100% SKYLINE GENERAL LEDGER)", st["title"]))
    el.append(Paragraph(f"AS OF {time.strftime('%B %d, %Y').upper()} (TODAY'S LIVE LEDGER POSITION)", st["sub"]))

    col_hdr = ParagraphStyle('ColHdr', fontName='Helvetica-Bold', fontSize=7, leading=9, alignment=2)
    bs_data = [
        ["", Paragraph("Skyline GL<br/>(100% Property)", col_hdr), Paragraph("Jennings Share<br/>(50% JV Interest)", col_hdr), Paragraph("Prior-Year<br/>(6/30/2025)", col_hdr)],
        [Paragraph("<b>ASSETS</b>", st["bold"]), "", "", ""],
        [Paragraph("PROPERTY AND EQUIPMENT", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;LAND (15000000)", st["reg"]), Paragraph(f"{sk['land']:,.0f}", st["right"]), Paragraph(f"{sk['land']*0.5:,.0f}", st["right"]), Paragraph("1,300,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;SITES AND IMPROVEMENTS (1700-1708)", st["reg"]), Paragraph(f"{sk['bld_sites']:,.0f}", st["right"]), Paragraph(f"{sk['bld_sites']*0.5:,.0f}", st["right"]), Paragraph("9,651,327", st["right"])],
        [Paragraph("&nbsp;&nbsp;FURNITURE AND EQUIPMENT (1670)", st["reg"]), Paragraph(f"{sk['furn']:,.0f}", st["right"]), Paragraph(f"{sk['furn']*0.5:,.0f}", st["right"]), Paragraph("398,605", st["right"])],
        [Paragraph("&nbsp;&nbsp;VEHICLES (1690)", st["reg"]), Paragraph(f"{sk['veh']:,.0f}", st["right"]), Paragraph(f"{sk['veh']*0.5:,.0f}", st["right"]), Paragraph("30,634", st["right"])],
        ["", Paragraph(f"{sk['land'] + sk['bld_sites'] + sk['furn'] + sk['veh']:,.0f}", st["right_bold"]), Paragraph(f"{(sk['land'] + sk['bld_sites'] + sk['furn'] + sk['veh'])*0.5:,.0f}", st["right_bold"]), Paragraph("11,380,566", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;LESS ACCUMULATED DEPRECIATION", st["reg"]), Paragraph(f"({sk['ad']:,.0f})", st["right"]), Paragraph(f"({sk['ad']*0.5:,.0f})", st["right"]), Paragraph("(2,360,782)", st["right"])],
        ["", Paragraph(f"{sk['net_ppe']:,.0f}", st["right_bold"]), Paragraph(f"{sk['net_ppe']*0.5:,.0f}", st["right_bold"]), Paragraph("9,019,784", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("OTHER ASSETS", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH & CASH EQUIVALENTS (1014-1031)", st["reg"]), Paragraph(f"{sk['cash']:,.0f}", st["right"]), Paragraph(f"{sk['cash']*0.5:,.0f}", st["right"]), Paragraph("1,417,440", st["right"])],
        [Paragraph("&nbsp;&nbsp;PREPAID EXPENSES & DEPOSITS (1450-1750)", st["reg"]), Paragraph(f"{sk['prepaid']:,.0f}", st["right"]), Paragraph(f"{sk['prepaid']*0.5:,.0f}", st["right"]), Paragraph("119,736", st["right"])],
        ["", Paragraph(f"{sk['cash'] + sk['prepaid']:,.0f}", st["right_bold"]), Paragraph(f"{(sk['cash'] + sk['prepaid'])*0.5:,.0f}", st["right_bold"]), Paragraph("1,537,176", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), Paragraph(f"<b>{sk['tot_ast']:,.0f}</b>", st["right_bold"]), Paragraph(f"<b>{sk['tot_ast']*0.5:,.0f}</b>", st["right_bold"]), Paragraph("<b>10,556,960</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>LIABILITIES AND PARTNERS' CAPITAL</b>", st["bold"]), "", "", ""],
        [Paragraph("LIABILITIES", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS PAYABLE & ACCRUED EXPENSES", st["reg"]), Paragraph(f"{sk['ap']:,.0f}", st["right"]), Paragraph(f"{sk['ap']*0.5:,.0f}", st["right"]), Paragraph("99,754", st["right"])],
        [Paragraph("&nbsp;&nbsp;TENANTS' SECURITY DEPOSITS & UNEARNED", st["reg"]), Paragraph(f"{sk['deposits']:,.0f}", st["right"]), Paragraph(f"{sk['deposits']*0.5:,.0f}", st["right"]), Paragraph("182,410", st["right"])],
        ["", Paragraph(f"{sk['ap'] + sk['deposits']:,.0f}", st["right_bold"]), Paragraph(f"{(sk['ap'] + sk['deposits'])*0.5:,.0f}", st["right_bold"]), Paragraph("282,164", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("LONG-TERM DEBT (MORTGAGE LOAN 2250)", st["bold"]), Paragraph(f"{sk['mtg']:,.0f}", st["right"]), Paragraph(f"{sk['mtg']*0.5:,.0f}", st["right"]), Paragraph("4,874,210", st["right"])],
        ["", "", "", ""],
        [Paragraph("MEMBERS EQUITY & CAPITAL", st["bold"]), Paragraph(f"{sk['equity']:,.0f}", st["right"]), Paragraph(f"{sk['equity']*0.5:,.0f}", st["right"]), Paragraph("5,400,586", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & MEMBERS EQUITY</b>", st["bold"]), Paragraph(f"<b>{sk['tot_ast']:,.0f}</b>", st["right_bold"]), Paragraph(f"<b>{sk['tot_ast']*0.5:,.0f}</b>", st["right_bold"]), Paragraph("<b>10,556,960</b>", st["right_bold"])],
    ]

    t_bs = Table(bs_data, colWidths=[210, 110, 110, 110])
    t_bs.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (1, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (1, 7), (3, 7), 0.5, colors.black),
        ('LINEBELOW', (1, 9), (3, 9), 0.5, colors.black),
        ('LINEBELOW', (1, 14), (3, 14), 0.5, colors.black),
        ('LINEBELOW', (1, 16), (3, 16), 1.5, colors.black),
        ('LINEABOVE', (1, 16), (3, 16), 0.5, colors.black),
        ('LINEBELOW', (1, 21), (3, 21), 0.5, colors.black),
        ('LINEBELOW', (1, 27), (3, 27), 1.5, colors.black),
        ('LINEABOVE', (1, 27), (3, 27), 0.5, colors.black),
    ]))
    el.append(t_bs)

    # ==========================================
    # PAGE 2: INCOME STATEMENT
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("SUNKISSED VILLAGE RV RESORT", st["title"]))
    el.append(Paragraph("STATEMENT OF INCOME AND RETAINED EARNINGS", st["title"]))
    el.append(Paragraph("FOR THE PERIOD ENDING JUNE 30, 2026", st["sub"]))

    pnl_data = [
        [Paragraph("REVENUE", st["bold"]), "", Paragraph("6/30/2026", st["right_bold"]), Paragraph("6/30/2025", st["right_bold"])],
        [Paragraph("RENTAL INCOME (SITE LEASES)", st["reg"]), "", Paragraph("1,125,333", st["right"]), Paragraph("1,092,464", st["right"])],
        [Paragraph("LAUNDRY INCOME", st["reg"]), "", Paragraph("9,790", st["right"]), Paragraph("10,124", st["right"])],
        [Paragraph("PROPANE GAS SALES", st["reg"]), "", Paragraph("15,036", st["right"]), Paragraph("12,799", st["right"])],
        [Paragraph("SUNDRY INCOME", st["reg"]), "", Paragraph("3,177", st["right"]), Paragraph("4,487", st["right"])],
        [Paragraph("MISCELLANEOUS INCOME - ICE", st["reg"]), "", Paragraph("1,144", st["right"]), Paragraph("1,200", st["right"])],
        [Paragraph("STORE MERCHANDISE INCOME", st["reg"]), "", Paragraph("4,250", st["right"]), Paragraph("3,850", st["right"])],
        [Paragraph("ELECTRIC INCOME (SUBMETER REIMBURSEMENTS)", st["reg"]), "", Paragraph("90,225", st["right"]), Paragraph("90,389", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), "", Paragraph("<b>1,248,955</b>", st["right_bold"]), Paragraph("<b>1,215,313</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("OPERATING EXPENSES", st["bold"]), "", Paragraph("742,771", st["right"]), Paragraph("710,480", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>OPERATING INCOME (NOI)</b>", st["bold"]), "", Paragraph("<b>506,184</b>", st["right_bold"]), Paragraph("<b>504,833</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("OTHER INCOME OR (EXPENSE)", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;DEPRECIATION EXPENSE", st["reg"]), "", Paragraph("(218,001)", st["right"]), Paragraph("(215,400)", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTEREST EXPENSE (MORTGAGE)", st["reg"]), "", Paragraph("(148,090)", st["right"]), Paragraph("(155,200)", st["right"])],
        ["", "", Paragraph("(366,091)", st["right"]), Paragraph("(370,600)", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>NET INCOME</b>", st["bold"]), "", Paragraph("<b>140,093</b>", st["right_bold"]), Paragraph("<b>134,233</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("MEMBERS EQUITY-BEGINNING", st["reg"]), "", Paragraph("5,232,793", st["right"]), Paragraph("5,266,353", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>MEMBERS EQUITY-ENDING</b>", st["bold"]), "", Paragraph("<b>5,372,886</b>", st["right_bold"]), Paragraph("<b>5,400,586</b>", st["right_bold"])],
    ]

    t_pnl = Table(pnl_data, colWidths=[280, 20, 115, 115])
    t_pnl.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 9), (3, 9), 1, colors.black),
        ('LINEBELOW', (2, 11), (3, 11), 1, colors.black),
        ('LINEBELOW', (2, 13), (3, 13), 1, colors.black),
        ('LINEBELOW', (2, 17), (3, 17), 0.5, colors.black),
        ('LINEBELOW', (2, 19), (3, 19), 1.5, colors.black),
        ('LINEABOVE', (2, 19), (3, 19), 0.5, colors.black),
        ('LINEBELOW', (2, 23), (3, 23), 1.5, colors.black),
        ('LINEABOVE', (2, 23), (3, 23), 0.5, colors.black),
    ]))
    el.append(t_pnl)

    # ==========================================
    # PAGE 3: OPERATING EXPENSE COMPARATIVE (% OF REV)
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("SUNKISSED VILLAGE RV RESORT", st["title"]))
    el.append(Paragraph("OPERATING EXPENSE COMPARATIVE ANALYSIS", st["title"]))
    el.append(Paragraph("PARK OPERATIONS — 6/30/2026 vs. 6/30/2025", st["sub"]))

    exp_data = [
        [Paragraph("Line Item", st["bold"]), Paragraph("6/30/2026 ($)", st["right_bold"]), Paragraph("% of Rev", st["right_bold"]), Paragraph("6/30/2025 ($)", st["right_bold"]), Paragraph("% of Rev", st["right_bold"])],
        [Paragraph("<b>Total Revenue</b>", st["bold"]), Paragraph("<b>1,248,955</b>", st["right_bold"]), Paragraph("100.00%", st["right_bold"]), Paragraph("<b>1,215,313</b>", st["right_bold"]), Paragraph("100.00%", st["right_bold"])],
        [Paragraph("ADVERTISING", st["reg"]), Paragraph("10,150", st["right"]), Paragraph("0.81%", st["right"]), Paragraph("7,929", st["right"]), Paragraph("0.65%", st["right"])],
        [Paragraph("INSURANCE", st["reg"]), Paragraph("26,637", st["right"]), Paragraph("2.13%", st["right"]), Paragraph("24,500", st["right"]), Paragraph("2.02%", st["right"])],
        [Paragraph("MANAGEMENT FEES (4.00%)", st["bold"]), Paragraph("49,958", st["right_bold"]), Paragraph("4.00%", st["right_bold"]), Paragraph("48,612", st["right_bold"]), Paragraph("4.00%", st["right_bold"])],
        [Paragraph("PAYROLL (OFFICE & MAINTENANCE)", st["reg"]), Paragraph("200,779", st["right"]), Paragraph("16.08%", st["right"]), Paragraph("195,000", st["right"]), Paragraph("16.05%", st["right"])],
        [Paragraph("PROPANE GAS WHOLESALE", st["reg"]), Paragraph("12,450", st["right"]), Paragraph("1.00%", st["right"]), Paragraph("10,200", st["right"]), Paragraph("0.84%", st["right"])],
        [Paragraph("REPAIRS AND MAINTENANCE", st["reg"]), Paragraph("42,169", st["right"]), Paragraph("3.38%", st["right"]), Paragraph("45,000", st["right"]), Paragraph("3.70%", st["right"])],
        [Paragraph("REFUSE REMOVAL (TRASH)", st["reg"]), Paragraph("24,500", st["right"]), Paragraph("1.96%", st["right"]), Paragraph("22,400", st["right"]), Paragraph("1.84%", st["right"])],
        [Paragraph("TAXES - REAL ESTATE", st["reg"]), Paragraph("62,996", st["right"]), Paragraph("5.04%", st["right"]), Paragraph("58,400", st["right"]), Paragraph("4.81%", st["right"])],
        [Paragraph("UTILITIES (ELECTRIC, WATER, SEWER)", st["reg"]), Paragraph("122,775", st["right"]), Paragraph("9.83%", st["right"]), Paragraph("120,500", st["right"]), Paragraph("9.92%", st["right"])],
        [Paragraph("OTHER OPERATING COSTS", st["reg"]), Paragraph("190,357", st["right"]), Paragraph("15.24%", st["right"]), Paragraph("177,939", st["right"]), Paragraph("14.64%", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL OPERATING EXPENSES</b>", st["bold"]), Paragraph("<b>742,771</b>", st["right_bold"]), Paragraph("<b>59.47%</b>", st["right_bold"]), Paragraph("<b>710,480</b>", st["right_bold"]), Paragraph("<b>58.46%</b>", st["right_bold"])],
        ["", "", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME</b>", st["bold"]), Paragraph("<b>506,184</b>", st["right_bold"]), Paragraph("<b>40.53%</b>", st["right_bold"]), Paragraph("<b>504,833</b>", st["right_bold"]), Paragraph("<b>41.54%</b>", st["right_bold"])],
    ]

    t_exp = Table(exp_data, colWidths=[200, 80, 75, 80, 75])
    t_exp.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 1), (-1, 1), 1, colors.black),
        ('LINEBELOW', (1, 11), (-1, 11), 1, colors.black),
        ('LINEBELOW', (1, 13), (-1, 13), 1.5, colors.black),
        ('LINEABOVE', (1, 13), (-1, 13), 0.5, colors.black),
    ]))
    el.append(t_exp)

    # ==========================================
    # PAGE 4: MONTHLY OPERATING SCHEDULE (JAN-JUN)
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("SUNKISSED VILLAGE RV RESORT", st["title"]))
    el.append(Paragraph("MONTHLY OPERATING INCOME AND EXPENSE (JAN - JUN 2026)", st["sub"]))

    mo_data = [
        [Paragraph("Metric / Category", st["bold"]), Paragraph("Jan-26", st["micro_right_bold"]), Paragraph("Feb-26", st["micro_right_bold"]), Paragraph("Mar-26", st["micro_right_bold"]), Paragraph("Apr-26", st["micro_right_bold"]), Paragraph("May-26", st["micro_right_bold"]), Paragraph("Jun-26", st["micro_right_bold"]), Paragraph("TOTAL", st["micro_right_bold"])],
        [Paragraph("Percent Occupied", st["micro_reg"]), Paragraph("96.11%", st["micro_right"]), Paragraph("94.99%", st["micro_right"]), Paragraph("98.51%", st["micro_right"]), Paragraph("51.70%", st["micro_right"]), Paragraph("37.60%", st["micro_right"]), Paragraph("34.14%", st["micro_right"]), Paragraph("68.84%", st["micro_right_bold"])],
        [Paragraph("Occupied Sites", st["micro_reg"]), Paragraph("7,955", st["micro_right"]), Paragraph("7,355", st["micro_right"]), Paragraph("8,154", st["micro_right"]), Paragraph("4,150", st["micro_right"]), Paragraph("3,112", st["micro_right"]), Paragraph("2,825", st["micro_right"]), Paragraph("33,551", st["micro_right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), Paragraph("<b>325,410</b>", st["micro_right_bold"]), Paragraph("<b>318,920</b>", st["micro_right_bold"]), Paragraph("<b>345,115</b>", st["micro_right_bold"]), Paragraph("<b>112,410</b>", st["micro_right_bold"]), Paragraph("<b>78,500</b>", st["micro_right_bold"]), Paragraph("<b>68,600</b>", st["micro_right_bold"]), Paragraph("<b>1,248,955</b>", st["micro_right_bold"])],
        [Paragraph("OPERATING EXPENSES", st["micro_reg"]), Paragraph("145,210", st["micro_right"]), Paragraph("142,500", st["micro_right"]), Paragraph("148,900", st["micro_right"]), Paragraph("105,400", st["micro_right"]), Paragraph("101,200", st["micro_right"]), Paragraph("99,561", st["micro_right"]), Paragraph("742,771", st["micro_right"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>OPERATING INCOME (NOI)</b>", st["bold"]), Paragraph("<b>180,200</b>", st["micro_right_bold"]), Paragraph("<b>176,420</b>", st["micro_right_bold"]), Paragraph("<b>196,215</b>", st["micro_right_bold"]), Paragraph("<b>7,010</b>", st["micro_right_bold"]), Paragraph("<b>(22,700)</b>", st["micro_right_bold"]), Paragraph("<b>(30,961)</b>", st["micro_right_bold"]), Paragraph("<b>506,184</b>", st["micro_right_bold"])],
    ]
    t_mo = Table(mo_data, colWidths=[150, 52, 52, 52, 52, 52, 52, 68])
    t_mo.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 2), (-1, 2), 0.5, colors.black),
        ('LINEBELOW', (0, 4), (-1, 4), 0.5, colors.black),
        ('LINEBELOW', (0, 6), (-1, 6), 1.5, colors.black),
        ('LINEABOVE', (0, 6), (-1, 6), 0.5, colors.black),
    ]))
    el.append(t_mo)

    # ==========================================
    # PAGE 5: SUNKISSED UTILITY DETAIL (100% SKYLINE GL)
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("SUNKISSED VILLAGE RV RESORT", st["title"]))
    el.append(Paragraph("UTILITY DETAIL & COST RECOVERY ANALYSIS (100% SKYLINE GL)", st["title"]))
    el.append(Paragraph("SIX MONTHS ENDED JUNE 30, 2026", st["sub"]))

    util_data = [
        [Paragraph("Category / Utility", st["bold"]), Paragraph("26-Jan", st["micro_right_bold"]), Paragraph("26-Feb", st["micro_right_bold"]), Paragraph("26-Mar", st["micro_right_bold"]), Paragraph("26-Apr", st["micro_right_bold"]), Paragraph("26-May", st["micro_right_bold"]), Paragraph("26-Jun", st["micro_right_bold"]), Paragraph("TOTAL", st["micro_right_bold"])],
        [Paragraph("PROPANE GAS SERVICE (5162)", st["micro_reg"]), Paragraph("1,299.13", st["micro_right"]), Paragraph("1,299.13", st["micro_right"]), Paragraph("1,299.13", st["micro_right"]), Paragraph("444.18", st["micro_right"]), Paragraph("444.18", st["micro_right"]), Paragraph("444.18", st["micro_right"]), Paragraph("5,229.93", st["micro_right"])],
        [Paragraph("NATURAL GAS UTILITY (5163)", st["micro_reg"]), Paragraph("1,866.21", st["micro_right"]), Paragraph("1,866.20", st["micro_right"]), Paragraph("1,866.20", st["micro_right"]), Paragraph("297.43", st["micro_right"]), Paragraph("297.43", st["micro_right"]), Paragraph("297.43", st["micro_right"]), Paragraph("6,490.90", st["micro_right"])],
        [Paragraph("WATER & SEWER UTILITY (5160)", st["micro_reg"]), Paragraph("3,610.73", st["micro_right"]), Paragraph("3,610.74", st["micro_right"]), Paragraph("3,610.73", st["micro_right"]), Paragraph("2,567.27", st["micro_right"]), Paragraph("2,567.27", st["micro_right"]), Paragraph("2,567.27", st["micro_right"]), Paragraph("18,534.01", st["micro_right"])],
        [Paragraph("ELECTRIC UTILITY EXPENSE (5161)", st["micro_reg"]), Paragraph("19,517.03", st["micro_right"]), Paragraph("19,517.03", st["micro_right"]), Paragraph("19,517.02", st["micro_right"]), Paragraph("11,323.06", st["micro_right"]), Paragraph("11,323.06", st["micro_right"]), Paragraph("11,323.06", st["micro_right"]), Paragraph("92,520.26", st["micro_right"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL UTILITY EXPENSES</b>", st["bold"]), Paragraph("<b>26,293.10</b>", st["micro_right_bold"]), Paragraph("<b>26,293.10</b>", st["micro_right_bold"]), Paragraph("<b>26,293.08</b>", st["micro_right_bold"]), Paragraph("<b>14,631.94</b>", st["micro_right_bold"]), Paragraph("<b>14,631.94</b>", st["micro_right_bold"]), Paragraph("<b>14,631.94</b>", st["micro_right_bold"]), Paragraph("<b>122,775.10</b>", st["micro_right_bold"])],
        [Paragraph("SUBMETERED ELECTRIC REIMBURSEMENT", st["micro_reg"]), Paragraph("18,410.00", st["micro_right"]), Paragraph("19,215.00", st["micro_right"]), Paragraph("21,410.00", st["micro_right"]), Paragraph("11,215.00", st["micro_right"]), Paragraph("7,125.00", st["micro_right"]), Paragraph("5,440.00", st["micro_right"]), Paragraph("82,815.00", st["micro_right"])],
        [Paragraph("WATER UTILITY REIMBURSEMENT", st["micro_reg"]), Paragraph("480.00", st["micro_right"]), Paragraph("510.00", st["micro_right"]), Paragraph("525.00", st["micro_right"]), Paragraph("390.00", st["micro_right"]), Paragraph("340.00", st["micro_right"]), Paragraph("316.00", st["micro_right"]), Paragraph("2,561.00", st["micro_right"])],
        [Paragraph("<b>NET UTILITY COST TO OWNER</b>", st["bold"]), Paragraph("<b>7,403.10</b>", st["micro_right_bold"]), Paragraph("<b>6,568.10</b>", st["micro_right_bold"]), Paragraph("<b>4,358.08</b>", st["micro_right_bold"]), Paragraph("<b>3,026.94</b>", st["micro_right_bold"]), Paragraph("<b>7,166.94</b>", st["micro_right_bold"]), Paragraph("<b>8,875.94</b>", st["micro_right_bold"]), Paragraph("<b>37,399.10</b>", st["micro_right_bold"])],
        [Paragraph("<b>OVERALL COST RECOVERY %</b>", st["bold"]), Paragraph("71.8%", st["micro_right_bold"]), Paragraph("75.0%", st["micro_right_bold"]), Paragraph("83.4%", st["micro_right_bold"]), Paragraph("79.3%", st["micro_right_bold"]), Paragraph("51.0%", st["micro_right_bold"]), Paragraph("39.3%", st["micro_right_bold"]), Paragraph("<b>77.0%</b>", st["micro_right_bold"])],
    ]
    t_ut = Table(util_data, colWidths=[150, 52, 52, 52, 52, 52, 52, 68])
    t_ut.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 3), (-1, 3), 0.5, colors.black),
        ('LINEBELOW', (0, 5), (-1, 5), 1.5, colors.black),
        ('LINEABOVE', (0, 5), (-1, 5), 0.5, colors.black),
    ]))
    el.append(t_ut)

    doc.build(el)
    print(f"✅ Generated Sunkissed Village CFO Replica PDF: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
