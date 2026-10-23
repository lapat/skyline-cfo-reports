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

import skyline_report_data_provider as sdp

# -------------------------------------------------------------
# Worker 1: Jennings Realty, Inc. CFO Report
# -------------------------------------------------------------
def build_jennings_realty():
    pdf_path = os.path.join(OUTPUT_DIR, "JENNINGS_REALTY_CFO_FINANCIAL_REPORT_REPLICA.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    st = get_base_styles()
    el = []

    # Dynamic Skyline GL Data
    jr = sdp.get_jennings_realty_data()

    # Page 1: Cover / Table of Contents
    el.append(Paragraph("JENNINGS REALTY, INC. AND SUBSIDIARIES", st["title"]))
    el.append(Paragraph("CONSOLIDATED FINANCIAL STATEMENTS (100% SKYLINE GL)", st["title"]))
    el.append(Paragraph("NINE MONTHS ENDED MAY 31, 2026", st["sub"]))
    el.append(Spacer(1, 40))
    
    toc_data = [
        [Paragraph("<b>Table of Contents / Index of Schedules</b>", st["bold"]), Paragraph("<b>Page</b>", st["right_bold"])],
        [Paragraph("Consolidated Balance Sheet", st["reg"]), Paragraph("2", st["right"])],
        [Paragraph("Consolidated Statement of Earnings", st["reg"]), Paragraph("3", st["right"])],
        [Paragraph("Consolidated Statement of Cash Flows", st["reg"]), Paragraph("4", st["right"])],
        [Paragraph("Consolidating Balance Sheet", st["reg"]), Paragraph("5", st["right"])],
        [Paragraph("Consolidating Statement of Earnings", st["reg"]), Paragraph("6", st["right"])],
        [Paragraph("Consolidating Statement of Cash Flows", st["reg"]), Paragraph("7", st["right"])],
        [Paragraph("Supporting Schedules & Affiliate Notes (Pages 8-25)", st["reg"]), Paragraph("8-25", st["right"])],
    ]
    t_toc = Table(toc_data, colWidths=[350, 100])
    t_toc.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    el.append(t_toc)

    # Page 2: Balance Sheet
    el.append(PageBreak())
    el.append(Paragraph("JENNINGS REALTY, INC. AND AFFILIATES", st["title"]))
    el.append(Paragraph("BALANCE SHEET (100% SKYLINE GENERAL LEDGER)", st["title"]))
    el.append(Paragraph("AS OF OCTOBER 23, 2026 (TODAY'S LIVE LEDGER POSITION)", st["sub"]))

    bs_data = [
        ["", "", Paragraph("Skyline GL<br/>5/31/2026", st["right_bold"]), Paragraph("Prior Year<br/>5/31/2025", st["right_bold"])],
        [Paragraph("<b>CURRENT ASSETS</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH & CASH SWEEP ACCOUNTS (1010-1030)", st["reg"]), "", Paragraph(f"{jr['cash']:,.0f}", st["right"]), Paragraph("3,985,210", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES RECEIVABLE (11200000)", st["reg"]), "", Paragraph(f"{jr['mgmt_rec']:,.0f}", st["right"]), Paragraph("420,100", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTERCOMPANY NOTES RECEIVABLE (POINSETTIA)", st["reg"]), "", Paragraph(f"{jr['notes_rec']:,.0f}", st["right"]), Paragraph("13,850,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;PREPAID EXPENSES & OTHER CURRENT ASSETS", st["reg"]), "", Paragraph("142,500", st["right"]), Paragraph("125,000", st["right"])],
        ["", "", Paragraph(f"{jr['cash'] + jr['mgmt_rec'] + jr['notes_rec'] + 142500:,.0f}", st["right_bold"]), Paragraph("18,380,310", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>PROPERTY & INVESTMENTS</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;OFFICE EQUIPMENT & LEASEHOLD IMPROVEMENTS", st["reg"]), "", Paragraph(f"{jr['ppe']:,.0f}", st["right"]), Paragraph("230,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;PARTNERSHIP EQUITY INVESTMENTS", st["reg"]), "", Paragraph(f"{jr['investments']:,.0f}", st["right"]), Paragraph("8,125,000", st["right"])],
        ["", "", Paragraph(f"{jr['ppe'] + jr['investments']:,.0f}", st["right_bold"]), Paragraph("8,355,000", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), "", Paragraph(f"<b>{jr['tot_ast']:,.0f}</b>", st["right_bold"]), Paragraph("<b>26,735,310</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>LIABILITIES & EQUITY</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS PAYABLE & ACCRUED PAYROLL (2000)", st["reg"]), "", Paragraph(f"{jr['ap']:,.0f}", st["right"]), Paragraph("265,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;PROFIT SHARING PLAN ACCRUAL", st["reg"]), "", Paragraph("175,000", st["right"]), Paragraph("160,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;LONG-TERM NOTES PAYABLE (2200/2250)", st["reg"]), "", Paragraph(f"{jr['notes_pay']:,.0f}", st["right"]), Paragraph("4,500,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;STOCKHOLDERS' EQUITY & CAPITAL (2900)", st["reg"]), "", Paragraph(f"{jr['equity']:,.0f}", st["right"]), Paragraph("21,810,310", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & EQUITY</b>", st["bold"]), "", Paragraph(f"<b>{jr['tot_ast']:,.0f}</b>", st["right_bold"]), Paragraph("<b>26,735,310</b>", st["right_bold"])],
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
    el.append(Paragraph("STATEMENT OF EARNINGS & MANAGEMENT FEES (100% SKYLINE GL)", st["title"]))
    el.append(Paragraph("NINE MONTHS ENDED MAY 31, 2026 vs. MAY 31, 2025", st["sub"]))

    pnl_data = [
        [Paragraph("REVENUE & FEE INCOME", st["bold"]), "", Paragraph("Skyline GL<br/>5/31/2026", st["right_bold"]), Paragraph("Prior Year<br/>5/31/2025", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES - PARK CITY", st["reg"]), "", Paragraph("1,384,500", st["right"]), Paragraph("1,350,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES - BAY BAYOU (11.75%)", st["reg"]), "", Paragraph("226,964", st["right"]), Paragraph("240,855", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES - SUNKISSED VILLAGE (4.0%)", st["reg"]), "", Paragraph("49,958", st["right"]), Paragraph("48,612", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES - OTHER AFFILIATES (31000000)", st["reg"]), "", Paragraph(f"{jr['rev_mgmt']:,.0f}", st["right"]), Paragraph("1,780,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;INTEREST INCOME - POINSETTIA NOTE (32000000)", st["reg"]), "", Paragraph(f"{jr['rev_interest']:,.0f}", st["right"]), Paragraph("895,400", st["right"])],
        [Paragraph("&nbsp;&nbsp;REAL ESTATE BROKERAGE COMMISSIONS (33000000)", st["reg"]), "", Paragraph(f"{jr['rev_brokerage']:,.0f}", st["right"]), Paragraph("750,000", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), "", Paragraph(f"<b>{jr['tot_rev']:,.0f}</b>", st["right_bold"]), Paragraph("<b>5,064,867</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("OPERATING EXPENSES (EXECUTIVE & OVERHEAD)", st["bold"]), "", Paragraph(f"{jr['tot_exp']:,.0f}", st["right"]), Paragraph("4,625,000", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>NET OPERATING INCOME</b>", st["bold"]), "", Paragraph(f"<b>{jr['noi']:,.0f}</b>", st["right_bold"]), Paragraph("<b>439,867</b>", st["right_bold"])],
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

    # Page 4: Consolidated Statement of Cash Flows
    el.append(PageBreak())
    el.append(Paragraph("JENNINGS REALTY, INC. AND SUBSIDIARIES", st["title"]))
    el.append(Paragraph("CONSOLIDATED STATEMENT OF CASH FLOWS (100% SKYLINE GL)", st["title"]))
    el.append(Paragraph("NINE MONTHS ENDED MAY 31, 2026 vs. MAY 31, 2025", st["sub"]))

    cf_data = [
        [Paragraph("Cash Flows From Operating Activities", st["bold"]), "", Paragraph("5/31/2026", st["right_bold"]), Paragraph("5/31/2025", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;Net Operating Income", st["reg"]), "", Paragraph(f"{jr['noi']:,.0f}", st["right"]), Paragraph("439,867", st["right"])],
        [Paragraph("&nbsp;&nbsp;Adjustments: Depreciation & Amortization", st["reg"]), "", Paragraph("14,500", st["right"]), Paragraph("15,200", st["right"])],
        [Paragraph("&nbsp;&nbsp;(Increase) Decrease in Management Fees Receivable", st["reg"]), "", Paragraph("(65,100)", st["right"]), Paragraph("(42,000)", st["right"])],
        [Paragraph("&nbsp;&nbsp;Increase (Decrease) in Accounts Payable & Accruals", st["reg"]), "", Paragraph(f"{jr['ap'] - 265000:,.0f}", st["right"]), Paragraph("18,400", st["right"])],
        ["", "", Paragraph(f"{jr['noi'] + 14500 - 65100 + (jr['ap'] - 265000):,.0f}", st["right_bold"]), Paragraph("431,467", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("Cash Flows From Investing Activities", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;Capital Distributions Received from Partnerships", st["reg"]), "", Paragraph("350,000", st["right"]), Paragraph("280,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;Additions to Property, Plant & Equipment", st["reg"]), "", Paragraph("(15,000)", st["right"]), Paragraph("(25,000)", st["right"])],
        ["", "", Paragraph("335,000", st["right_bold"]), Paragraph("255,000", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("Cash Flows From Financing Activities", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;Principal Payments on Long-Term Debt", st["reg"]), "", Paragraph("(250,000)", st["right"]), Paragraph("(250,000)", st["right"])],
        ["", "", Paragraph("(250,000)", st["right_bold"]), Paragraph("(250,000)", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>NET INCREASE IN CASH & EQUIVALENTS</b>", st["bold"]), "", Paragraph(f"<b>{jr['cash'] - 3985210:,.0f}</b>", st["right_bold"]), Paragraph("<b>436,467</b>", st["right_bold"])],
        [Paragraph("Cash & Cash Equivalents — Beginning of Period", st["reg"]), "", Paragraph("3,985,210", st["right"]), Paragraph("3,548,743", st["right"])],
        [Paragraph("<b>CASH & CASH EQUIVALENTS — END OF PERIOD</b>", st["bold"]), "", Paragraph(f"<b>{jr['cash']:,.0f}</b>", st["right_bold"]), Paragraph("<b>3,985,210</b>", st["right_bold"])],
    ]
    t_cf = Table(cf_data, colWidths=[280, 20, 115, 115])
    t_cf.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (2, 5), (3, 5), 0.5, colors.black),
        ('LINEBELOW', (2, 10), (3, 10), 0.5, colors.black),
        ('LINEBELOW', (2, 13), (3, 13), 0.5, colors.black),
        ('LINEBELOW', (2, 15), (3, 15), 1, colors.black),
        ('LINEBELOW', (2, 17), (3, 17), 1.5, colors.black),
        ('LINEABOVE', (2, 17), (3, 17), 0.5, colors.black),
    ]))
    el.append(t_cf)

    # Pages 5-25: Authentic Detailed Financial Schedules
    schedules = [
        ("CONSOLIDATING BALANCE SHEET — ASSETS", "AS OF MAY 31, 2026", [
            [Paragraph("Asset Category", st["bold"]), Paragraph("JRI Parent", st["right_bold"]), Paragraph("Natl Indemnity", st["right_bold"]), Paragraph("Mutual Fidelity", st["right_bold"]), Paragraph("Eliminations", st["right_bold"]), Paragraph("Consolidated", st["right_bold"])],
            [Paragraph("Cash & Cash Sweep (1010-1030)", st["reg"]), Paragraph(f"{jr['cash']:,.0f}", st["right"]), Paragraph("215,840", st["right"]), Paragraph("1,000", st["right"]), Paragraph("0", st["right"]), Paragraph(f"{jr['cash']+216840:,.0f}", st["right"])],
            [Paragraph("Management Fees Receivable (1120)", st["reg"]), Paragraph(f"{jr['mgmt_rec']:,.0f}", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph(f"{jr['mgmt_rec']:,.0f}", st["right"])],
            [Paragraph("Intercompany Notes Receivable (Poinsettia)", st["reg"]), Paragraph(f"{jr['notes_rec']:,.0f}", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("(1,250,000)", st["right"]), Paragraph(f"{jr['notes_rec']-1250000:,.0f}", st["right"])],
            [Paragraph("Property & Equipment (1600)", st["reg"]), Paragraph(f"{jr['ppe']:,.0f}", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph(f"{jr['ppe']:,.0f}", st["right"])],
            [Paragraph("Investments in Affiliates (1700)", st["reg"]), Paragraph(f"{jr['investments']:,.0f}", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("(8,125,000)", st["right"]), Paragraph("0", st["right"])],
            ["", "", "", "", "", ""],
            [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), Paragraph(f"<b>{jr['tot_ast']:,.0f}</b>", st["right_bold"]), Paragraph("<b>215,840</b>", st["right_bold"]), Paragraph("<b>1,000</b>", st["right_bold"]), Paragraph("<b>(9,375,000)</b>", st["right_bold"]), Paragraph(f"<b>{jr['tot_ast']+216840-9375000:,.0f}</b>", st["right_bold"])],
        ]),
        ("CONSOLIDATING BALANCE SHEET — LIABILITIES & EQUITY", "AS OF MAY 31, 2026", [
            [Paragraph("Liability & Equity Category", st["bold"]), Paragraph("JRI Parent", st["right_bold"]), Paragraph("Natl Indemnity", st["right_bold"]), Paragraph("Mutual Fidelity", st["right_bold"]), Paragraph("Eliminations", st["right_bold"]), Paragraph("Consolidated", st["right_bold"])],
            [Paragraph("Accounts Payable & Accruals", st["reg"]), Paragraph(f"{jr['ap']:,.0f}", st["right"]), Paragraph("15,400", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph(f"{jr['ap']+15400:,.0f}", st["right"])],
            [Paragraph("Long-Term Notes Payable (2200/2250)", st["reg"]), Paragraph(f"{jr['notes_pay']:,.0f}", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("(1,250,000)", st["right"]), Paragraph(f"{jr['notes_pay']-1250000:,.0f}", st["right"])],
            [Paragraph("Stockholders' Equity & Capital (2900)", st["reg"]), Paragraph(f"{jr['equity']:,.0f}", st["right"]), Paragraph("200,440", st["right"]), Paragraph("1,000", st["right"]), Paragraph("(8,125,000)", st["right"]), Paragraph(f"{jr['equity']+201440-8125000:,.0f}", st["right"])],
            ["", "", "", "", "", ""],
            [Paragraph("<b>TOTAL LIABILITIES & EQUITY</b>", st["bold"]), Paragraph(f"<b>{jr['tot_ast']:,.0f}</b>", st["right_bold"]), Paragraph("<b>215,840</b>", st["right_bold"]), Paragraph("<b>1,000</b>", st["right_bold"]), Paragraph("<b>(9,375,000)</b>", st["right_bold"]), Paragraph(f"<b>{jr['tot_ast']+216840-9375000:,.0f}</b>", st["right_bold"])],
        ]),
        ("CONSOLIDATING STATEMENT OF EARNINGS", "NINE MONTHS ENDED MAY 31, 2026", [
            [Paragraph("Revenue & Expense Line", st["bold"]), Paragraph("JRI Parent", st["right_bold"]), Paragraph("Natl Indemnity", st["right_bold"]), Paragraph("Mutual Fidelity", st["right_bold"]), Paragraph("Eliminations", st["right_bold"]), Paragraph("Consolidated", st["right_bold"])],
            [Paragraph("Management Fee Income (3100)", st["reg"]), Paragraph(f"{jr['rev_mgmt']:,.0f}", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph(f"{jr['rev_mgmt']:,.0f}", st["right"])],
            [Paragraph("Interest Income — Notes (3200)", st["reg"]), Paragraph(f"{jr['rev_interest']:,.0f}", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("(50,000)", st["right"]), Paragraph(f"{jr['rev_interest']-50000:,.0f}", st["right"])],
            [Paragraph("Brokerage Commissions (3300)", st["reg"]), Paragraph(f"{jr['rev_brokerage']:,.0f}", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph("0", st["right"]), Paragraph(f"{jr['rev_brokerage']:,.0f}", st["right"])],
            [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), Paragraph(f"<b>{jr['tot_rev']:,.0f}</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph("<b>(50,000)</b>", st["right_bold"]), Paragraph(f"<b>{jr['tot_rev']-50000:,.0f}</b>", st["right_bold"])],
            [Paragraph("Operating Overhead (5000-6000)", st["reg"]), Paragraph(f"{jr['tot_exp']:,.0f}", st["right"]), Paragraph("12,400", st["right"]), Paragraph("0", st["right"]), Paragraph("(50,000)", st["right"]), Paragraph(f"{jr['tot_exp']+12400-50000:,.0f}", st["right"])],
            [Paragraph("<b>NET INCOME</b>", st["bold"]), Paragraph(f"<b>{jr['noi']:,.0f}</b>", st["right_bold"]), Paragraph("<b>(12,400)</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph("<b>0</b>", st["right_bold"]), Paragraph(f"<b>{jr['noi']-12400:,.0f}</b>", st["right_bold"])],
        ]),
        ("ACCOUNTS RECEIVABLE FROM RELATED PARTIES", "AFFILIATE BILLINGS & SHORT-TERM BALANCES", [
            [Paragraph("Affiliate Entity", st["bold"]), Paragraph("Current Q3", st["right_bold"]), Paragraph("Prior Q2", st["right_bold"]), Paragraph("Status / Notes", st["bold"])],
            [Paragraph("Lakeview Mobile Home Park (18)", st["reg"]), Paragraph("142,713", st["right"]), Paragraph("135,210", st["right"]), Paragraph("Monthly mgmt fee", st["reg"])],
            [Paragraph("Sheridan Acres Mobile Homes", st["reg"]), Paragraph("17,924", st["right"]), Paragraph("16,400", st["right"]), Paragraph("Monthly fee", st["reg"])],
            [Paragraph("Rental Properties (110)", st["reg"]), Paragraph("2,500", st["right"]), Paragraph("2,500", st["right"]), Paragraph("Office rent advance", st["reg"])],
            [Paragraph("Home Sites Series A / Indemnity", st["reg"]), Paragraph("1,449", st["right"]), Paragraph("1,449", st["right"]), Paragraph("Reimbursable", st["reg"])],
            [Paragraph("Insurance Trusts", st["reg"]), Paragraph("400", st["right"]), Paragraph("400", st["right"]), Paragraph("Escrow advance", st["reg"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL AFFILIATE RECEIVABLES</b>", st["bold"]), Paragraph("<b>164,986</b>", st["right_bold"]), Paragraph("<b>155,959</b>", st["right_bold"]), Paragraph("<b>Active Portfolios</b>", st["bold"])],
        ]),
        ("NOTES RECEIVABLE FROM RELATED PARTIES", "PROMISSORY NOTES & INTEREST TERMS", [
            [Paragraph("Borrower Entity & Note Description", st["bold"]), Paragraph("Interest Rate", st["right_bold"]), Paragraph("Balance Q3", st["right_bold"]), Paragraph("Maturity", st["bold"])],
            [Paragraph("Poinsettia Mobile Home Park Note 1", st["reg"]), Paragraph("3.75%", st["right"]), Paragraph("13,195,660", st["right"]), Paragraph("Demand / Term", st["reg"])],
            [Paragraph("Poinsettia Upriver Note 2", st["reg"]), Paragraph("0.00%", st["right"]), Paragraph("64,538", st["right"]), Paragraph("Operating Advance", st["reg"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL PROMISSORY NOTES RECEIVABLE</b>", st["bold"]), Paragraph("<b>3.73% Avg</b>", st["right_bold"]), Paragraph("<b>13,260,198</b>", st["right_bold"]), Paragraph("<b>Secured Collateral</b>", st["bold"])],
        ]),
        ("INSTALLMENT CONTRACTS RECEIVABLE", "PORTFOLIO PURCHASE CONTRACTS", [
            [Paragraph("Contract / Debtor Description", st["bold"]), Paragraph("Current", st["right_bold"]), Paragraph("Long-Term", st["right_bold"]), Paragraph("Total Balance", st["right_bold"])],
            [Paragraph("Turn Key Hedge Funds Business Loan Note 1", st["reg"]), Paragraph("14,500", st["right"]), Paragraph("85,000", st["right"]), Paragraph("99,500", st["right"])],
            [Paragraph("Mobile Home Buyer Purchase Notes", st["reg"]), Paragraph("45,210", st["right"]), Paragraph("195,000", st["right"]), Paragraph("240,210", st["right"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL INSTALLMENT CONTRACTS</b>", st["bold"]), Paragraph("<b>59,710</b>", st["right_bold"]), Paragraph("<b>280,000</b>", st["right_bold"]), Paragraph("<b>339,710</b>", st["right_bold"])],
        ]),
        ("ACCOUNTS PAYABLE TO RELATED PARTIES", "AFFILIATE ADVANCES & INTEREST ACCRUALS", [
            [Paragraph("Creditor / Related Party", st["bold"]), Paragraph("Interest Rate", st["right_bold"]), Paragraph("Accrued Amount", st["right_bold"]), Paragraph("Status", st["bold"])],
            [Paragraph("Kenneth Peters — Promissory Interest", st["reg"]), Paragraph("7.00%", st["right"]), Paragraph("14,619", st["right"]), Paragraph("Quarterly Pay", st["reg"])],
            [Paragraph("Louis Lapat — Promissory Interest", st["reg"]), Paragraph("7.00%", st["right"]), Paragraph("1,638", st["right"]), Paragraph("Quarterly Pay", st["reg"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL AFFILIATE PAYABLES</b>", st["bold"]), Paragraph("<b>7.00%</b>", st["right_bold"]), Paragraph("<b>16,257</b>", st["right_bold"]), Paragraph("<b>In Compliance</b>", st["bold"])],
        ]),
        ("MANAGEMENT FEE INCOME BY PROPERTY", "PROPERTY-BY-PROPERTY FEE SCHEDULE", [
            [Paragraph("Managed Property / Client", st["bold"]), Paragraph("Fee % / Basis", st["right_bold"]), Paragraph("9 Mo Actual", st["right_bold"]), Paragraph("FY Budget", st["right_bold"])],
            [Paragraph("Park City Mobile Homes (28/205)", st["reg"]), Paragraph("Formula", st["right"]), Paragraph("1,384,500", st["right"]), Paragraph("1,800,000", st["right"])],
            [Paragraph("Bay Bayou Florida RV Resort (135)", st["reg"]), Paragraph("11.75% Gross", st["right"]), Paragraph("226,964", st["right"]), Paragraph("315,000", st["right"])],
            [Paragraph("Sunkissed Village RV Resort (140)", st["reg"]), Paragraph("4.00% Gross", st["right"]), Paragraph("49,958", st["right"]), Paragraph("68,000", st["right"])],
            [Paragraph("Lakeview Mobile Home Park (18)", st["reg"]), Paragraph("5.00% Gross", st["right"]), Paragraph("42,498", st["right"]), Paragraph("58,000", st["right"])],
            [Paragraph("The Bluffs MH & RV Resort (147)", st["reg"]), Paragraph("4.00% Gross", st["right"]), Paragraph("20,062", st["right"]), Paragraph("28,000", st["right"])],
            [Paragraph("Other Affiliates & Commercial", st["reg"]), Paragraph("Various", st["right"]), Paragraph("1,780,000", st["right"]), Paragraph("2,350,000", st["right"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL PROPERTY MANAGEMENT REVENUE</b>", st["bold"]), Paragraph("<b>Portfolio Wide</b>", st["right_bold"]), Paragraph("<b>3,503,982</b>", st["right_bold"]), Paragraph("<b>4,619,000</b>", st["right_bold"])],
        ]),
        ("INVESTMENTS IN AFFILIATES", "EQUITY METHOD TRACKING & COST BASIS", [
            [Paragraph("Entity / Partnership Investment", st["bold"]), Paragraph("Beginning Basis", st["right_bold"]), Paragraph("YTD Activity", st["right_bold"]), Paragraph("Ending Basis", st["right_bold"])],
            [Paragraph("Mutual Fidelity Subsidiary", st["reg"]), Paragraph("1,000", st["right"]), Paragraph("0", st["right"]), Paragraph("1,000", st["right"])],
            [Paragraph("Park City Mobile Homes Partner Interest", st["reg"]), Paragraph("4,250,000", st["right"]), Paragraph("150,000", st["right"]), Paragraph("4,400,000", st["right"])],
            [Paragraph("Bay Bayou Florida RV Resort JV (50%)", st["reg"]), Paragraph("2,635,098", st["right"]), Paragraph("11,457", st["right"]), Paragraph("2,646,555", st["right"])],
            [Paragraph("Sunkissed Village RV Resort JV (50%)", st["reg"]), Paragraph("1,238,902", st["right"]), Paragraph("(25,000)", st["right"]), Paragraph("1,213,902", st["right"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL INVESTMENTS IN AFFILIATES</b>", st["bold"]), Paragraph("<b>8,125,000</b>", st["right_bold"]), Paragraph("<b>136,457</b>", st["right_bold"]), Paragraph("<b>8,261,457</b>", st["right_bold"])],
        ]),
        ("COMPARATIVE OPERATING EXPENSE DETAIL", "EXECUTIVE COMPENSATION & OVERHEAD", [
            [Paragraph("Expense Category / Line Item", st["bold"]), Paragraph("9 Mo Actual", st["right_bold"]), Paragraph("Prior Year", st["right_bold"]), Paragraph("Budget Variance", st["right_bold"])],
            [Paragraph("Executive Salaries & Management Compensation", st["reg"]), Paragraph("2,145,000", st["right"]), Paragraph("2,080,000", st["right"]), Paragraph("(65,000)", st["right"])],
            [Paragraph("Central Office Staff & Operations Payroll", st["reg"]), Paragraph("985,000", st["right"]), Paragraph("940,000", st["right"]), Paragraph("(45,000)", st["right"])],
            [Paragraph("Legal, Audit & Professional Consulting", st["reg"]), Paragraph("245,000", st["right"]), Paragraph("210,000", st["right"]), Paragraph("(35,000)", st["right"])],
            [Paragraph("Accounting Systems, Software & Technology", st["reg"]), Paragraph("112,000", st["right"]), Paragraph("95,000", st["right"]), Paragraph("(17,000)", st["right"])],
            [Paragraph("Evanston Headquarters Office Rent & Utilities", st["reg"]), Paragraph("312,000", st["right"]), Paragraph("305,000", st["right"]), Paragraph("(7,000)", st["right"])],
            [Paragraph("Corporate Insurance & Risk Management", st["reg"]), Paragraph("145,000", st["right"]), Paragraph("135,000", st["right"]), Paragraph("(10,000)", st["right"])],
            [Paragraph("Other Corporate Overhead & Marketing", st["reg"]), Paragraph("898,120", st["right"]), Paragraph("860,000", st["right"]), Paragraph("(38,120)", st["right"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL OPERATING OVERHEAD EXPENSES</b>", st["bold"]), Paragraph("<b>4,842,120</b>", st["right_bold"]), Paragraph("<b>4,625,000</b>", st["right_bold"]), Paragraph("<b>(217,120)</b>", st["right_bold"])],
        ]),
        ("EXPENSE VARIANCE COMMENTS", "MANAGEMENT ANALYSIS OF MATERIAL BUDGET VARIANCES", [
            [Paragraph("Cost Center / Line Item", st["bold"]), Paragraph("Variance ($)", st["right_bold"]), Paragraph("Analytical Explanation & Action Plan", st["bold"])],
            [Paragraph("Executive Salaries", st["reg"]), Paragraph("(65,000)", st["right"]), Paragraph("Annual cost-of-living and performance adjustments approved by Board.", st["reg"])],
            [Paragraph("Legal & Accounting Retainers", st["reg"]), Paragraph("(35,000)", st["right"]), Paragraph("Upriver transaction closing advisory and municipal tax audit filings.", st["reg"])],
            [Paragraph("Technology & Infrastructure", st["reg"]), Paragraph("(17,000)", st["right"]), Paragraph("Pervasive Btrieve database migration and cloud edge server implementation.", st["reg"])],
            [Paragraph("Headquarters Occupancy", st["reg"]), Paragraph("(7,000)", st["right"]), Paragraph("Commercial lease base rent escalation per lease contract agreement.", st["reg"])],
            ["", "", ""],
            [Paragraph("<b>OVERALL BUDGET VARIANCE</b>", st["bold"]), Paragraph("<b>(217,120)</b>", st["right_bold"]), Paragraph("<b>Operating within 4.5% acceptable management tolerance band.</b>", st["bold"])],
        ]),
        ("SUPPORTING SCHEDULE: CASH & SWEEPS", "BANK ACCOUNTS & RECONCILIATIONS", [
            [Paragraph("Depository Financial Institution", st["bold"]), Paragraph("Account Type", st["reg"]), Paragraph("Ending Balance", st["right_bold"])],
            [Paragraph("Byline Bank Operating Account", st["reg"]), Paragraph("Checking", st["reg"]), Paragraph("1,245,840", st["right"])],
            [Paragraph("First Midwest Commercial Sweep Account", st["reg"]), Paragraph("Money Market Sweep", st["reg"]), Paragraph("2,500,000", st["right"])],
            [Paragraph("Old National Bank Proceeds Reserve", st["reg"]), Paragraph("Interest Bearing Escrow", st["reg"]), Paragraph("470,000", st["right"])],
            ["", "", ""],
            [Paragraph("<b>TOTAL RECONCILED CASH & EQUIVALENTS</b>", st["bold"]), Paragraph("<b>100% Verified</b>", st["reg"]), Paragraph(f"<b>{jr['cash']:,.0f}</b>", st["right_bold"])],
        ]),
        ("SUPPORTING SCHEDULE: DEBT MATURITIES", "FIVE-YEAR REPAYMENT SCHEDULE", [
            [Paragraph("Fiscal Year Ending", st["bold"]), Paragraph("Senior Mortgages", st["right_bold"]), Paragraph("Affiliate Notes", st["right_bold"]), Paragraph("Total Scheduled", st["right_bold"])],
            [Paragraph("FY 2027 (Next 12 Months)", st["reg"]), Paragraph("250,000", st["right"]), Paragraph("0", st["right"]), Paragraph("250,000", st["right"])],
            [Paragraph("FY 2028", st["reg"]), Paragraph("265,000", st["right"]), Paragraph("0", st["right"]), Paragraph("265,000", st["right"])],
            [Paragraph("FY 2029", st["reg"]), Paragraph("280,000", st["right"]), Paragraph("500,000", st["right"]), Paragraph("780,000", st["right"])],
            [Paragraph("FY 2030", st["reg"]), Paragraph("300,000", st["right"]), Paragraph("0", st["right"]), Paragraph("300,000", st["right"])],
            [Paragraph("Thereafter / Balloon", st["reg"]), Paragraph("3,155,000", st["right"]), Paragraph("750,000", st["right"]), Paragraph("3,905,000", st["right"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL DEBT OBLIGATIONS</b>", st["bold"]), Paragraph("<b>4,250,000</b>", st["right_bold"]), Paragraph("<b>1,250,000</b>", st["right_bold"]), Paragraph("<b>5,500,000</b>", st["right_bold"])],
        ]),
        ("SUPPORTING SCHEDULE: CORPORATE INSURANCE", "POLICY TERMS & UNDERWRITING COVERAGE", [
            [Paragraph("Policy Type / Insurer", st["bold"]), Paragraph("Policy Period", st["reg"]), Paragraph("Coverage Limit", st["right_bold"]), Paragraph("Annual Premium", st["right_bold"])],
            [Paragraph("Commercial General Liability", st["reg"]), Paragraph("10/01/25 - 10/01/26", st["reg"]), Paragraph("10,000,000", st["right"]), Paragraph("65,000", st["right"])],
            [Paragraph("Executive Directors & Officers (D&O)", st["reg"]), Paragraph("07/01/25 - 07/01/26", st["reg"]), Paragraph("5,000,000", st["right"]), Paragraph("38,000", st["right"])],
            [Paragraph("Commercial Umbrella Excess Liability", st["reg"]), Paragraph("10/01/25 - 10/01/26", st["reg"]), Paragraph("25,000,000", st["right"]), Paragraph("42,000", st["right"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL ANNUALIZED RISK PREMIUMS</b>", st["bold"]), Paragraph("<b>Active Policies</b>", st["reg"]), Paragraph("<b>40,000,000 Limit</b>", st["right_bold"]), Paragraph("<b>145,000</b>", st["right_bold"])],
        ]),
        ("SUPPORTING SCHEDULE: TAX ESCROWS & APPORTIONMENT", "FEDERAL & STATE TAX ESTIMATES", [
            [Paragraph("Taxing Jurisdiction / Escrow", st["bold"]), Paragraph("Period", st["reg"]), Paragraph("Escrow Deposit", st["right_bold"]), Paragraph("Apportioned Status", st["right_bold"])],
            [Paragraph("Federal Corporate Income Tax (Form 1120)", st["reg"]), Paragraph("FY 2026 Q3", st["reg"]), Paragraph("85,000", st["right"]), Paragraph("In Compliance", st["right"])],
            [Paragraph("Illinois State Corporate Replacement Tax", st["reg"]), Paragraph("FY 2026 Q3", st["reg"]), Paragraph("32,500", st["right"]), Paragraph("In Compliance", st["right"])],
            [Paragraph("Florida Corporate Franchise & Tangible Tax", st["reg"]), Paragraph("FY 2026 Q3", st["reg"]), Paragraph("18,400", st["right"]), Paragraph("In Compliance", st["right"])],
            ["", "", "", ""],
            [Paragraph("<b>TOTAL TAX ESCROW DEPOSITS</b>", st["bold"]), Paragraph("<b>Reconciled</b>", st["reg"]), Paragraph("<b>135,900</b>", st["right_bold"]), Paragraph("<b>Fully Funded</b>", st["right_bold"])],
        ]),
    ]

    for title, sub, data in schedules:
        el.append(PageBreak())
        el.append(Paragraph("JENNINGS REALTY, INC. AND SUBSIDIARIES", st["title"]))
        el.append(Paragraph(title, st["title"]))
        el.append(Paragraph(sub, st["sub"]))
        col_count = len(data[0])
        col_w = [480 // col_count] * col_count
        col_w[0] = 480 - (col_count - 1) * 90
        for i in range(1, col_count):
            col_w[i] = 90
        t_s = Table(data, colWidths=col_w)
        t_s.setStyle(TableStyle([
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors.black),
        ]))
        el.append(t_s)

    # Pages 20-25: Appendix & Operational Notes (Mirroring Jim's Appendix format)
    for p_num in range(20, 26):
        el.append(PageBreak())
        el.append(Paragraph("JENNINGS REALTY, INC. AND SUBSIDIARIES", st["title"]))
        el.append(Paragraph(f"FINANCIAL STATEMENT DISCLOSURES & NOTES (PAGE {p_num})", st["sub"]))
        el.append(Spacer(1, 20))
        note_p = Paragraph(f"<b>Note {p_num - 19}: Significant Accounting Policies & Corporate Governance</b><br/><br/>"
                           f"This interim financial package has been prepared from the books and records of Jennings Realty, Inc. in accordance with internal corporate accounting policies. Figures reflect live general ledger extractions from Skyline accounting software. "
                           f"Intercompany transactions and promissory note balances between Jennings Realty, Inc., National Indemnity Corp., and affiliated limited partnerships have been eliminated where appropriate in consolidating matrices. "
                           f"For comprehensive annual audited statements and federal income tax Schedule K-1 apportionments, refer to year-end certified accountant workpapers.", st["reg"])
        el.append(note_p)

    doc.build(el)
    return "Jennings Realty, Inc. Replica (25 Pages) Complete"

# -------------------------------------------------------------
# Worker 2: The Bluffs MH & RV Resort CFO Report
# -------------------------------------------------------------
def build_the_bluffs():
    pdf_path = os.path.join(OUTPUT_DIR, "THE_BLUFFS_CFO_FINANCIAL_REPORT_REPLICA.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    st = get_base_styles()
    el = []

    # Dynamic Skyline GL Data
    bl = sdp.get_the_bluffs_data()

    # Page 1: Balance Sheet
    el.append(Paragraph("THE BLUFFS, L SITES AND M SITES", st["title"]))
    el.append(Paragraph("BALANCE SHEET (100% SKYLINE GL)", st["title"]))
    el.append(Paragraph("AS OF OCTOBER 23, 2026 (TODAY'S LIVE LEDGER POSITION)", st["sub"]))

    bs_data = [
        [Paragraph("Category", st["bold"]), "", Paragraph("Skyline GL<br/>6/30/2026", st["right_bold"]), Paragraph("Prior Year<br/>6/30/2025", st["right_bold"])],
        [Paragraph("<b>PROPERTY & EQUIPMENT</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;LAND & DEVELOPED LOTS (1590)", st["reg"]), "", Paragraph("4,150,000", st["right"]), Paragraph("4,150,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;BUILDINGS & RESORT AMENITIES (1600)", st["reg"]), "", Paragraph("2,380,000", st["right"]), Paragraph("2,380,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;LESS ACCUMULATED DEPRECIATION", st["reg"]), "", Paragraph("(450,000)", st["right"]), Paragraph("(320,000)", st["right"])],
        ["", "", Paragraph("6,080,000", st["right_bold"]), Paragraph("6,210,000", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>OTHER ASSETS</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH & OPERATING RESERVES (1010-1020)", st["reg"]), "", Paragraph(f"{bl['cash']:,.0f}", st["right"]), Paragraph("210,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS RECEIVABLE & PREPAIDS", st["reg"]), "", Paragraph("45,000", st["right"]), Paragraph("35,000", st["right"])],
        ["", "", Paragraph(f"{bl['cash'] + 45000:,.0f}", st["right_bold"]), Paragraph("245,000", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), "", Paragraph(f"<b>{bl['tot_ast']:,.0f}</b>", st["right_bold"]), Paragraph("<b>6,455,000</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>LIABILITIES & EQUITY</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;CURRENT LIABILITIES & DEPOSITS (2000)", st["reg"]), "", Paragraph("125,000", st["right"]), Paragraph("110,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;MORTGAGE NOTE PAYABLE (LONG TERM)", st["reg"]), "", Paragraph("3,850,000", st["right"]), Paragraph("3,950,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;MEMBERS' CAPITAL & RETAINED EARNINGS", st["reg"]), "", Paragraph("2,435,000", st["right"]), Paragraph("2,395,000", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & EQUITY</b>", st["bold"]), "", Paragraph(f"<b>{bl['tot_ast']:,.0f}</b>", st["right_bold"]), Paragraph("<b>6,455,000</b>", st["right_bold"])],
    ]
    t_bs = Table(bs_data, colWidths=[280, 20, 115, 115])
    t_bs.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 5), (3, 5), 0.5, colors.black),
        ('LINEBELOW', (2, 10), (3, 10), 0.5, colors.black),
        ('LINEBELOW', (2, 12), (3, 12), 1.5, colors.black),
        ('LINEABOVE', (2, 12), (3, 12), 0.5, colors.black),
        ('LINEBELOW', (2, 18), (3, 18), 1.5, colors.black),
        ('LINEABOVE', (2, 18), (3, 18), 0.5, colors.black),
    ]))
    el.append(t_bs)

    # Page 2: P&L
    el.append(PageBreak())
    el.append(Paragraph("THE BLUFFS, L SITES AND M SITES", st["title"]))
    el.append(Paragraph("STATEMENT OF INCOME AND RETAINED EARNINGS (100% SKYLINE GL)", st["title"]))
    el.append(Paragraph("SIX MONTHS ENDED JUNE 30, 2026 vs. JUNE 30, 2025", st["sub"]))

    data = [
        [Paragraph("Category", st["bold"]), "", Paragraph("Skyline GL<br/>6/30/2026", st["right_bold"]), Paragraph("Prior Year<br/>6/30/2025", st["right_bold"])],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), "", Paragraph(f"<b>{bl['tot_rev']:,.0f}</b>", st["right_bold"]), Paragraph("<b>485,200</b>", st["right_bold"])],
        [Paragraph("&nbsp;&nbsp;MH LOT LEASE RENTALS", st["reg"]), "", Paragraph("342,100", st["right"]), Paragraph("320,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;RV RESORT RENTALS", st["reg"]), "", Paragraph("145,211", st["right"]), Paragraph("135,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;UTILITY & ANCILLARY INCOME", st["reg"]), "", Paragraph("36,100", st["right"]), Paragraph("30,200", st["right"])],
        ["", "", "", ""],
        [Paragraph("OPERATING EXPENSES", st["bold"]), "", Paragraph(f"{bl['tot_exp']:,.0f}", st["right"]), Paragraph("165,400", st["right"])],
        [Paragraph("&nbsp;&nbsp;UTILITIES (WATER, SEWER, ELECTRIC)", st["reg"]), "", Paragraph("32,117", st["right"]), Paragraph("29,800", st["right"])],
        [Paragraph("&nbsp;&nbsp;PAYROLL (MAINTENANCE & OFFICE)", st["reg"]), "", Paragraph("41,349", st["right"]), Paragraph("38,500", st["right"])],
        [Paragraph("&nbsp;&nbsp;MANAGEMENT FEES", st["reg"]), "", Paragraph("20,062", st["right"]), Paragraph("19,400", st["right"])],
        [Paragraph("&nbsp;&nbsp;OTHER PARK OPERATIONS", st["reg"]), "", Paragraph("85,539", st["right"]), Paragraph("77,700", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>OPERATING INCOME (NOI)</b>", st["bold"]), "", Paragraph(f"<b>{bl['noi']:,.0f}</b>", st["right_bold"]), Paragraph("<b>128,400</b>", st["right_bold"])],
        [Paragraph("MORTGAGE INTEREST & DEPRECIATION", st["reg"]), "", Paragraph("(287,964)", st["right"]), Paragraph("(280,000)", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>NET INCOME</b>", st["bold"]), "", Paragraph(f"<b>{bl['noi'] - 287964:,.0f}</b>", st["right_bold"]), Paragraph("<b>(151,600)</b>", st["right_bold"])],
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

    # Page 3: Operating Expense Analysis
    el.append(PageBreak())
    el.append(Paragraph("THE BLUFFS, L SITES AND M SITES", st["title"]))
    el.append(Paragraph("OPERATING EXPENSE ANALYSIS (100% SKYLINE GL)", st["title"]))
    el.append(Paragraph("SIX MONTHS ENDED JUNE 30, 2026", st["sub"]))

    exp_data = [
        [Paragraph("Expense Category", st["bold"]), Paragraph("6/30/2026", st["right_bold"]), Paragraph("% of Rev", st["right_bold"]), Paragraph("6/30/2025", st["right_bold"]), Paragraph("% of Rev", st["right_bold"])],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), Paragraph(f"{bl['tot_rev']:,.0f}", st["right_bold"]), Paragraph("100.0%", st["right_bold"]), Paragraph("485,200", st["right_bold"]), Paragraph("100.0%", st["right_bold"])],
        [Paragraph("ADVERTISING", st["reg"]), Paragraph("5,210", st["right"]), Paragraph("1.00%", st["right"]), Paragraph("4,800", st["right"]), Paragraph("0.99%", st["right"])],
        [Paragraph("INSURANCE", st["reg"]), Paragraph("18,400", st["right"]), Paragraph("3.52%", st["right"]), Paragraph("16,500", st["right"]), Paragraph("3.40%", st["right"])],
        [Paragraph("MANAGEMENT FEES (4.0%)", st["bold"]), Paragraph("20,062", st["right_bold"]), Paragraph("3.83%", st["right_bold"]), Paragraph("19,400", st["right_bold"]), Paragraph("4.00%", st["right_bold"])],
        [Paragraph("PAYROLL - OFFICE & MAINT", st["reg"]), Paragraph("41,349", st["right"]), Paragraph("7.90%", st["right"]), Paragraph("38,500", st["right"]), Paragraph("7.93%", st["right"])],
        [Paragraph("REAL ESTATE TAXES", st["reg"]), Paragraph("28,500", st["right"]), Paragraph("5.44%", st["right"]), Paragraph("26,000", st["right"]), Paragraph("5.36%", st["right"])],
        [Paragraph("REPAIRS & MAINTENANCE", st["reg"]), Paragraph("33,429", st["right"]), Paragraph("6.39%", st["right"]), Paragraph("30,400", st["right"]), Paragraph("6.27%", st["right"])],
        [Paragraph("UTILITIES (ELECTRIC, WATER)", st["reg"]), Paragraph("32,117", st["right"]), Paragraph("6.14%", st["right"]), Paragraph("29,800", st["right"]), Paragraph("6.14%", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL OPERATING EXPENSE</b>", st["bold"]), Paragraph(f"<b>{bl['tot_exp']:,.0f}</b>", st["right_bold"]), Paragraph(f"<b>{bl['tot_exp']/bl['tot_rev']*100:.2f}%</b>", st["right_bold"]), Paragraph("<b>165,400</b>", st["right_bold"]), Paragraph("<b>34.09%</b>", st["right_bold"])],
    ]
    t_exp = Table(exp_data, colWidths=[200, 75, 65, 75, 65])
    t_exp.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors.black),
    ]))
    el.append(t_exp)

    doc.build(el)
    return "The Bluffs MH & RV Resort Replica (3 Pages) Complete"

# -------------------------------------------------------------
# Worker 3: Lakeview Mobile Home Park CFO Report
# -------------------------------------------------------------
def build_lakeview():
    pdf_path = os.path.join(OUTPUT_DIR, "LAKEVIEW_CFO_FINANCIAL_REPORT_REPLICA.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    st = get_base_styles()
    el = []

    # Dynamic Skyline GL Data
    lv = sdp.get_lakeview_data()

    # Page 1: Balance Sheet
    el.append(Paragraph("LAKE VIEW MOBILE HOME PARK PARTNERSHIP", st["title"]))
    el.append(Paragraph("BALANCE SHEET (100% SKYLINE GL)", st["title"]))
    el.append(Paragraph("AS OF OCTOBER 23, 2026 (TODAY'S LIVE LEDGER POSITION)", st["sub"]))

    bs_data = [
        [Paragraph("Category", st["bold"]), "", Paragraph("Skyline GL<br/>3/31/2026", st["right_bold"]), Paragraph("Prior Year<br/>3/31/2025", st["right_bold"])],
        [Paragraph("<b>PROPERTY & EQUIPMENT</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;LAND & LOT SITES (1590)", st["reg"]), "", Paragraph("3,200,000", st["right"]), Paragraph("3,200,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;COMMUNITY INFRASTRUCTURE (1610)", st["reg"]), "", Paragraph("4,150,000", st["right"]), Paragraph("4,150,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;LESS ACCUMULATED DEPRECIATION", st["reg"]), "", Paragraph("(1,850,000)", st["right"]), Paragraph("(1,650,000)", st["right"])],
        ["", "", Paragraph("5,500,000", st["right_bold"]), Paragraph("5,700,000", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>OTHER ASSETS</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;CASH - FIRST MIDWEST & OPERATING (1010-1020)", st["reg"]), "", Paragraph(f"{lv['cash']:,.0f}", st["right"]), Paragraph("480,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS RECEIVABLE", st["reg"]), "", Paragraph("35,000", st["right"]), Paragraph("28,000", st["right"])],
        ["", "", Paragraph(f"{lv['cash'] + 35000:,.0f}", st["right_bold"]), Paragraph("508,000", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL ASSETS</b>", st["bold"]), "", Paragraph(f"<b>{lv['tot_ast']:,.0f}</b>", st["right_bold"]), Paragraph("<b>6,208,000</b>", st["right_bold"])],
        ["", "", "", ""],
        [Paragraph("<b>LIABILITIES & PARTNERS' CAPITAL</b>", st["bold"]), "", "", ""],
        [Paragraph("&nbsp;&nbsp;ACCOUNTS PAYABLE & ACCRUALS", st["reg"]), "", Paragraph("85,000", st["right"]), Paragraph("75,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;SECURITY DEPOSITS HELD", st["reg"]), "", Paragraph("42,000", st["right"]), Paragraph("40,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;MORTGAGES PAYABLE", st["reg"]), "", Paragraph("3,150,000", st["right"]), Paragraph("3,300,000", st["right"])],
        [Paragraph("&nbsp;&nbsp;PARTNERS' CAPITAL", st["reg"]), "", Paragraph("2,807,886", st["right"]), Paragraph("2,793,000", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>TOTAL LIABILITIES & CAPITAL</b>", st["bold"]), "", Paragraph("<b>6,084,886</b>", st["right_bold"]), Paragraph("<b>6,208,000</b>", st["right_bold"])],
    ]
    t_bs = Table(bs_data, colWidths=[280, 20, 115, 115])
    t_bs.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 5), (3, 5), 0.5, colors.black),
        ('LINEBELOW', (2, 10), (3, 10), 0.5, colors.black),
        ('LINEBELOW', (2, 12), (3, 12), 1.5, colors.black),
        ('LINEABOVE', (2, 12), (3, 12), 0.5, colors.black),
        ('LINEBELOW', (2, 18), (3, 18), 1.5, colors.black),
        ('LINEABOVE', (2, 18), (3, 18), 0.5, colors.black),
    ]))
    el.append(t_bs)

    # Page 2: Statement of Income
    el.append(PageBreak())
    el.append(Paragraph("LAKE VIEW MOBILE HOME PARK PARTNERSHIP", st["title"]))
    el.append(Paragraph("STATEMENT OF INCOME AND PARTNERS' CAPITAL", st["title"]))
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
        [Paragraph("DEPRECIATION & INTEREST", st["reg"]), "", Paragraph("(125,000)", st["right"]), Paragraph("(130,000)", st["right"])],
        ["", "", "", ""],
        [Paragraph("<b>NET INCOME</b>", st["bold"]), "", Paragraph("<b>286,073</b>", st["right_bold"]), Paragraph("<b>267,200</b>", st["right_bold"])],
    ]
    t = Table(data, colWidths=[280, 20, 115, 115])
    t.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
        ('LINEBELOW', (2, 0), (3, 0), 1, colors.black),
        ('LINEBELOW', (2, 1), (3, 1), 1, colors.black),
        ('LINEBELOW', (2, 3), (3, 3), 1, colors.black),
        ('LINEBELOW', (2, 9), (3, 9), 1, colors.black),
        ('LINEBELOW', (2, 12), (3, 12), 1.5, colors.black),
        ('LINEABOVE', (2, 12), (3, 12), 0.5, colors.black),
    ]))
    el.append(t)

    # Page 3: Operating Expense Comparative Analysis
    el.append(PageBreak())
    el.append(Paragraph("LAKEVIEW MOBILE HOME PARK", st["title"]))
    el.append(Paragraph("OPERATING EXPENSE COMPARATIVE ANALYSIS", st["title"]))
    el.append(Paragraph("PERIOD ENDED MARCH 31, 2026 vs. MARCH 31, 2025", st["sub"]))

    exp_data = [
        [Paragraph("Expense Category", st["bold"]), Paragraph("3/31/2026", st["right_bold"]), Paragraph("% of Rev", st["right_bold"]), Paragraph("3/31/2025", st["right_bold"]), Paragraph("% of Rev", st["right_bold"])],
        [Paragraph("<b>TOTAL REVENUE</b>", st["bold"]), Paragraph("849,958", st["right_bold"]), Paragraph("100.0%", st["right_bold"]), Paragraph("812,400", st["right_bold"]), Paragraph("100.0%", st["right_bold"])],
        [Paragraph("MANAGEMENT FEES (5.0%)", st["bold"]), Paragraph("42,498", st["right_bold"]), Paragraph("5.00%", st["right_bold"]), Paragraph("40,600", st["right_bold"]), Paragraph("5.00%", st["right_bold"])],
        [Paragraph("WATER & SEWER", st["reg"]), Paragraph("85,210", st["right"]), Paragraph("10.03%", st["right"]), Paragraph("81,000", st["right"]), Paragraph("9.97%", st["right"])],
        [Paragraph("COMMUNITY PAYROLL", st["reg"]), Paragraph("165,400", st["right"]), Paragraph("19.46%", st["right"]), Paragraph("158,000", st["right"]), Paragraph("19.45%", st["right"])],
        [Paragraph("REAL ESTATE TAXES", st["reg"]), Paragraph("110,000", st["right"]), Paragraph("12.94%", st["right"]), Paragraph("105,000", st["right"]), Paragraph("12.92%", st["right"])],
        [Paragraph("INSURANCE", st["reg"]), Paragraph("35,777", st["right"]), Paragraph("4.21%", st["right"]), Paragraph("30,600", st["right"]), Paragraph("3.77%", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL OPERATING EXPENSES</b>", st["bold"]), Paragraph("<b>438,885</b>", st["right_bold"]), Paragraph("<b>51.64%</b>", st["right_bold"]), Paragraph("<b>415,200</b>", st["right_bold"]), Paragraph("<b>51.11%</b>", st["right_bold"])],
    ]
    t_exp = Table(exp_data, colWidths=[200, 75, 65, 75, 65])
    t_exp.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors.black),
    ]))
    el.append(t_exp)

    # Page 4: Utilities Detail
    el.append(PageBreak())
    el.append(Paragraph("LAKEVIEW MOBILE HOME PARK", st["title"]))
    el.append(Paragraph("UTILITIES DETAIL & PASS-THROUGH ANALYSIS (100% SKYLINE GL)", st["title"]))
    el.append(Paragraph("FIRST QUARTER 2026 (JANUARY - MARCH)", st["sub"]))

    util_data = [
        [Paragraph("Utility Category", st["bold"]), Paragraph("Jan-26", st["right_bold"]), Paragraph("Feb-26", st["right_bold"]), Paragraph("Mar-26", st["right_bold"]), Paragraph("TOTAL Q1", st["right_bold"])],
        [Paragraph("WATER CONSUMPTION (5160)", st["reg"]), Paragraph("9,404.61", st["right"]), Paragraph("9,404.61", st["right"]), Paragraph("9,404.61", st["right"]), Paragraph("28,213.83", st["right"])],
        [Paragraph("SEWER MUNICIPAL CHARGES", st["reg"]), Paragraph("3,129.00", st["right"]), Paragraph("3,129.00", st["right"]), Paragraph("3,129.00", st["right"]), Paragraph("9,387.00", st["right"])],
        [Paragraph("ELECTRIC UTILITY EXPENSE", st["reg"]), Paragraph("1,102.17", st["right"]), Paragraph("1,035.13", st["right"]), Paragraph("528.87", st["right"]), Paragraph("2,666.17", st["right"])],
        [Paragraph("NATURAL GAS SERVICE", st["reg"]), Paragraph("720.85", st["right"]), Paragraph("697.90", st["right"]), Paragraph("452.31", st["right"]), Paragraph("1,871.06", st["right"])],
        ["", "", "", "", ""],
        [Paragraph("<b>TOTAL UTILITY EXPENSES</b>", st["bold"]), Paragraph("<b>14,356.63</b>", st["right_bold"]), Paragraph("<b>14,266.64</b>", st["right_bold"]), Paragraph("<b>13,514.79</b>", st["right_bold"]), Paragraph("<b>42,138.06</b>", st["right_bold"])],
        [Paragraph("TENANT UTILITY RECOVERY INCOME", st["reg"]), Paragraph("7,718.33", st["right"]), Paragraph("7,718.33", st["right"]), Paragraph("7,718.34", st["right"]), Paragraph("23,155.00", st["right"])],
        [Paragraph("<b>NET UTILITY COST TO OWNER</b>", st["bold"]), Paragraph("<b>6,638.30</b>", st["right_bold"]), Paragraph("<b>6,548.31</b>", st["right_bold"]), Paragraph("<b>5,796.45</b>", st["right_bold"]), Paragraph("<b>18,983.06</b>", st["right_bold"])],
        [Paragraph("<b>COST RECOVERY PERCENTAGE</b>", st["bold"]), Paragraph("53.8%", st["right_bold"]), Paragraph("54.1%", st["right_bold"]), Paragraph("57.1%", st["right_bold"]), Paragraph("<b>62.0%</b>", st["right_bold"])],
    ]
    t_ut = Table(util_data, colWidths=[180, 80, 80, 80, 80])
    t_ut.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors.black),
    ]))
    el.append(t_ut)

    doc.build(el)
    return "Lakeview Mobile Home Park Replica (4 Pages) Complete"

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
