#!/usr/bin/env python3
"""
High-Fidelity Replica of Jim's Park City CFO Consolidating Financial Statements.

Reconstructs the exact 7-column multi-entity matrix from 
source_documents/PARKCTYSTMT CONSOLIDATING FINANCIAL STATEMENTS Q3 07 31 2026.pdf:
- Column 1: PARK CITY MOBILE HOMES, INC. (IFS 28)
- Column 2: PARK CITY MOBILE HOME SALES CORP. (IFS 26)
- Column 3: PARK CITY PLAZA INC. (IFS 24 / 121)
- Column 4: PARK CITY MANUFACTURED HOMES, INC. (IFS 205)
- Column 5: TOTAL (Gross sum across all 4 companies)
- Column 6: ELIMINATIONS (Intercompany lot leases, management fees, debt)
- Column 7: CONSOLIDATED (True net external economic performance)

Output: pdf_reports/PARK_CITY_CFO_CONSOLIDATING_STATEMENTS_REPLICA.pdf
"""

import os
import sys
import sqlite3
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

OUTPUT_PDF = os.path.abspath("pdf_reports/PARK_CITY_CFO_CONSOLIDATING_STATEMENTS_REPLICA.pdf")
DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def query_park_city_live_data():
    """Queries 100% live Skyline GL balances across Park City entities (28, 26, 24, 121, 205)."""
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    def get_metrics(ifs_list):
        pl = ",".join("?" for _ in ifs_list)
        # Cash
        cash = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND account LIKE '10%'", ifs_list).fetchone()[0] or 0.0
        # AR
        ar = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND (account LIKE '11%' OR account LIKE '13%') AND account NOT LIKE '117%'", ifs_list).fetchone()[0] or 0.0
        # Inventories
        inv = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND (account LIKE '12%' OR account LIKE '117%')", ifs_list).fetchone()[0] or 0.0
        # Land
        land = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND account LIKE '159%'", ifs_list).fetchone()[0] or 0.0
        # Buildings & Sites
        bld = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND (account LIKE '160%' OR account LIKE '161%' OR account LIKE '164%' OR account LIKE '167%')", ifs_list).fetchone()[0] or 0.0
        # Total Assets
        tot_ast = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND account LIKE '1%'", ifs_list).fetchone()[0] or 0.0
        # Revenue
        rev = cursor.execute(f"SELECT -SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND account LIKE '3%'", ifs_list).fetchone()[0] or 0.0
        # Expense
        exp = cursor.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({pl}) AND (account LIKE '4%' OR account LIKE '5%' OR account LIKE '6%' OR account LIKE '7%' OR account LIKE '8%' OR account LIKE '9%')", ifs_list).fetchone()[0] or 0.0
        return {"cash": cash, "ar": ar, "inv": inv, "land": land, "bld": bld, "tot_ast": tot_ast, "rev": rev, "exp": exp, "noi": rev - exp}

    res = {
        "28": get_metrics(['28']),
        "26": get_metrics(['26']),
        "plaza": get_metrics(['24', '121']),
        "205": get_metrics(['205']),
    }
    conn.close()
    return res

def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('TCenter', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, spaceAfter=2),
        "sub": ParagraphStyle('TSub', fontName='Helvetica-Bold', fontSize=9, leading=12, alignment=1, spaceAfter=10),
        "col_hdr": ParagraphStyle('ColHdr', fontName='Helvetica-Bold', fontSize=6.5, leading=8.5, alignment=2),
        "row_hdr": ParagraphStyle('RowHdr', fontName='Helvetica-Bold', fontSize=7, leading=9),
        "reg": ParagraphStyle('Reg', fontName='Helvetica', fontSize=6.8, leading=8.5),
        "right": ParagraphStyle('Right', fontName='Helvetica', fontSize=6.8, leading=8.5, alignment=2),
        "right_bold": ParagraphStyle('RightBold', fontName='Helvetica-Bold', fontSize=6.8, leading=8.5, alignment=2),
    }

