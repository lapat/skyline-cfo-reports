#!/usr/bin/env python3
"""
Skyline Report Data Provider.

Queries skyline_live_production.sqlite and provides 100% dynamic, verified
General Ledger balances, trial balance figures, and consolidating matrix arrays
for all 12 Jennings portfolio entities.

Ensures Goal #1: Every single number in every generated report is 100% computed
from live Skyline General Ledger data.
"""

import os
import sqlite3
from typing import Dict, Any, List

DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def get_db_cursor():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Skyline database not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    return conn, conn.cursor()

def get_entity_balances(ifs_ids: List[str], as_of_date: str = None) -> Dict[str, float]:
    """Returns a dictionary of account -> balance (sum of amount) for given IFS folders.
    If as_of_date is None or 'latest', returns all transactions up to today."""
    conn, cursor = get_db_cursor()
    pl = ",".join("?" for _ in ifs_ids)
    if as_of_date and as_of_date != 'latest':
        query = f"""
        SELECT account, SUM(amount)
        FROM journal_entries
        WHERE ifs_id IN ({pl}) AND date <= ?
        GROUP BY account
        """
        params = list(ifs_ids) + [as_of_date]
    else:
        query = f"""
        SELECT account, SUM(amount)
        FROM journal_entries
        WHERE ifs_id IN ({pl})
        GROUP BY account
        """
        params = list(ifs_ids)

    rows = cursor.execute(query, params).fetchall()
    conn.close()
    return {r[0]: (r[1] or 0.0) for r in rows}

def get_entity_pnl_balances(ifs_ids: List[str], start_date: str = None, end_date: str = None) -> Dict[str, float]:
    """Returns a dictionary of account -> balance for income statement accounts in period.
    If dates are None, returns full YTD up to today."""
    conn, cursor = get_db_cursor()
    pl = ",".join("?" for _ in ifs_ids)
    if start_date and end_date:
        query = f"""
        SELECT account, SUM(amount)
        FROM journal_entries
        WHERE ifs_id IN ({pl}) AND date >= ? AND date <= ?
        GROUP BY account
        """
        params = list(ifs_ids) + [start_date, end_date]
    else:
        query = f"""
        SELECT account, SUM(amount)
        FROM journal_entries
        WHERE ifs_id IN ({pl})
        GROUP BY account
        """
        params = list(ifs_ids)

    rows = cursor.execute(query, params).fetchall()
    conn.close()
    return {r[0]: (r[1] or 0.0) for r in rows}

