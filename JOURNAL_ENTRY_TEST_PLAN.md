# Headless Skyline Journal Entry Addition: Sandbox Test Plan

## Objective
Scope out a 100% headless, programmatic plan to test adding journal entries directly to Skyline's General Ledger database on an isolated database copy (sandbox). 

> **CRITICAL MANDATE:** Under `GEMINI.md`, NO writes may occur against production Skyline data. All testing is strictly restricted to an isolated sandbox copy. GUI automation is explicitly excluded as impractical.

---

## 1. Why GUI-Free (Headless) Testing Is Required
Manual entry or GUI-driven file imports are challenging to automate in unattended server pipelines. A robust automation pipeline must interact directly with the database engine. In Skyline, this means testing whether we can programmatically insert balanced journal entries into `JOURHIST` / `JOURTRAN` while maintaining file integrity and index synchronization.

---

## 2. Sandbox Setup & Isolation
1. **Directory Duplication:**
   * Create an isolated local sandbox: `/Users/louislapat/vibe/google/skyline auto/sandbox/`
   * Copy the schema definitions (`DATA/FILE.DDF`, `DATA/FIELD.DDF`, `DATA/INDEX.DDF`) to `sandbox/DATA/`.
   * Duplicate one small, isolated company folder (e.g. `IFS/147/` - The Bluffs) to `sandbox/IFS/999_TEST/`.
2. **Read-Only Lock on Source:**
   * Verify that network paths to live data (`S:` / `T:` drives) are inaccessible from the test runner.
3. **Pre-Test Checksums:**
   * Record SHA-256 hashes of `sandbox/IFS/999_TEST/JOURHIST` and `CHART`.

---

## 3. The Two Headless Programmatic Paths to Test

### Path 1: Direct SQL Insert via Pervasive PSQL ODBC (Relational Engine)
* **Concept:** Pervasive PSQL exposes a SQL interface over the Btrieve files using `FILE.DDF` (Table 174 = `JOURHIST`).
* **Implementation:**
  1. Configure a sandbox ODBC DSN pointing to `sandbox/`.
  2. Use `pyodbc` to execute an atomic, balanced transaction:
     ```sql
     -- 1. Debit Cash
     INSERT INTO JOURHIST (ACCOUNT, DATE, JOURNAL_KEY, DESCRIPTION, REFERENCE, AMOUNT, BATCH_NUM, VOUCHER_NUMBER)
     VALUES ('10100000', '261020', 'GJ', 'Headless Test Debit', 'TST01', 1000.00, '99999', '00001');

     -- 2. Credit Revenue
     INSERT INTO JOURHIST (ACCOUNT, DATE, JOURNAL_KEY, DESCRIPTION, REFERENCE, AMOUNT, BATCH_NUM, VOUCHER_NUMBER)
     VALUES ('31000000', '261020', 'GJ', 'Headless Test Credit', 'TST01', -1000.00, '99999', '00001');
     ```
* **What This Tests:**
  * Does the installed Pervasive DSN grant SQL write permissions on `JOURHIST`?
  * Does the Pervasive relational engine automatically update the B-Tree indexes defined in `INDEX.DDF`?

### Path 2: Native Btrieve MicroKernel API Call (Transactional Engine)
* **Concept:** If ODBC is configured read-only by the vendor's DDF catalog, Skyline itself writes to these files via the native Btrieve C library (`wbtrv32.dll` on Windows).
* **Implementation:**
  1. Use Python `ctypes` to bind to `wbtrv32.dll`.
  2. Issue OpCode 2 (`B_INSERT`) passing the packed binary struct matching `JOURHIST`'s 88-byte fixed record layout (Account: 8s, Date: 6s, Key: 2s, Description: 50s, Ref: 5s, Amount: double 8s, etc.).
* **What This Tests:**
  * Bypasses SQL parser restrictions while still allowing the native Pervasive database engine to handle page splits, record locks, and B-Tree index updates safely.

---

## 4. The Critical Synchronized Balance Test: `JOURHIST` vs. `CHART`
In Skyline, the Chart of Accounts (`CHART`) maintains period bucket balance fields:
* `AMOUNT_1` through `AMOUNT_5` (Monthly / Period running balances).

**The Test Hypothesis to Verify:**
1. If we insert an entry into `JOURHIST`, do reporting engines (like ours and Claude's) pick up the transaction immediately? (Yes, because both query `JOURHIST` directly).
2. Does Skyline require `CHART.DAT`'s `AMOUNT_X` field to be incremented at the same time, or does Skyline provide a CLI/database utility (like `GLCONV.BAT` or a trial-balance rebuild) to re-sync `CHART` from `JOURHIST`?

---

## 5. Automated Post-Test Verification & Health Checks
After executing the write on the sandbox copy:
1. **Extraction Test:** Run `extract_skyline.py` against `sandbox/IFS/999_TEST/`. Confirm 2 new rows exist and total debits equal total credits.
2. **Reporting Test:** Run `generate_financial_reports.py`. Confirm Cash increased by `$1,000` and Revenue increased by `$1,000`.
3. **Database Engine Integrity Test:** 
   * Run Pervasive's command-line verification utility on the sandbox files:
     ```cmd
     butil -stat sandbox/IFS/999_TEST/JOURHIST
     butil -recover sandbox/IFS/999_TEST/JOURHIST temp.rec
     ```
   * Confirm that index pointers are 100% valid and the file passes physical structural integrity tests with zero corruption.

---

## 6. Teardown
* Because all testing occurs in `sandbox/`, teardown is simply deleting `sandbox/`. Zero risk to production.
