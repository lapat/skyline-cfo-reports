#!/usr/bin/env python3
"""
Jim Report Viewer Live Integration Bridge for Skyline Auto.

Automatically ingests the latest email reports, executive narrative summaries,
and attached financial PDFs from /Users/louislapat/vibe/jim report viewer:
1. Scans Jim's 302 email records from data/data.js.
2. Identifies the most recent package sent by Jim DiGiacomo for each of the 12 portfolio entities.
3. Extracts Jim's full written email text (Overview, Financial Highlights, Debt, Distributions, Closing).
4. Copies the latest primary statement PDF into source_documents/ for pixel-perfect Side-by-Side comparison.
5. Saves structured metadata to jim_latest_summaries.json for direct embedding in the executive dashboard.
"""

import os
import sys
import json
import time
import shutil

JIM_VIEWER_DIR = "/Users/louislapat/vibe/jim report viewer"
JIM_DATA_JS = os.path.join(JIM_VIEWER_DIR, "data/data.js")
JIM_PDF_DIR = os.path.join(JIM_VIEWER_DIR, "data/pdfs")
OUTPUT_JSON = os.path.abspath("jim_latest_summaries.json")
SOURCE_DOCS_DIR = os.path.abspath("source_documents")

ENTITY_MAP = {
    "bay_bayou": {
        "keys": ["bay bayou"],
        "primary_pdf_keyword": "BAYBAYOU",
        "default_pdf": "source_documents/BAYBAYOUFINANCIALSTMTS63026.pdf"
    },
    "park_city": {
        "keys": ["park city mobile homes"],
        "primary_pdf_keyword": "PARKCTYSTMT CONSOLIDATING",
        "default_pdf": "source_documents/PARKCTYSTMT CONSOLIDATING FINANCIAL STATEMENTS Q3 07 31 2026.pdf"
    },
    "jennings_realty": {
        "keys": ["jennings realty"],
        "primary_pdf_keyword": "Jennings Realty",
        "default_pdf": "source_documents/Jennings Realty May 28 2026 Q3 FY 2026 Financial Statements.pdf"
    },
    "sunkissed_village": {
        "keys": ["sunkissed village", "sunkissed"],
        "primary_pdf_keyword": "SUNKISSED",
        "default_pdf": "source_documents/SUNKISSEDFINANCIALS63026.pdf"
    },
    "tax_buyers": {
        "keys": ["tax certificate", "tax buyer", "central buyer", "interstate funding"],
        "primary_pdf_keyword": "TAX",
        "default_pdf": "source_documents/COMBINED_TAX_BUYERS_Q1_2026.pdf"
    },
    "the_bluffs": {
        "keys": ["the bluffs"],
        "primary_pdf_keyword": "THEBLUFFS",
        "default_pdf": "source_documents/THEBLUFFSANDLMSITES FINANCIALS2NDQTR2026.pdf"
    },
    "madison": {
        "keys": ["madison"],
        "primary_pdf_keyword": "MADISON",
        "default_pdf": "source_documents/MADISON and JETSITESB FINANCIALSDECEMBER2025.pdf"
    },
    "galaxy_sites": {
        "keys": ["galaxy", "home sites / galaxy", "combined llcs"],
        "primary_pdf_keyword": "GALAXY",
        "default_pdf": "source_documents/GALAXY_SITES_MARCH_2026.pdf"
    },
    "barbara_trust": {
        "keys": ["barbara descendant", "barbara trust"],
        "primary_pdf_keyword": "BARBDESCTR",
        "default_pdf": "source_documents/BARBARA_TRUST_06302025.pdf"
    },
    "lakeview": {
        "keys": ["lakeview", "lake view"],
        "primary_pdf_keyword": "LAKEVIEW",
        "default_pdf": "source_documents/LAKEVIEWFINANCIALS1STQTR2026.pdf"
    },
    "ellis_apartments": {
        "keys": ["ellis"],
        "primary_pdf_keyword": "ELLIS",
        "default_pdf": "source_documents/ELLIS_ST_MARCH_2026.pdf"
    },
    "upriver": {
        "keys": ["upriver"],
        "primary_pdf_keyword": "UPRIVER",
        "default_pdf": "source_documents/UPRIVER_PROCEEDS_MAY_2026.pdf"
    }
}

def sync_jim_reports(verbose=True):
    """Parses Jim Report Viewer data.js and updates jim_latest_summaries.json."""
    if not os.path.exists(JIM_DATA_JS):
        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Jim Report Viewer data.js not found at {JIM_DATA_JS}")
        return {}

    with open(JIM_DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse JSON array
    json_str = content.replace("window.emailDashboardData = ", "").strip().rstrip(";")
    try:
        records = json.loads(json_str)
    except Exception as e:
        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Error parsing Jim Report Viewer data.js: {e}")
        return {}

    os.makedirs(SOURCE_DOCS_DIR, exist_ok=True)
    results = {}

    for ent_id, cfg in ENTITY_MAP.items():
        keys = cfg["keys"]
        matched_records = []
        for r in records:
            c_name = (r.get("company_name") or "").lower()
            subj = (r.get("subject") or "").lower()
            if any(k in c_name or k in subj for k in keys):
                matched_records.append(r)

        matched_records.sort(key=lambda x: x.get("date_received", ""), reverse=True)

        if matched_records:
            top = matched_records[0]
            pdfs = top.get("files", {}).get("statement_pdfs", [])

            # Identify primary statement PDF
            primary_pdf_file = None
            for p in pdfs:
                if cfg["primary_pdf_keyword"].lower() in p.lower():
                    primary_pdf_file = p
                    break
            if not primary_pdf_file and pdfs:
                primary_pdf_file = pdfs[0]

            # Copy PDF to source_documents/ if present in Jim's pdf directory
            copied_pdf_path = cfg["default_pdf"]
            if primary_pdf_file:
                src_pdf = os.path.join(JIM_PDF_DIR, primary_pdf_file)
                if os.path.exists(src_pdf):
                    dest_pdf = os.path.join(SOURCE_DOCS_DIR, primary_pdf_file)
                    try:
                        shutil.copy2(src_pdf, dest_pdf)
                        copied_pdf_path = f"source_documents/{primary_pdf_file}"
                    except Exception:
                        pass

            # Clean and structure Jim's email text paragraphs
            raw_paragraphs = top.get("email_paragraphs", [])
            clean_paragraphs = []
            for p in raw_paragraphs:
                cleaned = p.replace("\r\n", "\n").strip()
                if cleaned and not cleaned.startswith("James A. Adamo, C.P.A."):
                    clean_paragraphs.append(cleaned)

            results[ent_id] = {
                "entity_id": ent_id,
                "company_name": top.get("company_name"),
                "date_display": top.get("date_display"),
                "date_received": top.get("date_received"),
                "subject": top.get("subject"),
                "sender": top.get("sender", "jadamo@jenningsrealtyinc.com"),
                "summary_text": "\n\n".join(clean_paragraphs),
                "paragraphs": clean_paragraphs,
                "primary_pdf": copied_pdf_path,
                "all_attached_pdfs": pdfs,
                "metrics": top.get("metrics", {})
            }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    if verbose:
        print("=" * 80)
        print("✅ JIM REPORT VIEWER LIVE INTEGRATION BRIDGE COMPLETE")
        print(f"  Ingested Jim Reports for {len(results)} / 12 Portfolio Entities")
        print(f"  Saved structured summaries -> {OUTPUT_JSON}")
        print("=" * 80)

    return results

if __name__ == "__main__":
    sync_jim_reports(verbose=True)
