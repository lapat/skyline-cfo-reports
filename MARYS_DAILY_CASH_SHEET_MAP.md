# Architectural Map: Mary's Daily Cash Sheet (`2026 DAILY $.xlsx`)

## 1. The Fundamental Structure & Quirk
Mary's Daily Cash Sheet is **not a standard contiguous table**. It is a visual dashboard laid out in Excel, consisting of **multiple independent side-by-side entity blocks** (e.g., Block 1: J R Mgmt & JRI, Block 2: Tax Buyers, Block 3: RV Parks). 
Each block repeats the header `JENNINGS-- / DAILY CASH SHEET`.

## 2. The Horizontal Misattribution Danger (The "78% Error" Trap)
Because the sheet is broken into vertical mini-blocks, **row labels do not govern the entire physical row**.
- Example: Row 42 might say "TAX BUYER INTEREST" in Column 1 (Block 1).
- But in Column 25 (Block 3), Row 42 might actually be logging a "MORTGAGE PYMT". 
- Mary types the label for Block 3 right next to the data in Block 3 (e.g., Column 24).
- **CRITICAL FIX:** A naive script that reads Column 1's label and applies it to every amount on that row will silently misattribute ~80% of transactions. The parser MUST scan **left-to-right**, tracking the *nearest preceding text label* as the active category for the columns that follow it in that block.

## 3. Row Taxonomy & Categories
The sheet primarily uses four structural prefixes that identify a row as a transaction row (rather than a balance row or a blank spacer):
- **Receipts:** `C/R` (Cash Receipt)
- **Disbursements:** `C/D` (Cash Disbursement), `W/T-OUT`, `W/T-IN`

## 4. Required Parsing Algorithm
Any script analyzing this file (e.g., `extract_cash_flash.py` or `extract_live_tax_activity.py`) MUST implement the following logic:

```python
# 1. Skip the monthly summary block at the bottom
if "BEGINNING BALANCE" in label_str:
    in_summary = True

# 2. Track category dynamically across the row
if is_transaction_row(label):
    current_cat = label
    for col_idx, val in enumerate(row):
        if isinstance(val, str) and val.strip():
            # A new text label was found mid-row! Update the active category for this block.
            if is_transaction_row(val):
                current_cat = val
                continue
        if col_idx in DATA_COLS and isinstance(val, (int, float)) and val != 0:
            # Apply the NEAREST PRECEDING label to this amount, not Column 1's label.
            add_to_ledger(current_cat, col_idx, val)
```

## 5. Balance Rows
Opening and closing balances do not have distinct prefixes. They are identified heuristically: a row where 20+ data columns are populated with non-zero floats, and the absolute sum of the row exceeds $500,000.