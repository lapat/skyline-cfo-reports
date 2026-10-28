#!/usr/bin/env python3
"""
build_lake_presale_excel.py -- Generates comprehensive workbook for Jay & Stan:
1. 2026 Sales Schedule & Lake Filter (Jay's specs).
2. 2025 County Bid Rates & Competitors (Full analysis of last year vs this year).
3. Commercial & Industrial (487 certs, $8.15M).
4. Residential & Other (4,524 certs, $29.25M).
"""

import os
import csv
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUTPUT_XLSX = os.path.abspath("data/Lake_County_2026_Presale_Targets.xlsx")
SCRAPED_XLSX = "/Users/louislapat/vibe/google/collarcounties/lake/output_2026/2026_Lake_Scraped_Results.xlsx"
LAKE_CSV = os.path.abspath("data/lake_2026_sale/2026 Lake List 2025 Taxes.csv")

def build_excel():
    # 1. Load scraped installment breakdown
    wb_scraped = openpyxl.load_workbook(SCRAPED_XLSX, data_only=True)
    ws_scraped = wb_scraped['Master Profile & Summary']

    half_pins = set()
    for r in range(2, ws_scraped.max_row + 1):
        pin = ws_scraped.cell(r, 1).value
        if pin:
            def clean_val(v):
                try: return float(str(v).replace('$', '').replace(',', '').strip())
                except: return 0.0
            c1 = clean_val(ws_scraped.cell(r, 9).value)
            c2 = clean_val(ws_scraped.cell(r, 10).value)
            if c1 <= 10.0 and c2 > 100.0:
                half_pins.add(str(pin).strip())

    # 2. Parse Lake CSV
    with open(LAKE_CSV, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    removed_under_3k = []
    comm_certs = []
    res_certs = []

    for r in rows:
        pin = (r.get('Parcel Number') or '').strip()
        amt_str = (r.get('Judgment Amount') or '0').replace('$', '').replace(',', '').strip()
        try: amt = float(amt_str)
        except: amt = 0.0
        
        is_half = pin in half_pins
        msg = r.get('MSG') or ''
        is_comm = ('commercial' in msg.lower()) or ('industrial' in msg.lower())

        item = {
            "pin": pin,
            "taxpayer": (r.get('Taxpayer Name') or '').strip(),
            "city": (r.get('Property City') or '').strip(),
            "township": (r.get('Township') or '').strip(),
            "property_type": msg,
            "tax_due": amt,
            "asmt_bldg": float((r.get('Asmt Bldg') or '0').replace(',', '').strip() or 0),
            "asmt_land": float((r.get('Asmt Land') or '0').replace(',', '').strip() or 0),
            "is_half": is_half,
            "installment_status": "2nd Inst Only (Half)" if is_half else "Full Year Delinquent"
        }
        item["bldg_land_ratio"] = round(item["asmt_bldg"] / item["asmt_land"], 2) if item["asmt_land"] > 0 else 0.0

        if (not is_half) and (amt < 3000.0):
            removed_under_3k.append(item)
        else:
            if is_comm:
                comm_certs.append(item)
            else:
                res_certs.append(item)

    comm_certs.sort(key=lambda x: x["tax_due"], reverse=True)
    res_certs.sort(key=lambda x: x["tax_due"], reverse=True)

    # 3. Build Excel
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    navy_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    dark_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    green_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    purple_fill = PatternFill(start_color="F3E8FF", end_color="F3E8FF", fill_type="solid")
    alt_row_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_normal = Font(name="Calibri", size=10)

    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # =========================================================================
    # SHEET 1: Master Schedule & Revised Lake Summary
    # =========================================================================
    ws1 = wb.create_sheet(title="2026 Sales Schedule & Lake")
    ws1.views.sheetView[0].showGridLines = True

    ws1.merge_cells("A1:G1")
    ws1["A1"] = "JENNINGS REALTY — 2026 TAX SALE SCHEDULE & REVISED LAKE METRICS"
    ws1["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    ws1["A1"].fill = navy_fill
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 32

    # Section 1: All Sales Schedule
    ws1.cell(row=3, column=1, value="1. REMAINING SALES SCHEDULE & PAST BUYS (LAST YEAR VS THIS YEAR)").font = font_bold
    sched_headers = ["County", "2026 Sale Date", "Status", "Last Year Won (Certs)", "Last Year Won ($)", "This Year Bid / Upload", "This Year Won / Target ($)"]
    ws1.append([]) # row 4 blank
    ws1.append(sched_headers) # row 5
    for c in range(1, len(sched_headers)+1):
        cell = ws1.cell(row=5, column=c)
        cell.font = font_header
        cell.fill = dark_fill
        cell.alignment = Alignment(horizontal="center" if c in [1, 2, 3] else "right", vertical="center")

    sched_rows = [
        ("Kendall", "Mon, Oct 26, 2026", "Completed", 78, 220882.52, "$300,000 Target", 0.0),
        ("Kane", "Mon, Oct 26, 2026", "Completed", 112, 852778.61, "779 certs ($5.90M)", 86466.79),
        ("Lake", "Fri, Nov 13, 2026", "UPCOMING", 853, 6131470.62, "5,011 filtered pool", 2000000.0),
        ("DuPage", "Thu, Nov 19, 2026", "UPCOMING", 32, 254027.42, "Awaiting List", 1500000.0),
        ("McHenry", "Mon, Nov 23, 2026", "UPCOMING", 180, 1452829.45, "Awaiting List", 1000000.0),
        ("Will", "Tue, Dec 01, 2026", "UPCOMING", 240, 1457090.96, "Awaiting List", 2000000.0),
    ]

    for r_idx, r in enumerate(sched_rows, start=6):
        ws1.append(list(r))
        ws1.row_dimensions[r_idx].height = 20
        for c in range(1, 8):
            cell = ws1.cell(row=r_idx, column=c)
            cell.font = font_normal
            cell.border = thin_border
            if c in [5, 7] and isinstance(cell.value, (int, float)):
                cell.number_format = '$#,##0.00'

    # Section 2: Lake County Revised Breakdown per Jay's Specifications
    sec2_start = 14
    ws1.cell(row=sec2_start, column=1, value="2. LAKE COUNTY 2026 REVISED BREAKDOWN (PER JAY'S SPECIFICATIONS)").font = font_bold
    lake_headers = ["Category / Segment", "Cert Count", "% of List", "Total Dollar Amount", "% of Dollars", "Average Cert Size", "Jay's Strategy / Workload Impact"]
    ws1.cell(row=sec2_start+1, column=1).value = ""
    for c, h in enumerate(lake_headers, start=1):
        cell = ws1.cell(row=sec2_start+2, column=c, value=h)
        cell.font = font_header
        cell.fill = navy_fill
        cell.alignment = Alignment(horizontal="center" if c in [2, 3, 5] else "left", vertical="center")
    ws1.row_dimensions[sec2_start+2].height = 24

    tot_amt = sum(r['tax_due'] for r in comm_certs + res_certs + removed_under_3k)
    kept_tot = sum(r['tax_due'] for r in comm_certs + res_certs)
    comm_tot = sum(r['tax_due'] for r in comm_certs)
    res_tot = sum(r['tax_due'] for r in res_certs)
    rem_tot = sum(r['tax_due'] for r in removed_under_3k)

    breakdown_rows = [
        ("Original Full County List", len(rows), "100.0%", tot_amt, "100.0%", tot_amt/len(rows), "Raw published list from Lake County Collector"),
        ("REMOVED: Full Installments < $3,000", len(removed_under_3k), f"{len(removed_under_3k)/len(rows):.1%}", rem_tot, f"{rem_tot/tot_amt:.1%}", rem_tot/len(removed_under_3k), "CUTS 1,067 FILING HEADACHES; loses only 3.0% of dollars!"),
        ("REVISED FILTERED POOL (Jay's Base)", len(comm_certs) + len(res_certs), f"{(len(comm_certs)+len(res_certs))/len(rows):.1%}", kept_tot, f"{kept_tot/tot_amt:.1%}", kept_tot/(len(comm_certs)+len(res_certs)), "Clean, high-margin pool to deploy $2.0M target"),
        ("  • Commercial & Industrial Sub-Pool", len(comm_certs), f"{len(comm_certs)/len(rows):.1%}", comm_tot, f"{comm_tot/tot_amt:.1%}", comm_tot/len(comm_certs), "Top priority: high ticket size ($16.7k avg) & bank-backed"),
        ("  • Residential & Other Sub-Pool", len(res_certs), f"{len(res_certs)/len(rows):.1%}", res_tot, f"{res_tot/tot_amt:.1%}", res_tot/len(res_certs), "Focus on 1/2 installments with Bldg > 2x Land")
    ]

    for r_idx, r in enumerate(breakdown_rows, start=sec2_start+3):
        ws1.append(list(r))
        ws1.row_dimensions[r_idx].height = 20
        for c in range(1, 8):
            cell = ws1.cell(row=r_idx, column=c)
            cell.font = font_bold if r_idx in [sec2_start+3, sec2_start+5] else font_normal
            cell.border = thin_border
            if c == 4: cell.number_format = '$#,##0.00'
            if c == 6: cell.number_format = '$#,##0'
        if r_idx == sec2_start+4:
            for c in range(1, 8): ws1.cell(row=r_idx, column=c).fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        if r_idx == sec2_start+5:
            for c in range(1, 8): ws1.cell(row=r_idx, column=c).fill = green_fill

    # =========================================================================
    # SHEET 2: Full Analysis of Last Year (2025 County Bids & Competitors)
    # =========================================================================
    ws_comp = wb.create_sheet(title="2025 County Bids & Competitors")
    ws_comp.views.sheetView[0].showGridLines = True

    ws_comp.merge_cells("A1:G1")
    ws_comp["A1"] = "FULL HISTORICAL ANALYSIS — LAST YEAR (2025) AUCTIONS & COMPETITOR BREAKDOWN"
    ws_comp["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    ws_comp["A1"].fill = navy_fill
    ws_comp["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws_comp.row_dimensions[1].height = 32

    # Table 2A: Jennings 2025 Winning Bid Rates by County
    ws_comp.cell(row=3, column=1, value="A. JENNINGS REALTY — LAST YEAR (2025 AUCTIONS) EXACT WINNING BID RATES BY COUNTY").font = font_bold
    headers_2a = ["County", "Certs Won", "Total Capital Won", "Weighted Avg Bid", "Dominant Winning Rate", "Rate Range", "Market Dynamics"]
    ws_comp.cell(row=4, column=1).value = ""
    for c, h in enumerate(headers_2a, start=1):
        cell = ws_comp.cell(row=5, column=c, value=h)
        cell.font = font_header
        cell.fill = dark_fill
        cell.alignment = Alignment(horizontal="center" if c in [2, 4, 5, 6] else "left", vertical="center")
    ws_comp.row_dimensions[5].height = 24

    data_2a = [
        ("Lake", 853, 6131470.62, 0.0184, "2% (67% of certs)", "1% - 3%", "Jennings dominated #1; 90% of >=$10k went at 2%-3%"),
        ("Will", 240, 1457090.96, 0.0152, "1% (71% of certs)", "1% - 3%", "Aggressive 1% bidding secured logistics & commercial"),
        ("McHenry", 180, 1452829.45, 0.0199, "2% (89% of certs)", "1% - 3%", "Clean 2% bidding dominated retail/commercial corridors"),
        ("Kane", 112, 852778.61, 0.0305, "3% (77% of certs)", "2% - 7%", "Jennings won $853k at 3% (before Bridge 5% sweep this year)"),
        ("DuPage", 32, 254027.42, 0.0200, "2% (100% of certs)", "2% - 2%", "High-equity select items; 100% won at 2.0% flat"),
        ("Kendall", 78, 220882.52, 0.0328, "3% (96% of certs)", "3% - 4%", "Won 78 items at 3% (vs $0 won this year)"),
        ("Peoria", 193, 932974.94, 0.0343, "2% (82% of certs)", "1% - 5%", "Downstate high-yield allocation"),
        ("Grundy", 133, 491604.67, 0.0099, "1% (83% of certs)", "0% - 3%", "83% won at 1% or lower"),
        ("DeKalb", 82, 427803.24, 0.0388, "4% (63% of certs)", "2% - 5%", "Selective higher-rate wins"),
        ("McLean", 69, 347346.09, 0.0205, "2% (97% of certs)", "2% - 3%", "97% won at 2% flat"),
        ("LaSalle", 65, 321295.23, 0.0196, "2% (94% of certs)", "1% - 2%", "94% won at 2% flat")
    ]

    for r_idx, r in enumerate(data_2a, start=6):
        ws_comp.append(list(r))
        ws_comp.row_dimensions[r_idx].height = 20
        for c in range(1, 8):
            cell = ws_comp.cell(row=r_idx, column=c)
            cell.font = font_normal
            cell.border = thin_border
            if c == 3: cell.number_format = '$#,##0.00'
            if c == 4: cell.number_format = '0.00%'

    # Total row for 2A
    tot_2a_row = len(data_2a) + 6
    ws_comp.cell(row=tot_2a_row, column=1, value="TOTAL ALL COUNTIES (2025):").font = font_bold
    ws_comp.cell(row=tot_2a_row, column=2, value="=SUM(B6:B" + str(tot_2a_row-1) + ")").font = font_bold
    ws_comp.cell(row=tot_2a_row, column=3, value="=SUM(C6:C" + str(tot_2a_row-1) + ")").font = font_bold
    ws_comp.cell(row=tot_2a_row, column=3).number_format = '$#,##0.00'
    ws_comp.cell(row=tot_2a_row, column=4, value="2.01%").font = Font(name="Calibri", size=11, bold=True, color="166534")
    ws_comp.cell(row=tot_2a_row, column=5, value="OVERALL WEIGHTED AVG").font = font_bold

    # Table 2B: Lake County 2025 Competitor Breakdown
    sec2b_start = tot_2a_row + 3
    ws_comp.cell(row=sec2b_start, column=1, value="B. LAKE COUNTY 2025 AUCTION — WHO WON WHAT ('THE BIG GUYS')").font = font_bold
    headers_2b = ["Competitor / Tax Buyer", "Buyer Code", "Certs Won", "Total Capital Won", "% of Sale $", "Weighted Avg Bid %", "Strategic Notes"]
    for c, h in enumerate(headers_2b, start=1):
        cell = ws_comp.cell(row=sec2b_start+1, column=c, value=h)
        cell.font = font_header
        cell.fill = navy_fill
        cell.alignment = Alignment(horizontal="center" if c in [2, 3, 5, 6] else "left", vertical="center")
    ws_comp.row_dimensions[sec2b_start+1].height = 24

    data_2b = [
        ("Central Buyer Corp (Jennings)", "148", 853, 6131470.62, 0.3007, 0.0168, "#1 BUYER IN COUNTY: Dominated 30.1% of entire $20.4M auction"),
        ("Private Equity Group LLC (Bridge)", "25014", 424, 2994604.65, 0.1469, 0.0204, "#2 Buyer: Bridge bought $3.0M at 2.04% avg (not 5%!)"),
        ("American Tax Lien LLC", "25003", 284, 2837985.99, 0.1392, 0.0226, "#3 Buyer: Aggressive commercial buyer averaging 2.26%"),
        ("Ari Bass (Personal / Raven)", "25015", 88, 1295766.90, 0.0636, 0.0285, "Large-ticket cherry picker averaging 2.85%"),
        ("Central Region Tax Auction, LLC", "25011", 227, 1314073.02, 0.0645, 0.0145, "Ultra-low rate volume buyer averaging 1.45%"),
        ("Custom Corp (Brian)", "25007", 72, 1271892.27, 0.0624, 0.0341, "Selective high-dollar buyer averaging 3.41%"),
        ("Newline Holdings LLC", "25016", 157, 896335.23, 0.0440, 0.0233, "Mid-tier residential buyer averaging 2.33%"),
        ("Barringlen, Inc", "25008", 60, 780652.53, 0.0383, 0.0344, "Local selective buyer averaging 3.44%")
    ]

    for r_idx, r in enumerate(data_2b, start=sec2b_start+2):
        ws_comp.append(list(r))
        ws_comp.row_dimensions[r_idx].height = 20
        for c in range(1, 8):
            cell = ws_comp.cell(row=r_idx, column=c)
            cell.font = font_bold if r_idx == sec2b_start+2 else font_normal
            cell.border = thin_border
            if c == 4: cell.number_format = '$#,##0.00'
            if c in [5, 6]: cell.number_format = '0.00%'
        if r_idx == sec2b_start+2:
            for c in range(1, 8): cell.fill = green_fill

    # =========================================================================
    # Detailed Item Sheets
    # =========================================================================
    def populate_items(ws, title, items):
        ws.views.sheetView[0].showGridLines = True
        ws.merge_cells("A1:I1")
        ws["A1"] = title
        ws["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
        ws["A1"].fill = navy_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 30

        headers = ["PIN", "Taxpayer / Business Name", "City", "Township", "Property Class", "Tax Due ($)", "Assessed Bldg ($)", "Bldg/Land Ratio", "Installment Status"]
        ws.append([])
        ws.append(headers)
        ws.row_dimensions[3].height = 24
        for c, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=c, value=h)
            cell.font = font_header
            cell.fill = navy_fill
            cell.alignment = Alignment(horizontal="center" if c in [1, 8, 9] else "left", vertical="center")

        for r_idx, item in enumerate(items, start=4):
            ws.append([
                item["pin"], item["taxpayer"], item["city"], item["township"], item["property_type"],
                item["tax_due"], item["asmt_bldg"], item["bldg_land_ratio"], item["installment_status"]
            ])
            ws.row_dimensions[r_idx].height = 19
            for c in range(1, 10):
                cell = ws.cell(row=r_idx, column=c)
                cell.font = font_normal
                cell.border = thin_border
                if r_idx % 2 == 0: cell.fill = alt_row_fill

            ws.cell(row=r_idx, column=1).alignment = Alignment(horizontal="center")
            ws.cell(row=r_idx, column=6).number_format = '$#,##0.00'
            ws.cell(row=r_idx, column=7).number_format = '$#,##0'
            ws.cell(row=r_idx, column=8).number_format = '0.0"x"'
            ws.cell(row=r_idx, column=9).alignment = Alignment(horizontal="center")
            if item["is_half"]: cell.fill = purple_fill

    # Sheet 3: Commercial & Industrial (487 certs)
    ws3 = wb.create_sheet(title="Commercial & Industrial (487)")
    populate_items(ws3, "LAKE COUNTY 2026 — COMMERCIAL & INDUSTRIAL SEGMENT (487 CERTS · $8,152,465)", comm_certs)

    # Sheet 4: Residential & Other (4,524 certs)
    ws4 = wb.create_sheet(title="Residential & Other (4,524)")
    populate_items(ws4, "LAKE COUNTY 2026 — RESIDENTIAL & OTHER SEGMENT (4,524 CERTS · $29,248,475)", res_certs)

    # Auto-fit column widths across all sheets
    for ws in [ws1, ws_comp, ws3, ws4]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row in [1, 2]: continue
                val_str = str(cell.value or '')
                if len(val_str) > max_len: max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    ws1.column_dimensions["A"].width = 38
    ws1.column_dimensions["G"].width = 45
    ws_comp.column_dimensions["A"].width = 34
    ws_comp.column_dimensions["G"].width = 45

    wb.save(OUTPUT_XLSX)
    print(f"✅ Generated comprehensive Excel workbook with 2025 historical analysis: {OUTPUT_XLSX}")

if __name__ == "__main__":
    build_excel()
