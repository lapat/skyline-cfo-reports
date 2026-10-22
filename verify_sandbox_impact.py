#!/usr/bin/env python3
"""
Verification Script: Evaluates the exact financial impact of our headless GL insert.
Compares the sandbox company (999_TEST) against the production baseline (IFS 147).
"""

import sys
import os
import sqlite3

sys.path.append("/Users/louislapat/vibe/skyline")
import extract_skyline

def main():
    SANDBOX_ROOT = "/Users/louislapat/vibe/google/skyline auto/sandbox/Skyline"
    os.environ["SKYLINE_ROOT"] = SANDBOX_ROOT
    extract_skyline.SKYLINE_ROOT = SANDBOX_ROOT
    extract_skyline.DATA_DIR = os.path.join(SANDBOX_ROOT, "DATA")

    files_by_id, fields_by_id = extract_skyline.load_schema()
    extracted = extract_skyline.extract_company("999_TEST", files_by_id, fields_by_id)

    # Load into in-memory sqlite db to run financial aggregations
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS companies (
            ifs_id TEXT PRIMARY KEY, company_name TEXT, address TEXT, city TEXT, state TEXT, zip_code TEXT
        );
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            ifs_id TEXT, account_number TEXT, account_title TEXT, account_type TEXT, account_level TEXT, account_category TEXT,
            PRIMARY KEY (ifs_id, account_number)
        );
        CREATE TABLE IF NOT EXISTS journal_entries (
            ifs_id TEXT, account TEXT, date TEXT, journal_key TEXT, description TEXT, reference TEXT, amount REAL, voucher_number TEXT, chk_num TEXT, batch_num INTEGER
        );
    """)
    extract_skyline.load_company_into_db(conn, extracted)

    # Baseline from production sqlite
    prod_db = "/Users/louislapat/vibe/skyline/skyline_extract.sqlite"
    prod_conn = sqlite3.connect(prod_db)

    prod_rev = prod_conn.execute("SELECT -SUM(amount) FROM journal_entries WHERE ifs_id='147' AND (account LIKE '3%') AND date != '000000'").fetchone()[0] or 0.0
    prod_exp = prod_conn.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='147' AND (account GLOB '[4-9]*') AND date != '000000'").fetchone()[0] or 0.0
    prod_cash = prod_conn.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='147' AND (account LIKE '10%')").fetchone()[0] or 0.0
    prod_net = prod_rev - prod_exp

    test_rev = conn.execute("SELECT -SUM(amount) FROM journal_entries WHERE ifs_id='999_TEST' AND (account LIKE '3%') AND date != '000000'").fetchone()[0] or 0.0
    test_exp = conn.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='999_TEST' AND (account GLOB '[4-9]*') AND date != '000000'").fetchone()[0] or 0.0
    test_cash = conn.execute("SELECT SUM(amount) FROM journal_entries WHERE ifs_id='999_TEST' AND (account LIKE '10%')").fetchone()[0] or 0.0
    test_net = test_rev - test_exp

    print("=" * 80)
    print("FINANCIAL VERIFICATION OF HEADLESS JOURNAL ENTRY INSERTION")
    print("=" * 80)
    print(f"{'Metric':<25} {'Baseline (IFS 147)':>20} {'Sandbox (IFS 999)':>20} {'Delta':>12}")
    print("-" * 80)
    print(f"{'Revenue':<25} ${prod_rev:>19,.2f} ${test_rev:>19,.2f} ${test_rev - prod_rev:>+11,.2f}")
    print(f"{'Expenses':<25} ${prod_exp:>19,.2f} ${test_exp:>19,.2f} ${test_exp - prod_exp:>+11,.2f}")
    print(f"{'Net Operating Income':<25} ${prod_net:>19,.2f} ${test_net:>19,.2f} ${test_net - prod_net:>+11,.2f}")
    print(f"{'Cash Balance':<25} ${prod_cash:>19,.2f} ${test_cash:>19,.2f} ${test_cash - prod_cash:>+11,.2f}")
    print("-" * 80)

    rev_pass = abs((test_rev - prod_rev) - 1000.00) < 0.01
    cash_pass = abs((test_cash - prod_cash) - 1000.00) < 0.01
    net_pass = abs((test_net - prod_net) - 1000.00) < 0.01
    exp_pass = abs(test_exp - prod_exp) < 0.01

    if rev_pass and cash_pass and net_pass and exp_pass:
        print("✅ ALL TESTS PASSED: Exactly +$1,000 Cash and +$1,000 Revenue recognized!")
        print("   Zero expense impact, zero unintended bleed, double-entry in full balance.")
    else:
        print("❌ VARIANCE NOTED in financial test assertions.")

    conn.close()
    prod_conn.close()

if __name__ == "__main__":
    main()
