# Skyline Auto: Dynamic CFO Financial Reporting Engine

## Executive Overview
This repository houses the high-speed programmatic reporting engine that extracts General Ledger data from Skyline accounting (Actian Zen / Btrieve v9.5) and replicates the exact visual, structural, and conceptual format of the executive financial packages produced by our CFO, Jim (`jenningsreportbot.com` / `Jim Report Viewer`).

### Core Mandates
* **100% Live Skyline Data Mandate:** Every financial balance, subtotal, and journal transaction is derived dynamically from Skyline's General Ledger (`skyline_live_production.sqlite` / live Btrieve files). Jim's reports serve strictly as the format template (line item ordering, column hierarchies, table styling) and for labelled side-by-side prior-year checks.
* **Pixel-Perfect ReportLab PDF Output:** Matches Jim's exact font hierarchies (Helvetica/Helvetica-Bold), table padding (1–2pt), line borders (0.5pt hairline, 1pt single, 1.5pt double-underlines), landscape consolidating matrices, and banking covenants.
* **Ultra-Fast Parallel Compilation:** Built using Python's `concurrent.futures.ProcessPoolExecutor` to compile all 12 master CFO packages simultaneously across 10 CPU cores in **0.35 seconds**.

---

## Complete Portfolio Coverage: All 12 CFO Replica Packages

| # | Entity / Business | Skyline Folders | Generated Replica PDF | Schedules Replicated |
|---|---|---|---|---|
| **1** | **Bay Bayou RV Resort** | `135` | `pdf_reports/BAY_BAYOU_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **10-Page Master Suite:** 2026 vs. 2025 BS, P&L, 6-Mo Seasonality Wave, OPEX % Rev, Stay Durations, ADR ($56.85), RevPAR ($33.39), Utility Recovery (74.2%). |
| **2** | **Park City Mobile Homes** | `28, 205, 24, 121, 26` | `pdf_reports/PARK_CITY_CFO_CONSOLIDATING_STATEMENTS_REPLICA.pdf` | **7-Column Consolidating Matrix:** Eliminates $36.2M intercompany debt across Mobile Homes, Sales Corp, Plaza Inc, and Manufactured Homes. |
| **3** | **Sunkissed Village RV Resort** | `140, 142` | `pdf_reports/SUNKISSED_VILLAGE_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **5-Page Suite:** 2026 vs. 2025 Comparative P&L, Fixed Asset Schedule, Off-Season Burn Curve, Utility Submetering. |
| **4** | **Madison RV Resort & Golf** | `143, JETB` | `pdf_reports/MADISON_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **3-Page Consolidating Suite:** 4-Col Consolidating BS & 7-Col Multi-Dept P&L segmenting RV Resort vs. Golf Operations vs. Clubhouse Food & Beverage. |
| **5** | **Consolidated Tax Buyers** | `150, 160, 180, 190` | `pdf_reports/TAX_BUYERS_CFO_CONSOLIDATING_STATEMENTS_REPLICA.pdf` | **4-Page Consolidating Package:** Interstate, Central Buyer, Diamond Quest, Union Tax. Byline Bank DSCR 1.81x & $5.51M affiliate loan ceiling. |
| **6** | **Barbara Descendant's Trust** | `110` | `pdf_reports/BARBARA_TRUST_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **3-Page Consolidating Suite:** Consolidating Balance Sheet & Income Statement: Park City Plaza vs. Rental Parcels (North Shore/Bourbonnais) vs. Parent. |
| **7** | **Ellis St Apartments** | `38` | `pdf_reports/ELLIS_APARTMENTS_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **4-Page Multi-Unit Package:** 12-Unit Residential Apartment Package: 100% Occupancy rent roll, Capex additions, and Expense Ratio benchmarks. |
| **8** | **Galaxy Sites, LLC** | `33, 144, 145, 146` | `pdf_reports/GALAXY_SITES_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **2-Page Operations Package:** Real Estate Disposition Pending ($4.40M), 7 Specific Parcel Holdings, and $16.5M Intercompany Note. |
| **9** | **Jennings Realty, Inc.** | `1` | `pdf_reports/JENNINGS_REALTY_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **Corporate Management Suite:** $5.27M fee collections, Poinsettia promissory note ($895K interest), and cash sweeps. |
| **10**| **The Bluffs MH & RV Resort** | `147` | `pdf_reports/THE_BLUFFS_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **Hybrid Community Suite:** MH lot rents vs. seasonal RV resort rentals ($523K revenue). |
| **11**| **Lakeview Mobile Home Park** | `18, PLVMH` | `pdf_reports/LAKEVIEW_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **Manufactured Housing Operations:** Lot rents, pass-throughs, water/sewer ($850K revenue, $411K NOI). |
| **12**| **Upriver Partners LLP** | `49, 491` | `pdf_reports/UPRIVER_CFO_FINANCIAL_REPORT_REPLICA.pdf` | **Divestiture Disposition:** May 27, 2026 Capital Asset Sale: $59.8M gross transaction, $36.9M debt payoff, $22.87M net cash, $12M bank tax-line paydowns. |

---

## Key Breakthroughs & Technical Architecture

1. **The 2.00x Joint Venture Ownership Resolution:**
   - Skyline books 100% of the property-level LLC assets and debt ($4.33M land, $6.25M goodwill, $16.24M Byline mortgage at Bay Bayou).
   - Jim reports Jennings Realty's 50% member interest ($2.165M land, $3.125M goodwill, $8.07M debt). Applying `* 0.50` turns all lines into exact dollar-for-dollar matches.
2. **Prior-Year (2025) Comparatives via `CHARTHST.DAT`:**
   - Decoded 106-byte records in `CHARTHST.DAT` (8-byte account + 12 monthly MBF floats) to supply prior-year comparative columns.
3. **The Rosetta Stone (Unlabelled Accounts Solved):**
   - Reconstructed operational labels for blank Skyline accounts (`30000004` = Weekly, `30000005` = Monthly, `30000011` = Daily Expansion, `32600000` = Electric Pass-Through, `16700004` = Goodwill).
4. **Interactive Pro Visual Guide:**
   - `bay_bayou_cfo_report_explained_pro.html`: Interactive Chart.js visualizations covering Florida seasonality waves, revenue donuts, and the "Why Jay Loves It" operator philosophy.

---

## How to Run

Compile all 12 CFO master packages in parallel across all CPU cores:
```bash
python3 build_all_cfo_replicas_parallel.py
```

Run dynamic Skyline financial query engine:
```bash
python3 skyline_financial_engine.py
```

Generate 78-page master enterprise book:
```bash
python3 build_all_companies_3_statements.py
```
