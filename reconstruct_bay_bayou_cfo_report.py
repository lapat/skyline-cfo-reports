#!/usr/bin/env python3
"""
Reverse-Engineered Mapping Engine: Reconstructing Jim's Bay Bayou CFO Financial Report.

Maps Skyline IFS 135 General Ledger accounts to the exact line items on:
- Page 1: Balance Sheet (June 30, 2026)
- Page 2: Statement of Income and Retained Earnings
- Page 3/4: Detail by Month
- Page 5: Operating Expense Comparative Analysis (% of Revenue)
"""

import sqlite3
import json

DB_PATH = "skyline_live_production.sqlite"

# Line item mappings to Skyline Account Numbers
REVENUE_MAPPING = {
    "RENTAL INCOME-DAILY": ["30000003"],
    "RENTAL INCOME-DAILY-EXPANSION": ["30000011"],
    "RENTAL INCOME-WEEKLY": ["30000004"],
    "RENTAL INCOME-WEEKLY-EXPANSION": ["30000012"],
    "RENTAL INCOME-MONTHLY": ["30000005"],
    "RENTAL INCOME-MONTHLY-EXPANSION": ["30000013"],
    "RENTAL INCOME-2 MONTH": ["30000010"],
    "RENTAL INCOME-2 MONTH-EXPANSION": ["30000014"],
    "RENTAL INCOME-3 MONTH": ["30000009"],
    "RENTAL INCOME-3 MONTH-EXPANSION": ["30000015"],
    "RENTAL INCOME-4 MONTH": ["30000008"],
    "RENTAL INCOME-4 MONTH-EXPANSION": ["30000016"],
    "RENTAL INCOME-5 MONTH": ["30000019"],
    "RENTAL INCOME-5 MONTH-EXPANSION": ["30000017"],
    "RENTAL INCOME-6 MONTH": ["30000006"],
    "RENTAL INCOME-6 MONTH-EXPANSION": ["30000018"],
    "RENTAL INCOME-YEARLY": ["30000007"],
    "RENTAL INCOME-SUNKISSED": ["30000000"],
    "LAUNDRY INCOME": ["30600000"],
    "PROPANE GAS SALES": ["30700000"],
    "SUNDRY INCOME": ["32500000"],
    "STORE INCOME": ["32500004"],
    "CREDIT CARD INCOME": ["32500005"],
    "ELECTRIC INCOME": ["32600000"],
}

EXPENSE_MAPPING = {
    "ADVERTISING": ["40500000"],
    "AUTOMOBILE EXPENSES": ["40600000"],
    "BANK CHARGES": ["41500000"],
    "CABLE TV": ["51600002", "51600003"],
    "COSTS OF GOODS SOLD-STORE": ["40000001"],
    "CREDIT CARD CHARGES": ["41500001", "41500002"],
    "DONATIONS": ["44000000"],
    "DUES AND SUBSCRIPTIONS": ["41900000"],
    "FILING FEES": ["42200000"],
    "INSURANCE": ["46500000"],
    "JANITORIAL SERVICES": ["52000000"],
    "LANDSCAPING": ["51450000"],
    "LICENSES": ["48000000"],
    "MANAGEMENT FEES": ["48600000"],
    "OFFICE SUPPLIES AND EXPENSES": ["49500000"],
    "POSTAGE": ["50000000"],
    "PAYROLL-MAINTENANCE": ["52700000"],
    "PAYROLL-OFFICE & ACTIVITIES": ["52600000"],
    "PROPANE GAS": ["40000000"],
    "PROFESSIONAL FEES": ["48100000"],
    "PROFIT SHARING": ["50100000"],
    "REFUSE REMOVAL": ["51900000"],
    "REPAIRS AND MAINTENANCE": ["51500000", "51500003"],
    "TAXES-PAYROLL": ["54500000", "54600000", "54700000"],
    "TAXES-REAL ESTATE": ["54900000"],
    "TAXES-OTHER": ["54800000"],
    "TELEPHONE": ["55500000"],
    "TRAVEL": ["54000000"],
    "UTILITIES": ["51600001", "51110000"],
}

