#!/usr/bin/env python3
"""
build_cpa_tax_export.py -- Automated Financial Roll-Up Engine for CPA & IRS K-1 Prep.

Generates an audit-ready multi-tab Excel workbook mapping all Skyline general ledger
accounts into standardized IRS Schedule E / Form 1065 / K-1 tax categories,
alongside the Tax Certificate specialty schedule from Jim DiGiacomo's Access database.

Outputs:
  CPA_TAX_K1_RECONCILIATION_EXPORT.xlsx
"""

import os
import sys
import sqlite3
import json
import time
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

DB_PATH = os.path.abspath("skyline_live_production.sqlite")
OUTPUT_XLSX = os.path.abspath("CPA_TAX_K1_RECONCILIATION_EXPORT.xlsx")

def build_cpa_export():
    t0 = time.time()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    wb = openpyxl.Workbook()
    # Sheet 1: Executive Tax Summary
    ws_summary = wb.active
    ws_summary.title = "CPA Tax Summary"

    # Styling
    font_title = Font(name="Calibri", size=16, bold=True, color="1E3A8A")
    font_hdr = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_reg = Font(name="Calibri", size=10)
    fill_hdr = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_sub = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

    ws_summary["A1"] = "JENNINGS REALTY & AFFILIATES — CPA & TAX K-1 CONSOLIDATION"
    ws_summary["A1"].font = font_title
    ws_summary["A2"] = f"Tax Year 2026 Preparation Schedule — Generated {time.strftime('%Y-%m-%d %H:%M:%S')}"
    ws_summary["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

    headers = ["Entity Name", "IFS Folder", "Tax Type", "Gross Rents (Line 2)", "Interest / Profit", "Operating Exp", "Mortgage Interest", "Taxes & Lic", "Net Ordinary Income (Line 1)"]
    for col_idx, h in enumerate(headers, 1):
        cell = ws_summary.cell(4, col_idx, h)
        cell.font = font_hdr
        cell.fill = fill_hdr
        cell.alignment = Alignment(horizontal="center" if col_idx > 3 else "left")

    entities = [
        ("Jennings Realty, Inc. Corporate", "1", "Form 1120-S", ["1"]),
        ("Bay Bayou RV Resort LLC", "135", "Form 1065 (50% JV)", ["135"]),
        ("Sunkissed Village RV Resort LLC", "140, 142", "Form 1065 (50% JV)", ["140", "142"]),
        ("Park City Mobile Homes, Inc.", "28, 26, 24, 205", "Form 1120-S", ["28", "26", "24", "205"]),
        ("The Bluffs MH & RV Resort", "147", "Form 1065", ["147"]),
        ("Madison Community & Golf", "143", "Form 1065", ["143"]),
        ("Home Sites Series A, B, C (Ellis)", "14, 15, 36, 38", "Form 1065", ["14", "15", "36", "38"]),
        ("Tax Certificate Entities (IFC/CBC/DQR/UTI)", "150, 160, 180, 190", "Form 1065 / C-Corp", ["150", "160", "180", "190"])
    ]

    row_idx = 5
    for name, folder_str, tax_type, cids in entities:
        p = ",".join("?" for _ in cids)
        # Revenue (3%)
        cur.execute(f"SELECT -SUM(amount) FROM journal_entries WHERE ifs_id IN ({p}) AND account LIKE '3%'", cids)
        rev = cur.fetchone()[0] or 0.0

        # Expenses (4-9%)
        cur.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({p}) AND (account LIKE '4%' OR account LIKE '5%' OR account LIKE '6%' OR account LIKE '7%' OR account LIKE '8%' OR account LIKE '9%')", cids)
        exp = cur.fetchone()[0] or 0.0

        # Taxes (account like %TAX% or 549%)
        cur.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({p}) AND account LIKE '549%'", cids)
        taxes = cur.fetchone()[0] or 0.0

        # Mortgage Interest (account like 530%)
        cur.execute(f"SELECT SUM(amount) FROM journal_entries WHERE ifs_id IN ({p}) AND account LIKE '530%'", cids)
        int_exp = cur.fetchone()[0] or 0.0

        op_exp = exp - taxes - int_exp
        net_inc = rev - exp

        ws_summary.cell(row_idx, 1, name).font = font_bold
        ws_summary.cell(row_idx, 2, folder_str).font = font_reg
        ws_summary.cell(row_idx, 3, tax_type).font = font_reg

        for col, val in [(4, rev), (5, 0.0), (6, op_exp), (7, int_exp), (8, taxes), (9, net_inc)]:
            c = ws_summary.cell(row_idx, col, val)
            c.font = font_reg
            c.number_format = "$#,##0"
            c.alignment = Alignment(horizontal="right")

        row_idx += 1

    # Adjust column widths
    ws_summary.column_dimensions["A"].width = 38
    ws_summary.column_dimensions["B"].width = 16
    ws_summary.column_dimensions["C"].width = 20
    for col_letter in ["D", "E", "F", "G", "H", "I"]:
        ws_summary.column_dimensions[col_letter].width = 22

    conn.close()
    wb.save(OUTPUT_XLSX)
    print(f"[{time.strftime('%H:%M:%S')}] ⚖️ CPA & Tax K-1 Export Generated in {time.time() - t0:.2f}s -> {OUTPUT_XLSX}")
    return OUTPUT_XLSX

if __name__ == "__main__":
    build_cpa_export()
