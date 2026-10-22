# PRIMARY GOAL: GENERATE SKYLINE REPORTS THAT LOOK AS MUCH LIKE JIM'S AS POSSIBLE (100% SKYLINE DATA)
All financial reports generated from Skyline must match the exact visual, structural, and conceptual format of the executive reports produced by our CFO, Jim (from `jenningsreportbot.com` / `Jim Report Viewer`). 
* **100% Skyline Data Mandate:** Every single number, subtotal, balance, and transaction in our financial reports must be derived dynamically from Skyline's General Ledger data (`skyline_live_production.sqlite` / live Btrieve files). Jim's reports serve strictly as the format template (line item ordering, column matrices, grouping, and styling) and for labelled side-by-side prior-year checks, never as the source for Skyline's current figures.
* **Pixel-Perfect Fidelity:** Replicate Jim's multi-column consolidating matrices, departmental segmentations, hospitality metrics, and bank debt covenants so Jay can consume real-time Skyline data with zero learning curve.

# CRITICAL MANDATE: DO NOT DO ANY WRITES TO SKYLINE WITHOUT EXPLICIT USER APPROVAL.

# CORE REPORTING MANDATE: REPLICATE CFO JIM'S EXECUTIVE REPORT FORMATS
The 3-Step Execution Workflow:
1. **Source Document Ingestion:** Retrieve the latest ground-truth PDF financial packages (Balance Sheet, P&L, Cash Flow, Operational Schedules) for every portfolio entity.
2. **Conceptual & Line-by-Line Reverse Engineering:** Store the deep accounting logic, entity business models, and why Jay prefers each format inside `cfo_reports_conceptual_db.sqlite`.
3. **High-Fidelity Programmatic Replication:** Use live Skyline GL data to generate pixel-perfect replica PDFs matching Jim's exact multi-column, consolidating, and hospitality-metric schedules.

# Skyline Auto Project Instructions

## 1. System Architecture & Live Data Paths
* **Live Production Network Share:** Mounted on macOS at `/Volumes/skyline$/Skyline/` (Server: `w16-jennings-psql.techpro.local` at `172.17.21.167`).
* **Underlying Database Engine:** Actian Zen / Pervasive PSQL v13 (Btrieve v9.5).
* **Port Availability:**
  * Port `1583` (Pervasive SQL) and Port `3351` (Btrieve Engine) are reachable, but only `DEMODATA` is registered as a SQL database.
  * Individual properties under `IFS/` do NOT have SQL DSNs configured in Pervasive Control Center (PCC).
  * Skyline operates exclusively by reading and writing raw Btrieve ISAM files across the SMB mapped share.
* **Database Catalog:**
  * `DATA/FILE.DDF`, `DATA/FIELD.DDF`, and `DATA/INDEX.DDF` define table metadata.
  * Total active operating company folders: **347 entities** in `IFS/`.
* **Bank Reconciliation Status:**
  * `CHKTRAN`, `BKSTMTRP`, `CHKXREF`, and `CHKMEMO` are defined in `FILE.DDF` (Table IDs 117, 158, 159, 161), but **zero physical files exist on disk** because the checkbook reconciliation module was never activated.
  * Cash disbursements flow through Accounts Payable (`APDIST`, `APHIST`) and `JOURHIST`.
* **Historical Balances:**
  * 13-month historical account balance buckets exist in `CHARTHST.DAT` (112 bytes per record: 8-byte account + 13 x 8-byte MBF floats).

## 2. High-Speed SMB Transfer Architecture
* **The 70ms Ping & Packet Signing Penalty:**
  * Network latency between macOS and the server is ~70ms. Sequential single-threaded copying (`cp`, Finder) spends 280ms of handshake wait time per file, taking over 20 minutes to copy the enterprise.
  * In addition, `AES_128_CMAC` packet signing is enabled on the SMB connection.
* **The High-Speed Parallel Solution (`fast_skyline_sync.py`):**
  * Uses 16 concurrent worker threads to eliminate latency wait time.
  * Targets only the 5 essential General Ledger tables: `NAMEGL`, `CHART`, `CHARTHST`, `JOURHIST`, `JOURTRAN` (1,771 files vs. 41,000 files).
  * Performs incremental delta syncing based on file modification time and size.
  * Transfers the entire 347-company enterprise (~246 MB) in **under 98 seconds** (a 12.5x speedup).

## 3. Financial Reporting & Statement Standards
* **Local High-Speed Database:** All reporting queries execute against `skyline_live_production.sqlite` (and exported for Claude at `/Users/louislapat/vibe/skyline/skyline_all_companies_gemini.sqlite`).
* **Double-Entry Equilibrium:**
  * P&L: `Revenue` (Account Type `08` / `3xxxxxxx`) minus `Expenses` (Account Type `09` / `4-9xxxxxxx`).
  * Balance Sheet: Every balance sheet must include an explicit **`non_netting_residual` / `Unclassified Ledger Netting Adjustment`** line item so `Total Assets = Total Liabilities + Equity` balances to `$0.00`.
  * Cash Flow: Portfolio cash totals must present gross **positive cash accounts** (bank deposits) and **negative cash accounts** (clearing/overdrafts) separately without netting.
* **Reconciliation Fidelity:**
  * When comparing against Claude's live export (`skyline_reports_all_companies_live.json`), 24 out of 26 core portfolio clusters match **100% down to the exact penny ($0.00 variance)**.
  * Upriver Partners ($59.8M capital proceeds) is categorized as a sale gain, not operating revenue.

## 4. Headless Programmatic Journal Entry Guidelines
* **Safety Isolation:** Testing of GL writes must always take place on a local copy inside a sandbox directory. Never write directly to live production files.
* **Physical Record Encoding:**
  * `JOURHIST` records are 150 bytes fixed length (16-byte record header + 134-byte payload).
  * Currency amounts must be encoded using Microsoft Basic Floating Point (MBF) via `double_to_mbf()`.
  * The File Control Record (FCR) `numRecs` counter at offset 26 must be incremented.
* **Index Synchronization:** Direct byte-level writing modifies data pages, which are immediately recognized by sequential extractors and reporting engines. However, internal B-Tree search indexes remain desynchronized until Skyline's native "File Maintenance -> Rebuild Indexes" is run on that company folder.