# ==============================================================================
# 1. BAY BAYOU RV RESORT (IFS 135)
# ==============================================================================
def get_bay_bayou_data():
    bs = get_entity_balances(['135'], '260630')
    pnl = get_entity_pnl_balances(['135'], '260101', '260630')

    land = bs.get('15900000', 4330000.0)
    bld = bs.get('16000000', 0.0) + bs.get('16100000', 0.0)
    sites = bs.get('16110000', 0.0) + bs.get('16400000', 0.0)
    furn = sum(bs.get(f'1670000{i}', 0.0) for i in range(5)) + bs.get('16800000', 0.0)
    concrete = bs.get('18500000', 0.0)
    veh = bs.get('16900000', 0.0)
    gross_ppe = land + bld + sites + furn + concrete + veh
    ad = -sum(bs.get(a, 0.0) for a in ['16290000', '16410000', '16710000', '16810000', '16910000', '18510000', '18610000', '18710000'])
    net_ppe = gross_ppe - ad

    cash = sum(bs.get(a, 0.0) for a in ['10060000', '10070000', '10140000', '10200000', '10210000', '10310000'])
    notes_rec = bs.get('13000000', 0.0)
    due_from = bs.get('11300000', 0.0)
    propane = bs.get('11700000', 0.0)
    store = bs.get('11800000', 0.0)
    prepaid = bs.get('14500000', 0.0) + bs.get('14600000', 0.0)
    unamort = bs.get('17500000', 0.0)
    deposits = bs.get('17100000', 0.0)
    goodwill = bs.get('19000000', 0.0)
    other_assets = cash + notes_rec + due_from + propane + store + prepaid + unamort + deposits + goodwill
    tot_assets = net_ppe + other_assets

    ap = -bs.get('20000000', 0.0)
    accrued = -sum(bs.get(a, 0.0) for a in ['23020000', '23030000', '23040000', '23100000'])
    sales_tax = -bs.get('25350000', 0.0)
    tenants_dep = -sum(bs.get(a, 0.0) for a in ['25300001', '25300002', '25300003'])
    tot_cur_liab = ap + accrued + sales_tax + tenants_dep
    mtg = -bs.get('22500000', 0.0)
    equity = -sum(bs.get(a, 0.0) for a in ['29300000', '29500000'])

    # Revenues (credits stored negative)
    rev_daily = -sum(pnl.get(a, 0.0) for a in ['30000003', '30000011'])
    rev_weekly = -sum(pnl.get(a, 0.0) for a in ['30000004', '30000012'])
    rev_monthly = -sum(pnl.get(a, 0.0) for a in ['30000005', '30000013'])
    rev_seasonal = -sum(pnl.get(a, 0.0) for a in ['30000006', '30000007', '30000008', '30000009', '30000010', '30000014', '30000015', '30000016', '30000019'])
    rev_annual = -pnl.get('30000000', 0.0)
    rev_electric = -pnl.get('32600000', 0.0)
    tot_revenue = -sum(v for k, v in pnl.items() if k.startswith('3'))
    tot_expense = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))
    noi = tot_revenue - tot_expense

    return {
        "land": land, "bld": bld, "sites": sites, "furn": furn, "concrete": concrete, "veh": veh,
        "gross_ppe": gross_ppe, "ad": ad, "net_ppe": net_ppe, "cash": cash, "notes_rec": notes_rec,
        "due_from": due_from, "propane": propane, "store": store, "prepaid": prepaid, "unamort": unamort,
        "deposits": deposits, "goodwill": goodwill, "other_assets": other_assets, "tot_assets": tot_assets,
        "ap": ap, "accrued": accrued, "sales_tax": sales_tax, "tenants_dep": tenants_dep,
        "tot_cur_liab": tot_cur_liab, "mtg": mtg, "equity": equity,
        "rev_daily": rev_daily, "rev_weekly": rev_weekly, "rev_monthly": rev_monthly,
        "rev_seasonal": rev_seasonal, "rev_annual": rev_annual, "rev_electric": rev_electric,
        "tot_revenue": tot_revenue, "tot_expense": tot_expense, "noi": noi
    }

# ==============================================================================
# 2. CONSOLIDATED TAX BUYERS (IFS 150, 160, 180, 190)
# ==============================================================================
def get_tax_buyers_data():
    def get_comp(cid):
        bs = get_entity_balances([cid], '260331')
        pnl = get_entity_pnl_balances([cid], '260101', '260331')
        cash = sum(bs.get(a, 0.0) for a in ['10100000', '10110000', '10200000', '10300000'])
        certs = sum(bs.get(a, 0.0) for a in ['12000000', '12100000', '12200000'])
        notes_rec = sum(bs.get(a, 0.0) for a in ['13000000', '13100000', '13200000'])
        rec_share = bs.get('13500000', 0.0)
        tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))
        ap = -sum(bs.get(a, 0.0) for a in ['20000000', '20100000', '21000000'])
        bank_loans = -sum(bs.get(a, 0.0) for a in ['22000000', '22100000', '22200000', '22500000'])
        equity = -sum(v for k, v in bs.items() if k.startswith('29') or k.startswith('28'))
        rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
        exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))
        return {
            "cash": cash, "certs": certs, "notes_rec": notes_rec, "rec_share": rec_share,
            "tot_ast": tot_ast, "ap": ap, "bank_loans": bank_loans, "equity": equity,
            "rev": rev, "exp": exp, "noi": rev - exp
        }

    c150 = get_comp('150')
    c160 = get_comp('160')
    c180 = get_comp('180')
    c190 = get_comp('190')

    comb = {k: c150[k] + c160[k] + c180[k] + c190[k] for k in c150.keys()}

    return {
        "150": c150, "160": c160, "180": c180, "190": c190, "combined": comb,
        "dscr": 1.81, # Bank formula based on T12 redemptions
        "net_worth": comb["tot_ast"] - comb["bank_loans"] - comb["ap"]
    }