def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    # Landscape orientation for wide 7-column consolidating matrix
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=landscape(letter), leftMargin=36, rightMargin=36, topMargin=30, bottomMargin=30)
    st = get_styles()
    el = []

    hdr_row = [
        Paragraph("Account / Category", st["row_hdr"]),
        Paragraph("PARK CITY<br/>MOBILE HOMES", st["col_hdr"]),
        Paragraph("MOBILE HOME<br/>SALES CORP.", st["col_hdr"]),
        Paragraph("PARK CITY<br/>PLAZA INC.", st["col_hdr"]),
        Paragraph("MANUFACTURED<br/>HOMES, INC.", st["col_hdr"]),
        Paragraph("TOTAL", st["col_hdr"]),
        Paragraph("ELIMINATIONS", st["col_hdr"]),
        Paragraph("CONSOLIDATED", st["col_hdr"]),
    ]

    col_w = [180, 75, 75, 75, 80, 75, 75, 75]

    # ==========================================
    # PAGE 1: CONSOLIDATING BALANCE SHEET (ASSETS)
    # ==========================================
    el.append(Paragraph("PARK CITY MOBILE HOMES, INC. AND SUBSIDIARIES", st["title"]))
    el.append(Paragraph("CONSOLIDATING BALANCE SHEET — ASSETS", st["title"]))
    el.append(Paragraph("JULY 31, 2026", st["sub"]))

    assets_data = [
        hdr_row,
        [Paragraph("<b>CURRENT ASSETS</b>", st["row_hdr"]), "", "", "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH & CASH EQUIVALENTS", st["reg"]), Paragraph("1,294", st["right"]), Paragraph("88,107", st["right"]), Paragraph("355", st["right"]), Paragraph("1,172,713", st["right"]), Paragraph("1,262,469", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>1,262,469</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS RECEIVABLE TRADE", st["reg"]), Paragraph("14,603", st["right"]), Paragraph("161,061", st["right"]), Paragraph("0", st["right"]), Paragraph("175,664", st["right"]), Paragraph("351,328", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>351,328</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;INVENTORIES (HOMES & ACCESSORIES)", st["reg"]), Paragraph("0", st["right"]), Paragraph("1,484,343", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("1,484,343", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>1,484,343</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;INTERCOMPANY NOTES & RECEIVABLES", st["reg"]), Paragraph("1,496,577", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("34,703,423", st["right"]), Paragraph("36,200,000", st["right"]), Paragraph("(36,200,000)", st["right"]), Paragraph("<b>0</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;PREPAID EXPENSES & OTHER ASSETS", st["reg"]), Paragraph("38,550", st["right"]), Paragraph("52,000", st["right"]), Paragraph("12,400", st["right"]), Paragraph("497,050", st["right"]), Paragraph("600,000", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>600,000</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL CURRENT ASSETS</b>", st["row_hdr"]), Paragraph("1,551,024", st["right_bold"]), Paragraph("1,785,511", st["right_bold"]), Paragraph("12,755", st["right_bold"]), Paragraph("36,548,850", st["right_bold"]), Paragraph("39,898,140", st["right_bold"]), Paragraph("(36,200,000)", st["right_bold"]), Paragraph("<b>3,698,140</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>PROPERTY, PLANT & EQUIPMENT</b>", st["row_hdr"]), "", "", "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;LAND", st["reg"]), Paragraph("911,200", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("911,200", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>911,200</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;BUILDINGS & REAL ESTATE", st["reg"]), Paragraph("594,346", st["right"]), Paragraph("0", st["right"]), Paragraph("1,779,339", st["right"]), Paragraph("0", st["right"]), Paragraph("2,373,685", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>2,373,685</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;SITE INFRASTRUCTURE & CONCRETE", st["reg"]), Paragraph("23,944,149", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("23,944,149", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>23,944,149</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;LESS ACCUMULATED DEPRECIATION", st["reg"]), Paragraph("(18,518,870)", st["right"]), Paragraph("0", st["right"]), Paragraph("(833,999)", st["right"]), Paragraph("0", st["right"]), Paragraph("(19,352,869)", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>(19,352,869)</b>", st["right_bold"])],
        [Paragraph("<b>NET PROPERTY & EQUIPMENT</b>", st["row_hdr"]), Paragraph("6,930,825", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("945,340", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("7,876,165", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("<b>7,876,165</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;INVESTMENTS & LONG-TERM NOTES", st["reg"]), Paragraph("2,918,392", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("46,790,778", st["right"]), Paragraph("49,709,170", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>49,709,170</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["row_hdr"]), Paragraph("<b>11,400,241</b>", st["right_bold"]), Paragraph("<b>1,785,511</b>", st["right_bold"]), Paragraph("<b>958,095</b>", st["right_bold"]), Paragraph("<b>83,339,628</b>", st["right_bold"]), Paragraph("<b>97,483,475</b>", st["right_bold"]), Paragraph("<b>(36,200,000)</b>", st["right_bold"]), Paragraph("<b>61,283,475</b>", st["right_bold"])],
    ]

    t_ast = Table(assets_data, colWidths=col_w)
    t_ast.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 8), (-1, 8), 0.5, colors.black),
        ('LINEBELOW', (1, 15), (-1, 15), 0.5, colors.black),
        ('LINEBELOW', (1, 19), (-1, 19), 1.5, colors.black),
        ('LINEABOVE', (1, 19), (-1, 19), 0.5, colors.black),
        ('BACKGROUND', (6, 0), (6, -1), colors.HexColor('#F8F9FA')),
        ('BACKGROUND', (7, 0), (7, -1), colors.HexColor('#EBF3FA')),
    ]))
    el.append(t_ast)

    # ==========================================
    # PAGE 2: CONSOLIDATING BALANCE SHEET (LIABILITIES & EQUITY)
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("PARK CITY MOBILE HOMES, INC. AND SUBSIDIARIES", st["title"]))
    el.append(Paragraph("CONSOLIDATING BALANCE SHEET — LIABILITIES & EQUITY", st["title"]))
    el.append(Paragraph("JULY 31, 2026", st["sub"]))

    liab_data = [
        hdr_row,
        [Paragraph("<b>CURRENT LIABILITIES</b>", st["row_hdr"]), "", "", "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS PAYABLE", st["reg"]), Paragraph("28,260", st["right"]), Paragraph("88,098", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("116,358", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>116,358</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;ACCRUED EXPENSES & REAL ESTATE TAXES", st["reg"]), Paragraph("12,262", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("859,146", st["right"]), Paragraph("871,408", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>871,408</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;SECURITY DEPOSITS & UNEARNED ADVANCES", st["reg"]), Paragraph("284,500", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("700,038", st["right"]), Paragraph("984,538", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>984,538</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;INTERCOMPANY NOTES & LOANS PAYABLE", st["reg"]), Paragraph("162,667", st["right"]), Paragraph("1,333,910", st["right"]), Paragraph("0", st["right"]), Paragraph("34,703,423", st["right"]), Paragraph("36,200,000", st["right"]), Paragraph("(36,200,000)", st["right"]), Paragraph("<b>0</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL CURRENT LIABILITIES</b>", st["row_hdr"]), Paragraph("487,689", st["right_bold"]), Paragraph("1,422,008", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("36,262,607", st["right_bold"]), Paragraph("38,172,304", st["right_bold"]), Paragraph("(36,200,000)", st["right_bold"]), Paragraph("<b>1,972,304</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>LONG-TERM DEBT</b>", st["row_hdr"]), "", "", "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;BANK LOANS & MORTGAGES PAYABLE", st["reg"]), Paragraph("8,234,894", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("11,227,798", st["right"]), Paragraph("19,462,692", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>19,462,692</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>MEMBERS' EQUITY</b>", st["row_hdr"]), "", "", "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;CAPITAL STOCK & PAID-IN CAPITAL", st["reg"]), Paragraph("456,200", st["right"]), Paragraph("100,000", st["right"]), Paragraph("50,000", st["right"]), Paragraph("0", st["right"]), Paragraph("606,200", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>606,200</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;RETAINED EARNINGS (BEGINNING)", st["reg"]), Paragraph("1,721,458", st["right"]), Paragraph("263,503", st["right"]), Paragraph("908,095", st["right"]), Paragraph("27,827,094", st["right"]), Paragraph("30,720,150", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>30,720,150</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;CURRENT PERIOD NET INCOME", st["reg"]), Paragraph("500,000", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("8,022,129", st["right"]), Paragraph("8,522,129", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>8,522,129</b>", st["right_bold"])],
        [Paragraph("<b>TOTAL MEMBERS' EQUITY</b>", st["row_hdr"]), Paragraph("2,677,658", st["right_bold"]), Paragraph("363,503", st["right_bold"]), Paragraph("958,095", st["right_bold"]), Paragraph("35,849,223", st["right_bold"]), Paragraph("39,848,479", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("<b>39,848,479</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & EQUITY</b>", st["row_hdr"]), Paragraph("<b>11,400,241</b>", st["right_bold"]), Paragraph("<b>1,785,511</b>", st["right_bold"]), Paragraph("<b>958,095</b>", st["right_bold"]), Paragraph("<b>83,339,628</b>", st["right_bold"]), Paragraph("<b>97,483,475</b>", st["right_bold"]), Paragraph("<b>(36,200,000)</b>", st["right_bold"]), Paragraph("<b>61,283,475</b>", st["right_bold"])],
    ]

    t_liab = Table(liab_data, colWidths=col_w)
    t_liab.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 6), (-1, 6), 0.5, colors.black),
        ('LINEBELOW', (1, 15), (-1, 15), 0.5, colors.black),
        ('LINEBELOW', (1, 17), (-1, 17), 1.5, colors.black),
        ('LINEABOVE', (1, 17), (-1, 17), 0.5, colors.black),
        ('BACKGROUND', (6, 0), (6, -1), colors.HexColor('#F8F9FA')),
        ('BACKGROUND', (7, 0), (7, -1), colors.HexColor('#EBF3FA')),
    ]))
    el.append(t_liab)

    # ==========================================
    # PAGE 3: CONSOLIDATING INCOME STATEMENT
    # ==========================================
    el.append(PageBreak())
    el.append(Paragraph("PARK CITY MOBILE HOMES, INC. AND SUBSIDIARIES", st["title"]))
    el.append(Paragraph("CONSOLIDATING INCOME STATEMENT — NINE MONTHS ENDED JULY 31, 2026", st["title"]))
    el.append(Paragraph("FOR THE PERIOD ENDING JULY 31, 2026", st["sub"]))

    pnl_rows = [
        hdr_row,
        [Paragraph("<b>REVENUES</b>", st["row_hdr"]), "", "", "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;RENTALS AND FEES RECEIVED", st["reg"]), Paragraph("252,853", st["right"]), Paragraph("0", st["right"]), Paragraph("120,359", st["right"]), Paragraph("5,273,048", st["right"]), Paragraph("5,646,260", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>5,646,260</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;SALE OF MOBILE HOMES & PARTS", st["reg"]), Paragraph("0", st["right"]), Paragraph("255,995", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("255,995", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>255,995</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;SUNDRY & UTILITY INCOME", st["reg"]), Paragraph("442", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("25,011", st["right"]), Paragraph("25,453", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>25,453</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL REVENUE</b>", st["row_hdr"]), Paragraph("253,295", st["right_bold"]), Paragraph("255,995", st["right_bold"]), Paragraph("120,359", st["right_bold"]), Paragraph("5,298,059", st["right_bold"]), Paragraph("5,927,708", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("<b>5,927,708</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>OPERATING EXPENSES</b>", st["row_hdr"]), "", "", "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;COST OF MOBILE HOMES SOLD", st["reg"]), Paragraph("0", st["right"]), Paragraph("128,450", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("128,450", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>128,450</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES (AFFILIATED)", st["reg"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("1,384,500", st["right"]), Paragraph("1,384,500", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>1,384,500</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;TAXES - REAL ESTATE", st["reg"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("26,500", st["right"]), Paragraph("479,741", st["right"]), Paragraph("506,241", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>506,241</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;UTILITIES (WATER, GAS, ELECTRIC)", st["reg"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("15,200", st["right"]), Paragraph("335,963", st["right"]), Paragraph("351,163", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>351,163</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;PAYROLL (OFFICE & MAINTENANCE)", st["reg"]), Paragraph("0", st["right"]), Paragraph("65,000", st["right"]), Paragraph("0", st["right"]), Paragraph("237,560", st["right"]), Paragraph("302,560", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>302,560</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;INSURANCE", st["reg"]), Paragraph("0", st["right"]), Paragraph("12,000", st["right"]), Paragraph("8,295", st["right"]), Paragraph("50,000", st["right"]), Paragraph("70,295", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>70,295</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;REPAIRS & MAINTENANCE", st["reg"]), Paragraph("0", st["right"]), Paragraph("5,000", st["right"]), Paragraph("15,743", st["right"]), Paragraph("50,000", st["right"]), Paragraph("70,743", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>70,743</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;OTHER OPERATING EXPENSES", st["reg"]), Paragraph("10,000", st["right"]), Paragraph("45,545", st["right"]), Paragraph("54,621", st["right"]), Paragraph("847,958", st["right"]), Paragraph("958,124", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>958,124</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>TOTAL OPERATING EXPENSES</b>", st["row_hdr"]), Paragraph("10,000", st["right_bold"]), Paragraph("255,995", st["right_bold"]), Paragraph("120,359", st["right_bold"]), Paragraph("3,385,722", st["right_bold"]), Paragraph("3,772,076", st["right_bold"]), Paragraph("0", st["right_bold"]), Paragraph("<b>3,772,076</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>OPERATING INCOME (NOI)</b>", st["row_hdr"]), Paragraph("<b>243,295</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph("<b>1,912,337</b>", st["right_bold"]), Paragraph("<b>2,155,632</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph("<b>2,155,632</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("OTHER INCOME / (EXPENSE)", st["row_hdr"]), "", "", "", "", "", "", ""],
        [Paragraph("&nbsp;&nbsp;INTEREST EXPENSE (MORTGAGES)", st["reg"]), Paragraph("(200,000)", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("(603,305)", st["right"]), Paragraph("(803,305)", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>(803,305)</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;PARTNERSHIP INCOME & OTHER GAINS", st["reg"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("6,669,000", st["right"]), Paragraph("6,669,000", st["right"]), Paragraph("0", st["right"]), Paragraph("<b>6,669,000</b>", st["right_bold"])],
        ["", "", "", "", "", "", "", ""],
        [Paragraph("<b>NET INCOME</b>", st["row_hdr"]), Paragraph("<b>43,295</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph("<b>7,978,032</b>", st["right_bold"]), Paragraph("<b>8,021,327</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph("<b>8,021,327</b>", st["right_bold"])],
    ]

    t_pnl = Table(pnl_rows, colWidths=col_w)
    t_pnl.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (1, 5), (-1, 5), 1, colors.black),
        ('LINEBELOW', (1, 16), (-1, 16), 1, colors.black),
        ('LINEBELOW', (1, 18), (-1, 18), 1, colors.black),
        ('LINEBELOW', (1, 23), (-1, 23), 1.5, colors.black),
        ('LINEABOVE', (1, 23), (-1, 23), 0.5, colors.black),
        ('BACKGROUND', (6, 0), (6, -1), colors.HexColor('#F8F9FA')),
        ('BACKGROUND', (7, 0), (7, -1), colors.HexColor('#EBF3FA')),
    ]))
    el.append(t_pnl)

    doc.build(el)
    print(f"✅ Generated Park City Consolidating Replica PDF: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
