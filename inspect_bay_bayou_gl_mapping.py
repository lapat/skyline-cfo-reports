#!/usr/bin/env python3
"""
Detailed line-by-line inspection of Bay Bayou (IFS 135) GL accounts 
for the period Jan 1, 2026 to June 30, 2026, comparing against Jim's numbers.
"""

import sqlite3

conn = sqlite3.connect("skyline_live_production.sqlite")

query = """
    SELECT 
        je.account, 
        coa.account_title,
        -SUM(CASE WHEN je.account LIKE '3%' OR coa.account_type='08' THEN je.amount ELSE 0 END) as rev,
         SUM(CASE WHEN je.account GLOB '[4-9]*' OR coa.account_type='09' THEN je.amount ELSE 0 END) as exp,
         count(*)
    FROM journal_entries je
    LEFT JOIN chart_of_accounts coa ON je.ifs_id = coa.ifs_id AND je.account = coa.account_number
    WHERE je.ifs_id = '135' AND je.date >= '260101' AND je.date <= '260630'
    GROUP BY je.account, coa.account_title
    HAVING ABS(rev) > 0.01 OR ABS(exp) > 0.01
    ORDER BY je.account
"""

print(f"{'Account':<12} {'Title':<32} {'Type':<5} {'Amount':>14} {'Entries':>8}")
print("-" * 75)

for acct, title, r, e, n in conn.execute(query).fetchall():
    is_rev = abs(r) > 0.01
    amt = r if is_rev else e
    kind = "REV" if is_rev else "EXP"
    t_str = (title or "(unnamed)").strip()[:30]
    print(f"{acct:<12} {t_str:<32} {kind:<5} ${amt:>13,.2f} {n:>8}")

conn.close()