BALANCE_SHEET_MAPPING = {
    "PROPERTY AND EQUIPMENT": {
        "LAND": ["15900000"],
        "BUILDING AND IMPROVEMENTS": ["16000000", "16100000"],
        "SITES AND IMPROVEMENTS": ["16110000", "16400000"],
        "FURNITURE AND EQUIPMENT": ["16700000", "16700001", "16700002", "16700003", "16700004"],
        "CONCRETE": ["18500000"],
        "VEHICLES": ["16900000"],
        "LESS ACCUMULATED DEPRECIATION": ["16290000", "16410000", "16710000", "16810000", "16910000", "18510000", "18610000", "18710000"]
    },
    "OTHER ASSETS": {
        "CASH": ["10060000", "10070000", "10140000", "10200000", "10210000", "10310000"],
        "LOAN & NOTES RECEIVABLE": ["13000000"],
        "DUE FROM RELATED PARTY": ["11300000"],
        "PROPANE GAS INVENTORY": ["11700000"],
        "STORE INVENTORY": ["11800000"],
        "PREPAID EXPENSES": ["14500000", "14600000"],
        "UNAMORTIZED MORTGAGE ACQUISITION FEES": ["17500000"],
        "DEPOSITS": ["17100000"],
        "GOODWILL": ["19000000"]
    },
    "LIABILITIES": {
        "ACCOUNTS PAYABLE": ["20000000"],
        "ACCRUED EXPENSES": ["23020000", "23030000", "23040000", "23100000"],
        "SALES TAX PAYABLE": ["23000000"],
        "TENANTS' CREDIT BALANCES AND DEPOSITS": ["25300001", "25300003", "25350000"],
        "CURRENT PORTION OF LONG-TERM DEBT": ["21000000"],
        "LONG-TERM DEBT": ["22500000"],
        "MEMBERS EQUITY": ["29300000", "29500000"]
    }
}

def build_map_database():
    conn = sqlite3.connect("bay_bayou_cfo_map.sqlite")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cfo_report_line_mapping (
            report_section TEXT,
            line_item_name TEXT,
            skyline_account_number TEXT,
            account_description TEXT,
            statement_type TEXT,
            sort_order INTEGER,
            PRIMARY KEY (statement_type, line_item_name, skyline_account_number)
        );
    """)

    order = 1
    # Revenues
    for line, accts in REVENUE_MAPPING.items():
        for a in accts:
            conn.execute("INSERT OR REPLACE INTO cfo_report_line_mapping VALUES (?,?,?,?,?,?)",
                         ("REVENUE", line, a, "Skyline GL Account", "INCOME_STATEMENT", order))
        order += 1

    # Expenses
    for line, accts in EXPENSE_MAPPING.items():
        for a in accts:
            conn.execute("INSERT OR REPLACE INTO cfo_report_line_mapping VALUES (?,?,?,?,?,?)",
                         ("OPERATING_EXPENSES", line, a, "Skyline GL Account", "INCOME_STATEMENT", order))
        order += 1

    # Balance Sheet
    for sec, items in BALANCE_SHEET_MAPPING.items():
        for line, accts in items.items():
            for a in accts:
                conn.execute("INSERT OR REPLACE INTO cfo_report_line_mapping VALUES (?,?,?,?,?,?)",
                             (sec, line, a, "Skyline GL Account", "BALANCE_SHEET", order))
            order += 1

    conn.commit()
    count = conn.execute("SELECT count(*) FROM cfo_report_line_mapping").fetchone()[0]
    conn.close()
    print(f"✅ Created bay_bayou_cfo_map.sqlite with {count} mapped line items.")

if __name__ == "__main__":
    build_map_database()
