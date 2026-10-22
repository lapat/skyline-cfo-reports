#!/usr/bin/env python3
"""
Financial Statement Generator for the Top 10 Portfolio Companies.

Aligned with Jim Report Viewer's yearly revenue rankings (LTM) & IFS entity mapping:
1. Park City Mobile Homes, Inc. (IFS: 28, 205, 24, 121, 26)
2. Jennings Realty, Inc. (IFS: 1)
3. Tax Certificate Buying Entities (IFS: 150, 160, 180, 190)
4. Bay Bayou RV Resort (IFS: 135)
5. Home Sites / Galaxy / Jet Sites B (IFS: 33, 144, 145, 146)
6. Sunkissed Village RV Resort LLC (IFS: 140)
7. Lakeview Mobile Home Park (IFS: PLVMH, 19)
8. Madison Community Resort (IFS: 143)
9. Sunkissed RV Sales LLC (IFS: 142)
10. The Bluffs MH & RV Resort (IFS: 147)
"""

import os
import sqlite3
import sys
from typing import Dict, Any, List

# Official Top 10 Companies ranked by yearly revenue (LTM) from Jim Report Viewer
OFFICIAL_TOP_10 = [
    {
        "name": "Park City Mobile Homes, Inc.",
        "ifs_ids": ["28", "205", "24", "121", "26"],
        "jim_yearly_rev": 7816311.00,
        "type": "Manufactured Housing"
    },
    {
        "name": "Jennings Realty, Inc.",
        "ifs_ids": ["1"],
        "jim_yearly_rev": 5985488.00,
        "type": "Corporate / Management"
    },
    {
        "name": "Tax Certificate Buying Entities",
        "ifs_ids": ["150", "160", "180", "190"],
        "jim_yearly_rev": 4697911.00,
        "type": "Tax Lien Portfolio"
    },
    {
        "name": "Bay Bayou RV Resort",
        "ifs_ids": ["135"],
        "jim_yearly_rev": 3135741.00,
        "type": "RV Resort"
    },
    {
        "name": "Home Sites / Galaxy / Jet Sites",
        "ifs_ids": ["33", "144", "145", "146"],
        "jim_yearly_rev": 3161457.00,
        "type": "Residential Parcels"
    },
    {
        "name": "Sunkissed Village RV Resort LLC",
        "ifs_ids": ["140"],
        "jim_yearly_rev": 1933231.00,
        "type": "RV Resort"
    },
    {
        "name": "Lakeview Mobile Home Park",
        "ifs_ids": ["PLVMH", "19"],
        "jim_yearly_rev": 1907064.00,
        "type": "Manufactured Housing"
    },
    {
        "name": "Madison Community Resort",
        "ifs_ids": ["143"],
        "jim_yearly_rev": 949013.00,
        "type": "RV Resort"
    },
    {
        "name": "Sunkissed RV Sales LLC",
        "ifs_ids": ["142"],
        "jim_yearly_rev": 826711.00,
        "type": "Dealership / Sales"
    },
    {
        "name": "The Bluffs MH & RV Resort",
        "ifs_ids": ["147"],
        "jim_yearly_rev": 359000.00,  # Expanding / Major Capital Expansion
        "type": "Hybrid MHP/RV"
    },
]

DEFAULT_SQLITE_PATH = "/Users/louislapat/vibe/skyline/skyline_extract.sqlite"

def generate_company_report(conn: sqlite3.Connection, ifs_ids: List[str]) -> Dict[str, Any]:
    placeholders = ",".join("?" for _ in ifs_ids)
    
    query = f"""
        SELECT
          -SUM(CASE WHEN coa.account_type='08' OR (coa.account_type IS NULL AND je.account LIKE '3%')
                    THEN je.amount ELSE 0 END) AS revenue,
           SUM(CASE WHEN coa.account_type='09' OR (coa.account_type IS NULL AND je.account GLOB '[4-9]*')
                    THEN je.amount ELSE 0 END) AS expenses,
           MIN(je.date) AS start_date,
           MAX(je.date) AS end_date,
           COUNT(*) AS total_entries
        FROM journal_entries je
        LEFT JOIN chart_of_accounts coa ON je.ifs_id=coa.ifs_id AND je.account=coa.account_number
        WHERE je.ifs_id IN ({placeholders}) AND je.date != '000000'
    """
    row = conn.execute(query, ifs_ids).fetchone()
    rev, exp, start_d, end_d, count = row
    rev = rev or 0.0
    exp = exp or 0.0
    net = rev - exp
    margin = (net / rev * 100) if rev > 0 else 0.0

    return {
        "revenue": rev,
        "expenses": exp,
        "net_income": net,
        "margin_pct": margin,
        "start_date": start_d or "N/A",
        "end_date": end_d or "N/A",
        "entry_count": count
    }

def print_top_10_reports(db_path: str = DEFAULT_SQLITE_PATH):
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}", file=sys.stderr)
        return

    conn = sqlite3.connect(db_path)
    
    print("\n" + "=" * 122)
    print(f"{'TOP 10 COMPANIES — RANKED BY YEARLY REVENUE (JIM REPORT VIEWER ALIGNED)':^122}")
    print("=" * 122)
    header = (
        f"{'#':<3} {'Company Name':<34} {'Jim Yearly Rev':>15} "
        f"{'Skyline Rev':>14} {'Skyline Exp':>14} {'Skyline Net':>14} {'Margin':>8}"
    )
    print(header)
    print("-" * 122)

    tot_jim_rev = 0.0
    tot_sky_rev = 0.0
    tot_sky_exp = 0.0
    tot_sky_net = 0.0

    for idx, comp in enumerate(OFFICIAL_TOP_10, 1):
        data = generate_company_report(conn, comp["ifs_ids"])
        
        tot_jim_rev += comp["jim_yearly_rev"]
        tot_sky_rev += data["revenue"]
        tot_sky_exp += data["expenses"]
        tot_sky_net += data["net_income"]
        
        print(
            f"{idx:<3} {comp['name']:<34} {comp['jim_yearly_rev']:>15,.2f} "
            f"{data['revenue']:>14,.2f} {data['expenses']:>14,.2f} {data['net_income']:>14,.2f} "
            f"{data['margin_pct']:>7.1f}%"
        )

    print("-" * 122)
    overall_margin = (tot_sky_net / tot_sky_rev * 100) if tot_sky_rev > 0 else 0.0
    print(
        f"{'':<3} {'TOTAL (TOP 10 PORTFOLIO)':<34} {tot_jim_rev:>15,.2f} "
        f"{tot_sky_rev:>14,.2f} {tot_sky_exp:>14,.2f} {tot_sky_net:>14,.2f} "
        f"{overall_margin:>7.1f}%"
    )
    print("=" * 122 + "\n")
    conn.close()

if __name__ == "__main__":
    print_top_10_reports()