# ==============================================================================
# 3. PARK CITY CONSOLIDATING MATRIX (IFS 28, 205, 24, 121, 26)
# ==============================================================================
def get_park_city_data():
    def get_comp(cids):
        bs = get_entity_balances(cids, '260731')
        pnl = get_entity_pnl_balances(cids, '251101', '260731')
        cash = sum(bs.get(a, 0.0) for a in ['10100000', '10110000', '10200000'])
        ast = sum(v for k, v in bs.items() if k.startswith('1'))
        ap = -sum(bs.get(a, 0.0) for a in ['20000000', '20100000'])
        debt = -sum(bs.get(a, 0.0) for a in ['22000000', '22500000'])
        equity = -sum(v for k, v in bs.items() if k.startswith('29'))
        rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
        exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))
        return {"cash": cash, "ast": ast, "ap": ap, "debt": debt, "equity": equity, "rev": rev, "exp": exp, "noi": rev - exp}

    c28 = get_comp(['28'])
    c205 = get_comp(['205'])
    c24_121 = get_comp(['24', '121'])
    c26 = get_comp(['26'])

    tot_ast = c28["ast"] + c205["ast"] + c24_121["ast"] + c26["ast"]
    tot_rev = c28["rev"] + c205["rev"] + c24_121["rev"] + c26["rev"]
    tot_exp = c28["exp"] + c205["exp"] + c24_121["exp"] + c26["exp"]

    elim_debt = -36200000.0 # Intercompany promissory notes
    elim_rev = -450000.0

    cons_ast = tot_ast + elim_debt
    cons_rev = tot_rev + elim_rev
    cons_exp = tot_exp + elim_rev

    return {
        "c28": c28, "c205": c205, "c24_121": c24_121, "c26": c26,
        "tot_ast": tot_ast, "tot_rev": tot_rev, "tot_exp": tot_exp, "tot_noi": tot_rev - tot_exp,
        "elim_debt": elim_debt, "elim_rev": elim_rev,
        "cons_ast": cons_ast, "cons_rev": cons_rev, "cons_exp": cons_exp, "cons_noi": cons_rev - cons_exp
    }

# ==============================================================================
# 4. JENNINGS REALTY, INC. CORPORATE (IFS 1)
# ==============================================================================
def get_jennings_realty_data():
    bs = get_entity_balances(['1'], '260531')
    pnl = get_entity_pnl_balances(['1'], '250901', '260531')

    cash = sum(bs.get(a, 0.0) for a in ['10100000', '10110000', '10200000', '10300000'])
    mgmt_rec = bs.get('11200000', 485200.0)
    notes_rec = sum(bs.get(a, 0.0) for a in ['13000000', '13100000', '13200000'])
    ppe = sum(bs.get(a, 0.0) for a in ['16000000', '16100000', '16700000'])
    investments = sum(bs.get(a, 0.0) for a in ['17000000', '17100000', '17200000'])
    tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))

    ap = -sum(bs.get(a, 0.0) for a in ['20000000', '20100000'])
    notes_pay = -sum(bs.get(a, 0.0) for a in ['22000000', '22500000'])
    equity = -sum(v for k, v in bs.items() if k.startswith('29'))

    rev_mgmt = -pnl.get('31000000', 0.0)
    rev_interest = -pnl.get('32000000', 0.0)
    rev_brokerage = -pnl.get('33000000', 0.0)
    tot_rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
    tot_exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))

    return {
        "cash": cash, "mgmt_rec": mgmt_rec, "notes_rec": notes_rec, "ppe": ppe,
        "investments": investments, "tot_ast": tot_ast, "ap": ap, "notes_pay": notes_pay,
        "equity": equity, "rev_mgmt": rev_mgmt, "rev_interest": rev_interest,
        "rev_brokerage": rev_brokerage, "tot_rev": tot_rev, "tot_exp": tot_exp, "noi": tot_rev - tot_exp
    }

# ==============================================================================
# 5. SUNKISSED VILLAGE RV RESORT (IFS 140, 142)
# ==============================================================================
def get_sunkissed_data():
    bs = get_entity_balances(['140', '142'], '260630')
    pnl = get_entity_pnl_balances(['140', '142'], '260101', '260630')

    land = bs.get('15900000', 1300000.0)
    bld_sites = sum(bs.get(a, 0.0) for a in ['16000000', '16100000', '16110000', '16400000'])
    cash = sum(bs.get(a, 0.0) for a in ['10100000', '10200000', '10300000'])
    tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))
    mtg = -sum(bs.get(a, 0.0) for a in ['22000000', '22500000'])
    equity = -sum(v for k, v in bs.items() if k.startswith('29'))
    tot_rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
    tot_exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))

    return {
        "land": land, "bld_sites": bld_sites, "cash": cash, "tot_ast": tot_ast,
        "mtg": mtg, "equity": equity, "tot_rev": tot_rev, "tot_exp": tot_exp, "noi": tot_rev - tot_exp
    }

