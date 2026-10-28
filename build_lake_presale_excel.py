#!/usr/bin/env python3
"""
build_lake_presale_excel.py -- Generates a clean, institutional Excel workbook
for Stan Engelsen containing all 268 high-dollar 2nd-installment targets ($5.12M pool)
and the curated $2.0M bidding plan for the Lake County Tax Sale (Nov 13, 2026).
"""

import os
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUTPUT_XLSX = os.path.abspath("data/Lake_County_2026_Presale_Targets.xlsx")
TARGETS_JSON = os.path.abspath("lake_presale_targets.json")

def build_excel():
    with open(TARGETS_JSON) as f:
        targets_data = json.load(f)

    wb = openpyxl.Workbook()
    wb.remove(wb.active) # Remove default sheet

    # Color Palette
    navy_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    dark_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    green_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    purple_fill = PatternFill(start_color="F3E8FF", end_color="F3E8FF", fill_type="solid")
    alt_row_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_normal = Font(name="Calibri", size=10)
    font_green = Font(name="Calibri", size=10, bold=True, color="166534")
    font_purple = Font(name="Calibri", size=10, bold=True, color="6B21A8")

    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # Helper function to populate a target sheet
    def populate_sheet(ws, title_text, target_list):
        ws.views.sheetView[0].showGridLines = True

        ws.merge_cells("A1:K1")
        ws["A1"] = title_text
        ws["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
        ws["A1"].fill = navy_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 32

        ws.merge_cells("A2:K2")
        ws["A2"] = "Sale Date: Friday, Nov 13, 2026 | Strategy: 4% on >= $25k (Outbids Bridge); 5% on $10k-$25k | 100% Lake County Portal Data"
        ws["A2"].font = Font(name="Calibri", size=10, italic=True, color="FFFFFF")
        ws["A2"].fill = dark_fill
        ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 20

        headers = [
            "PIN", "Taxpayer / Business Name", "City", "Township", "Property Class",
            "Tax Due ($)", "Assessed Bldg ($)", "Bldg/Land Ratio", "Recommended Bid %",
            "Est. 12% Subtax Return ($/yr)", "County Redemption History"
        ]
        ws.append([]) # row 3
        ws.append(headers) # row 4
        ws.row_dimensions[4].height = 26

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=4, column=col_idx)
            cell.font = font_header
            cell.fill = navy_fill
            cell.alignment = Alignment(horizontal="center" if col_idx in [1, 9, 11] else "left", vertical="center")

        for r_idx, t in enumerate(target_list, start=5):
            pin = t["pin"]
            name = t["taxpayer"]
            city = t["city"]
            twp = t["township"]
            pclass = t["property_type"]
            due = t["tax_due"]
            bldg = t["asmt_bldg"]
            ratio = t["bldg_land_ratio"]
            rec_bid = t["rec_bid"]
            subtax = t["subtax_annual_return"]
            reds = t.get("prior_redemptions_count", 0)
            red_text = f"{reds}x Redeemed" if reds > 0 else "Clean Record"

            ws.append([pin, name, city, twp, pclass, due, bldg, ratio, rec_bid, subtax, red_text])
            ws.row_dimensions[r_idx].height = 20

            for c in range(1, 12):
                cell = ws.cell(row=r_idx, column=c)
                cell.font = font_normal
                cell.border = thin_border
                if r_idx % 2 == 0:
                    cell.fill = alt_row_fill

            ws.cell(row=r_idx, column=1).alignment = Alignment(horizontal="center")
            ws.cell(row=r_idx, column=6).number_format = '$#,##0.00'
            ws.cell(row=r_idx, column=7).number_format = '$#,##0'
            ws.cell(row=r_idx, column=8).number_format = '0.0"x"'
            ws.cell(row=r_idx, column=9).number_format = '0.0%'
            ws.cell(row=r_idx, column=9).alignment = Alignment(horizontal="center")
            if rec_bid <= 0.04:
                ws.cell(row=r_idx, column=9).font = font_green
                ws.cell(row=r_idx, column=9).fill = green_fill
            ws.cell(row=r_idx, column=10).number_format = '$#,##0.00'
            ws.cell(row=r_idx, column=10).font = font_green
            ws.cell(row=r_idx, column=11).alignment = Alignment(horizontal="center")
            if reds >= 2:
                ws.cell(row=r_idx, column=11).font = font_purple
                ws.cell(row=r_idx, column=11).fill = purple_fill

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row in [1, 2]:
                    continue
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        ws.column_dimensions["A"].width = 16
        ws.column_dimensions["B"].width = 30

    # Sheet 1: All 268 2nd-Installment Targets ($5.12M Pool)
    ws1 = wb.create_sheet(title="2nd Inst Targets ($5.12M)")
    half_targets = [t for t in targets_data["top_targets"] if t.get("is_half_installment")]
    populate_sheet(ws1, "LAKE COUNTY 2026 — ALL 2ND INSTALLMENT TARGETS ($5.12M POOL)", half_targets)

    # Sheet 2: Curated $2.0M Portfolio Plan
    ws2 = wb.create_sheet(title="Curated $2.0M Bidding Plan")
    curated = targets_data.get("curated_2m_portfolio", {}).get("parcels", [])
    populate_sheet(ws2, "LAKE COUNTY 2026 — CURATED $2.0M ALLOCATION PLAN (54 PARCELS)", curated)

    wb.save(OUTPUT_XLSX)
    print(f"✅ Created streamlined Excel workbook: {OUTPUT_XLSX}")

if __name__ == "__main__":
    build_excel()
