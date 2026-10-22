#!/usr/bin/env python3
"""
CFO Conceptual Database Builder.

Stores the deep conceptual accounting model, executive rationale (Why Jay Prefers It),
schedule architectures, and line-by-line Skyline GL mappings for all of Jim's reports.
Database: cfo_reports_conceptual_db.sqlite
"""

import os
import sqlite3
import json

DB_PATH = "cfo_reports_conceptual_db.sqlite"

MODELS = [
    {
        "entity_key": "bay_bayou_rv_resort",
        "display_name": "Bay Bayou Florida RV Resort LLC",
        "business_model": "Luxury 302-site RV resort community in Tampa, Florida. High seasonal winter snowbird influx (Oct-Apr) followed by summer off-season. Generates revenue via nightly/weekly/monthly site leases, electric utility submeter reimbursements, propane, store sales, and laundry.",
        "skyline_ifs_ids": ["135"],
        "ground_truth_pdf": "source_documents/BAYBAYOUFINANCIALSTMTS63026.pdf",
        "report_architecture": "Hospitality Unit Economics & Seasonality Matrix (10-Page Suite)",
        "why_jay_loves_it": "1) Separates core property-level NOI ($819.6K) from Byline Bank mortgage interest ($266.8K) and depreciation ($161.6K). 2) Tracks capital expansion ROI by isolating 'Expansion Sites' revenue ($411.6K) from 'Existing Sites' ($1.36M). 3) Provides hotel-industry KPIs: ADR ($56.85) and RevPAR ($33.39) alongside a 6-month seasonal curve (Jan NOI +$359K vs Jun NOI -$41K). 4) Evaluates operational overhead discipline via % of Revenue expense benchmarks (Management Fees: 11.75%, Utilities: 9.88%). 5) Tracks Electric Cost Recovery Ratio (74.2%).",
        "key_metrics": "Occupancy %, Available Sites (9,548/mo), ADR ($56.85), RevPAR ($33.39), Electric Recovery % (74.2%), NOI Margin (42.4%), Management Fee % (11.75%)",
        "schedules": [
            {"page": 1, "title": "Comparative Balance Sheet", "treatment": "Assets vs Liabilities/Equity ($11,140,612). Full YoY comparative."},
            {"page": 2, "title": "Statement of Income and Retained Earnings", "treatment": "Operational revenues & expenses above NOI; financing & non-cash items below NOI."},
            {"page": 3, "title": "Detail by Month (Revenues & Part 1 Expenses)", "treatment": "6-month horizontal schedule (Jan-Jun) by stay duration (Daily, Weekly, Monthly, 2-6 Mo, Annual)."},
            {"page": 4, "title": "Detail by Month (Part 2 Expenses, NOI, Net Income)", "treatment": "6-month monthly operating expense detail and monthly net income."},
            {"page": 5, "title": "Operating Expense Comparative Analysis", "treatment": "Itemized park operations expenses with % of Revenue benchmarks."},
            {"page": 6, "title": "Occupancy by Length of Stay", "treatment": "Matrix of occupied nights across expansion vs original site tiers."},
            {"page": 7, "title": "Occupancy Summary Matrix", "treatment": "Contract duration summary nights (35,697 total nights)."},
            {"page": 8, "title": "Monthly Site Utilization Tracking", "treatment": "Unit night utilization (308 units x days) and TTM occupancy % (58.2%)."},
            {"page": 9, "title": "Hospitality ADR & RevPAR Analysis", "treatment": "Average Daily Rate and RevPAR with YoY variance (+3.58 ADR, -2.12 RevPAR)."},
            {"page": 10, "title": "Utility Recovery Detail", "treatment": "Water & Electric costs vs tenant electric billing ($190.8K vs $96.8K = 74.2%)."}
        ]
    },
    {
        "entity_key": "park_city_mobile_homes",
        "display_name": "Park City Mobile Homes, Inc. & Subsidiaries",
        "business_model": "Large-scale consolidated manufactured housing community, retail plaza commercial center, and home sales dealership in Illinois. Operates 4 subsidiaries: Mobile Homes (community lot rents), Plaza Inc (commercial retail center), Sales Corp (dealership/modular home sales), and Manufactured Homes Inc.",
        "skyline_ifs_ids": ["28", "205", "24", "121", "26"],
        "ground_truth_pdf": "source_documents/PARKCTYSTMT CONSOLIDATING FINANCIAL STATEMENTS Q3 07 31 2026.pdf",
        "report_architecture": "7-Column Consolidating Multi-Entity Matrix",
        "why_jay_loves_it": "1) Presents each operating subsidiary side-by-side in separate columns (Park City Mobile Homes, Home Sales Corp, Plaza Inc, Manufactured Homes Inc). 2) Eliminates massive intercompany transfers ($36M+ in notes receivable/payable, internal lot rents, and intercompany fees) in an explicit 'ELIMINATIONS' column. 3) Arrives at the true external 'CONSOLIDATED' economic reality ($1.82M net rental income, $96.7M total assets). 4) Allows Jay to assess the retail strip plaza's health independently from the mobile home park and home sales division.",
        "key_metrics": "Sub-Entity Standalone Revenue, Intercompany Eliminations Total, Consolidated External Revenue, Gross Margin on Home Sales, Plaza Retail Occupancy",
        "schedules": [
            {"page": 1, "title": "Consolidating Balance Sheet (Assets)", "treatment": "7 columns: 4 entities + Total + Eliminations + Consolidated ($95.8M)."},
            {"page": 2, "title": "Consolidating Balance Sheet (Liabilities & Equity)", "treatment": "Current liabilities, long-term debt, and intercompany debt eliminations."},
            {"page": 3, "title": "Consolidating Income Statement", "treatment": "Rentals, mobile home sales, operating expenses, and consolidated net income."}
        ]
    },
    {
        "entity_key": "sunkissed_village_rv_resort",
        "display_name": "Sunkissed Village RV Resort LLC",
        "business_model": "Modern premier RV resort community located in Summerfield/The Villages, Florida market. Focuses on premium luxury RV lots, active retirement snowbird lifestyle, resort amenities, and separate RV sales dealership.",
        "skyline_ifs_ids": ["140", "142"],
        "ground_truth_pdf": "source_documents/SUNKISSEDFINANCIALS63026.pdf",
        "report_architecture": "Seasonal RV Resort P&L, Fixed Asset Schedule & Cash Flow Worksheet",
        "why_jay_loves_it": "1) Breaks out Back-In vs Pull-Through luxury site premium rates. 2) Tracks fixed asset capital additions quarter-by-quarter (clubhouse upgrades, pool improvements, electrical pedestal additions). 3) Includes an explicit Cash Flow Worksheet reconciling operational cash burn during off-season months against peak winter deposit collections.",
        "key_metrics": "Luxury Site Occupancy, Fixed Asset Additions, Ancillary Resort Income, Working Capital Cash Flow",
        "schedules": [
            {"page": 1, "title": "Balance Sheet", "treatment": "Comparative property assets, loan debt, and partners' capital."},
            {"page": 2, "title": "Statement of Income and Retained Earnings", "treatment": "Resort operating revenues, park operating expenses, and net operating income."},
            {"page": 3, "title": "Cash Flow Worksheet", "treatment": "Quarterly operational cash flow, debt repayments, and capital investments."}
        ]
    },
    {
        "entity_key": "jennings_realty_inc",
        "display_name": "Jennings Realty, Inc. (Parent Holding & Management)",
        "business_model": "Parent management company and corporate nerve center. Earns recurring management fees (e.g. 11.75% fee on Bay Bayou, fees across portfolio) and earns interest income on large intercompany debt facilities (e.g. note from Poinsettia). Houses executive management overhead and brokerage operations.",
        "skyline_ifs_ids": ["1", "PJRI", "FM1", "FM2", "FMGMT", "PMGMT"],
        "ground_truth_pdf": "source_documents/Jennings Realty May 28 2026 Q3 FY 2026 Financial Statements.pdf",
        "report_architecture": "Management Company Operating Statement & Debt Facility Schedule",
        "why_jay_loves_it": "1) Isolates management fee collections ($5M+ annually) across all managed properties, showing which properties pay on time. 2) Explicitly strips out quarterly non-cash accrual true-ups ('Accrued', 'RECEIPT OF', 'QTR') so Jay sees real cash management earnings. 3) Reconciles large intercompany interest receivables that power corporate liquidity.",
        "key_metrics": "Total Management Fees Charged, Intercompany Interest Earned, Corporate Overhead Ratio, Cash Sweep Account Balances",
        "schedules": [
            {"page": 1, "title": "Balance Sheet", "treatment": "Cash sweep accounts, intercompany notes receivable ($13M+), and corporate equity."},
            {"page": 2, "title": "Statement of Income & Retained Earnings", "treatment": "Management fees by property, interest income, corporate operating expenses, and net profit."}
        ]
    },
    {
        "entity_key": "the_bluffs_mh_rv_resort",
        "display_name": "The Bluffs MH and RV Resort LLC",
        "business_model": "Hybrid manufactured housing and RV resort community in Michigan undergoing major capital expansion and utility infrastructure development.",
        "skyline_ifs_ids": ["147"],
        "ground_truth_pdf": "source_documents/THEBLUFFSANDLMSITES FINANCIALS2NDQTR2026.pdf",
        "report_architecture": "Capital Expansion & Hybrid Community Financial Statement",
        "why_jay_loves_it": "1) Blends stable long-term MH lot lease revenue with seasonal RV guest revenue. 2) Directly tracks expansion infrastructure expenditures and construction in progress. 3) Reconciles utility billing against municipal water/electric accounts.",
        "key_metrics": "MH Lot Lease Revenue, Seasonal RV Revenue, Expansion Capital Spend, Infrastructure Utility Recovery",
        "schedules": [
            {"page": 1, "title": "Balance Sheet", "treatment": "Fixed assets under construction, operating debt, and partners' equity."},
            {"page": 2, "title": "Operating Statement", "treatment": "MH rent roll vs RV rental income and park maintenance expenses."}
        ]
    }
]

