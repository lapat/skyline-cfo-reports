# Comprehensive Company Map: Jennings Realty, Inc. & Affiliates

## Overview & Core Identity
* **Parent / Core Entity:** **Jennings Realty, Inc.**
* **D-U-N-S Number:** `06-849-8252`
* **Address:** 820 Church Street, Suite 200, Evanston, IL 60201
* **Phone:** (847) 328-3600
* **State of Incorporation:** Illinois (File No: 40503854, Inc. Date: 12-22-1960)

Jennings Realty operates as the central management and holding company for a diversified portfolio of real estate assets, private trusts, and alternative investments.

---

## What We Do (Lines of Business)
1. **RV Resorts & Hospitality:** Ownership, development, and operation of high-end RV communities in Florida and other warm-weather markets.
2. **Manufactured Housing / Mobile Home Parks (MHP):** Affordable and lifestyle communities offering lot leases and modular home sales.
3. **Tax Certificate Investments & Collections:** Acquiring, managing, and tracking redemptions on municipal tax liens and held indemnity judgments.
4. **Property Development & Expansion:** Active land acquisition, clubhouse construction, and park expansion (e.g., The Bluffs expansion, Madison projects).

---

## Portfolio Entities & Skyline IFS Mapping

| Entity / Property | Business Type | Skyline IFS ID(s) | Description / Notes |
| :--- | :--- | :--- | :--- |
| **Jennings Realty, Inc.** | Management / Corporate | `1` | Core corporate entity; holds cash, incurs management overhead. |
| **Bay Bayou Florida RV Resort** | RV Resort | `135` | Major flagship RV community in Florida. High cash generator. |
| **Sunkissed Village RV Resort** | RV Resort | `140`, `142` | Modern RV resort operation. |
| **The Bluffs MH & RV Resort** | Hybrid MHP / RV | `147` | Subject to major 2026 expansion and construction. |
| **Madison Community Resort** | RV / Community | `143` | Development / operational community resort. |
| **Park City Mobile Homes, Inc.** | Mobile Home Park | `28`, `205`, `24`, `121`, `26` | Consolidated multi-site manufactured housing operations. |
| **Lakeview Mobile Home Park** | Mobile Home Park | `PLVMH`, `19` | Established manufactured housing community. |
| **Home Sites / Galaxy** | Residential Parcels | `33`, `144`, `145`, `146` | Real estate holdings / residential sites. |
| **Home Sites / Ellis** | Residential Parcels | `38` | Land / single-site holdings. |
| **Barbara Descendant's Trust** | Private Family Trust | `110` | Wealth preservation / holding trust for specific family assets. |
| **Tax Certificate Entities** | Tax Lien Portfolio | `150`, `160`, `180`, `190` | Entities dedicated to municipal tax certificates and redemptions. |
| **Upriver** | RV Resort (Divested) | `49`, `491` | Sold in Q2 2026 (kept for historical reporting). |

---

## Technical & Reporting Ecosystem
1. **Jim Report Viewer (`jenningsreportbot.com`):**
   * Flask-based dashboard served via Railway.
   * Ingests executive reports, runs automated AI parsing, and presents cash flow insights, entity profiles, and red-flag alerts.
2. **The "Flash Report" Pipeline:**
   * Reads Mary's daily cash management workbook (`2026 DAILY $.xlsx`).
   * Produces weekly rolling cash balances, 13-week forecasts, and bank reconciliations.
3. **Skyline Accounting System (SS&C):**
   * Core General Ledger and transactional database (underlying Pervasive SQL / Btrieve engine).
   * Houses `GLDET` (transactions), `GLMAST` (balances), and `CHART` (chart of accounts).