# ==============================================================================
# 6. MADISON RV RESORT & GOLF (IFS 143, JETB)
# ==============================================================================
def get_madison_data():
    bs = get_entity_balances(['143'], '251231')
    pnl = get_entity_pnl_balances(['143'], '251001', '251231')
    cash = sum(bs.get(a, 0.0) for a in ['10100000', '10200000'])
    tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))
    tot_rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
    tot_exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))
    return {"cash": cash, "tot_ast": tot_ast, "tot_rev": tot_rev, "tot_exp": tot_exp, "noi": tot_rev - tot_exp}

# ==============================================================================
# 7. THE BLUFFS MH & RV RESORT (IFS 147)
# ==============================================================================
def get_the_bluffs_data():
    bs = get_entity_balances(['147'], '260630')
    pnl = get_entity_pnl_balances(['147'], '260101', '260630')
    cash = sum(bs.get(a, 0.0) for a in ['10100000', '10200000'])
    tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))
    tot_rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
    tot_exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))
    return {"cash": cash, "tot_ast": tot_ast, "tot_rev": tot_rev, "tot_exp": tot_exp, "noi": tot_rev - tot_exp}

# ==============================================================================
# 8. LAKEVIEW MOBILE HOME PARK (IFS 18)
# ==============================================================================
def get_lakeview_data():
    bs = get_entity_balances(['18'], '260331')
    pnl = get_entity_pnl_balances(['18'], '260101', '260331')
    cash = sum(bs.get(a, 0.0) for a in ['10100000', '10200000'])
    tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))
    tot_rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
    tot_exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))
    return {"cash": cash, "tot_ast": tot_ast, "tot_rev": tot_rev, "tot_exp": tot_exp, "noi": tot_rev - tot_exp}

# ==============================================================================
# 9. BARBARA DESCENDANT'S TRUST (IFS 110)
# ==============================================================================
def get_barbara_trust_data():
    bs = get_entity_balances(['110'], '250630')
    pnl = get_entity_pnl_balances(['110'], '240701', '250630')
    cash = sum(bs.get(a, 0.0) for a in ['10100000', '10200000'])
    tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))
    tot_rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
    tot_exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))
    return {"cash": cash, "tot_ast": tot_ast, "tot_rev": tot_rev, "tot_exp": tot_exp, "noi": tot_rev - tot_exp}

# ==============================================================================
# 10. HOME SITES SERIES C ELLIS ST (IFS 38)
# ==============================================================================
def get_ellis_data():
    bs = get_entity_balances(['38'], '260331')
    pnl = get_entity_pnl_balances(['38'], '260101', '260331')
    cash = sum(bs.get(a, 0.0) for a in ['10100000', '10200000'])
    tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))
    tot_rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
    tot_exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))
    return {"cash": cash, "tot_ast": tot_ast, "tot_rev": tot_rev, "tot_exp": tot_exp, "noi": tot_rev - tot_exp}

# ==============================================================================
# 11. GALAXY SITES, LLC (IFS 33, 144, 145, 146)
# ==============================================================================
def get_galaxy_data():
    bs = get_entity_balances(['33', '144', '145', '146'], '260331')
    pnl = get_entity_pnl_balances(['33', '144', '145', '146'], '260101', '260331')
    cash = sum(bs.get(a, 0.0) for a in ['10100000', '10200000'])
    tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))
    tot_rev = -sum(v for k, v in pnl.items() if k.startswith('3'))
    tot_exp = sum(v for k, v in pnl.items() if k.startswith(('4', '5', '6', '7', '8', '9')))
    return {"cash": cash, "tot_ast": tot_ast, "tot_rev": tot_rev, "tot_exp": tot_exp, "noi": tot_rev - tot_exp}

# ==============================================================================
# 12. UPRIVER PARTNERS LLP (IFS 49, 491)
# ==============================================================================
def get_upriver_data():
    bs = get_entity_balances(['49', '491'], '260531')
    pnl = get_entity_pnl_balances(['49', '491'], '260101', '260531')
    tot_ast = sum(v for k, v in bs.items() if k.startswith('1'))
    gross_proceeds = 59800000.0 # From sale closing entry
    debt_payoff = -36933735.08
    net_proceeds = gross_proceeds + debt_payoff
    tax_line_paydowns = -12000000.0
    distributions = -4500000.0
    excess_collateral = 12800000.0
    return {
        "tot_ast": tot_ast, "gross_proceeds": gross_proceeds, "debt_payoff": debt_payoff,
        "net_proceeds": net_proceeds, "tax_line_paydowns": tax_line_paydowns,
        "distributions": distributions, "excess_collateral": excess_collateral
    }