def build_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS entities_conceptual_model (
            entity_key TEXT PRIMARY KEY,
            display_name TEXT,
            business_model TEXT,
            skyline_ifs_ids TEXT,
            ground_truth_pdf TEXT,
            report_architecture TEXT,
            why_jay_loves_it TEXT,
            key_metrics TEXT
        );
        CREATE TABLE IF NOT EXISTS cfo_report_schedules (
            entity_key TEXT,
            page_number INTEGER,
            schedule_title TEXT,
            accounting_treatment TEXT,
            PRIMARY KEY (entity_key, page_number)
        );
    """)

    for m in MODELS:
        conn.execute("""
            INSERT OR REPLACE INTO entities_conceptual_model VALUES (?,?,?,?,?,?,?,?)
        """, (
            m["entity_key"],
            m["display_name"],
            m["business_model"],
            json.dumps(m["skyline_ifs_ids"]),
            m["ground_truth_pdf"],
            m["report_architecture"],
            m["why_jay_loves_it"],
            m["key_metrics"]
        ))

        for s in m["schedules"]:
            conn.execute("""
                INSERT OR REPLACE INTO cfo_report_schedules VALUES (?,?,?,?)
            """, (m["entity_key"], s["page"], s["title"], s["treatment"]))

    conn.commit()
    count_e = conn.execute("SELECT count(*) FROM entities_conceptual_model").fetchone()[0]
    count_s = conn.execute("SELECT count(*) FROM cfo_report_schedules").fetchone()[0]
    conn.close()

    print("=" * 80)
    print("CFO CONCEPTUAL DATABASE BUILT!")
    print(f"  Entities Modeled: {count_e}")
    print(f"  Schedules Documented: {count_s}")
    print(f"  Database Path: {os.path.abspath(DB_PATH)}")
    print("=" * 80)

if __name__ == "__main__":
    build_db()
