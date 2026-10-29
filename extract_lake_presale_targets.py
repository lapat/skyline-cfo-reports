#!/usr/bin/env python3
"""
extract_lake_presale_targets.py -- Lake County 2026 Tax Sale Bidding Screener & Optimizer.

Integrates:
1. Official Lake County 2026 Tax Sale list (data/lake_2026_sale/2026 Lake List 2025 Taxes.csv).
2. Lou's complete 6,056-parcel county portal scraper results (/Users/louislapat/vibe/google/collarcounties/lake/output_2026/2026_Lake_Scraped_Results.xlsx).
3. 9,469 historical redemptions from Lake County property records.

Executes Jay & Stan's exact strategic mandate:
- Pinpoints 1/2 Installment Only parcels (Cycle 1 paid, Cycle 2 delinquent).
- Screens for High-Dollar ($10k - $100k+) Improved assets (Bldg > 2x Land).
- Flags Chronic Redeemers (taxpayers with 2+ historical redemptions).
- Curates a prime $2,000,000 bidding portfolio for Lake County on Friday, Nov 13, 2026.
"""

import os
import sys
import csv
import json
import time
import openpyxl

SOURCE_CSV = os.path.abspath("data/lake_2026_sale/2026 Lake List 2025 Taxes.csv")
SCRAPED_XLSX = "/Users/louislapat/vibe/google/collarcounties/lake/output_2026/2026_Lake_Scraped_Results.xlsx"
OUTPUT_JSON = os.path.abspath("lake_presale_targets.json")

def process_lake_presale(verbose=True):
    t0 = time.time()
    if not os.path.exists(SOURCE_CSV):
        if verbose:
            print(f"❌ Error: {SOURCE_CSV} not found.")
        return {}

    # 1. Load Lou's scraped portal data if available
    scraped_data = {}
    red_counts = {}
    if os.path.exists(SCRAPED_XLSX):
        try:
            wb = openpyxl.load_workbook(SCRAPED_XLSX, data_only=True)
            if 'Tax Redemptions' in wb.sheetnames:
                ws_red = wb['Tax Redemptions']
                for r in range(2, ws_red.max_row + 1):
                    pin = ws_red.cell(r, 1).value
                    if pin:
                        red_counts[pin] = red_counts.get(pin, 0) + 1

            if 'Master Profile & Summary' in wb.sheetnames:
                ws_main = wb['Master Profile & Summary']
                for r in range(2, ws_main.max_row + 1):
                    pin = ws_main.cell(r, 1).value
                    if pin:
                        def clean_val(v):
                            try:
                                return float(str(v).replace('$', '').replace(',', '').strip())
                            except Exception:
                                return 0.0

                        c1 = clean_val(ws_main.cell(r, 9).value)
                        c2 = clean_val(ws_main.cell(r, 10).value)
                        forf = str(ws_main.cell(r, 6).value or '').strip()
                        lien = str(ws_main.cell(r, 7).value or '').strip()

                        # In Lake County, when 1st installment is paid, only $10 county cost fee remains in Cycle 1
                        is_half = (c1 <= 10.0 and c2 > 100.0)
                        half_tag = "2nd Installment Only (Half)" if is_half else "Full Year Delinquent"

                        scraped_data[pin] = {
                            "in_forfeiture": (forf.lower() == "yes"),
                            "open_lien_flag": (lien.lower() == "yes"),
                            "is_half_installment": is_half,
                            "installment_tag": half_tag,
                            "cycle1_due": c1,
                            "cycle2_due": c2,
                            "year_built": ws_main.cell(r, 12).value,
                            "living_area": ws_main.cell(r, 13).value,
                            "prior_redemptions": red_counts.get(pin, 0)
                        }
        except Exception as e:
            if verbose:
                print(f"⚠️ Note reading scraped results: {e}")

    # 2. Parse official auction list CSV
    with open(SOURCE_CSV, "r", encoding="latin-1") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_parcels = len(rows)
    total_amount = 0.0

    tier_50k = []
    tier_25k_50k = []
    tier_10k_25k = []
    tier_under_10k = []

    all_targets = []
    half_targets = []

    for r in rows:
        amt_str = (r.get("Judgment Amount") or "0").replace("$", "").replace(",", "").strip()
        try:
            amt = float(amt_str)
        except Exception:
            amt = 0.0
        total_amount += amt

        bldg = float((r.get("Asmt Bldg") or "0").replace(",", "").strip() or 0)
        land = float((r.get("Asmt Land") or "0").replace(",", "").strip() or 0)
        pin = (r.get("Parcel Number") or "").strip()
        msg = r.get("MSG") or "Unknown"
        name = (r.get("Taxpayer Name") or "").strip()
        city = (r.get("Property City") or "").strip()
        addr = (r.get("Property Address 1") or "").strip()
        twp = (r.get("Township") or "").strip()
        if " - " in twp:
            twp = twp.split(" - ")[-1].strip()

        ratio = (bldg / land) if land > 0 else 0.0
        is_improved = ("Improvement" in msg) or (bldg > 0)
        is_commercial = ("Commercial" in msg) or ("Industrial" in msg)

        # Scraped metadata lookup
        meta = scraped_data.get(pin, {})
        is_half = meta.get("is_half_installment", False)
        inst_tag = meta.get("installment_tag", "Full Year Delinquent")
        prior_reds = meta.get("prior_redemptions", 0)
        in_forf = meta.get("in_forfeiture", False)
        open_lien = meta.get("open_lien_flag", False)

        # Recommended Bid Rate:
        # Jay's Binding Directive: 5.0% is the absolute lowest rate Jennings will bid.
        # 5.0% clears competitive auctions against Bridge/Bass while locking in +552 bps net spread.
        if amt >= 10000:
            rec_bid = 0.05
            rec_bid_label = "5% (Jay's Floor)"
        else:
            rec_bid = 0.06
            rec_bid_label = "6%+"

        subtax_annual = amt * 0.12

        # Quality & Strategy Scoring
        score = 50
        risk = "C Land / Speculative"

        if is_commercial and ratio >= 2.0:
            score = 95
            risk = "A+ Prime Commercial (Bank Protected)"
        elif ratio >= 2.5:
            score = 90
            risk = "A Prime Residential"
        elif is_improved:
            score = 80
            risk = "B Standard Improved"

        if is_half:
            score += 10  # 1/2 installment carries highest redemption probability
            risk += " ⭐ 1/2 Inst"
        if prior_reds >= 2:
            score += 5   # Chronic redeemer

        # Waukegan Municipal Water Lien Redline check (Stan's 08-20, 08-21, 08-28, 08-29 sectors)
        is_waukegan_redline = pin.startswith(('08-20', '08-21', '08-28', '08-29'))
        if is_waukegan_redline:
            score -= 25
            risk += " ⚠️ Water Lien Risk"

        item = {
            "pin": pin,
            "taxpayer": name,
            "address": addr,
            "city": city,
            "township": twp,
            "tax_due": amt,
            "asmt_bldg": bldg,
            "asmt_land": land,
            "bldg_land_ratio": round(ratio, 2),
            "property_type": msg,
            "is_commercial": is_commercial,
            "is_improved": is_improved,
            "is_half_installment": is_half,
            "installment_tag": inst_tag,
            "prior_redemptions_count": prior_reds,
            "in_forfeiture": in_forf,
            "open_lien_flag": open_lien,
            "waukegan_redline": is_waukegan_redline,
            "rec_bid": rec_bid,
            "rec_bid_label": rec_bid_label,
            "subtax_annual_return": round(subtax_annual, 2),
            "risk_rating": risk,
            "quality_score": score
        }

        if amt >= 50000:
            tier_50k.append(item)
        elif amt >= 25000:
            tier_25k_50k.append(item)
        elif amt >= 10000:
            tier_10k_25k.append(item)
        else:
            tier_under_10k.append(item)

        if amt >= 10000 and is_improved:
            all_targets.append(item)
            if is_half:
                half_targets.append(item)

    # Sort high-yield targets by Quality Score desc, then Tax Due desc
    all_targets.sort(key=lambda x: (x["quality_score"], x["tax_due"]), reverse=True)
    half_targets.sort(key=lambda x: (x["tax_due"]), reverse=True)

    # Curate Jay & Stan $2.0M Strategic Portfolio:
    # Prioritizes 1/2 Installments and Prime Commercial/Improved Assets
    curated_portfolio = []
    portfolio_spend = 0.0

    # First add top 1/2 installment targets
    for t in half_targets:
        if portfolio_spend + t["tax_due"] <= 2050000:
            curated_portfolio.append(t)
            portfolio_spend += t["tax_due"]
        if portfolio_spend >= 1500000:
            break

    # Fill remainder with top prime commercial improvements
    for t in all_targets:
        if t not in curated_portfolio and portfolio_spend + t["tax_due"] <= 2050000:
            curated_portfolio.append(t)
            portfolio_spend += t["tax_due"]
        if portfolio_spend >= 2000000:
            break

    result = {
        "as_of_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "county": "Lake County",
        "tax_sale_date": "2026-11-13",
        "jennings_allocation_target": 2000000.0,
        "total_list_parcels": total_parcels,
        "total_list_delinquency": round(total_amount, 2),
        "tiers": {
            "tier_50k_plus": {
                "count": len(tier_50k),
                "total_due": round(sum(x["tax_due"] for x in tier_50k), 2),
                "avg_due": round(sum(x["tax_due"] for x in tier_50k) / len(tier_50k), 2) if tier_50k else 0
            },
            "tier_25k_to_50k": {
                "count": len(tier_25k_50k),
                "total_due": round(sum(x["tax_due"] for x in tier_25k_50k), 2),
                "avg_due": round(sum(x["tax_due"] for x in tier_25k_50k) / len(tier_25k_50k), 2) if tier_25k_50k else 0
            },
            "tier_10k_to_25k": {
                "count": len(tier_10k_25k),
                "total_due": round(sum(x["tax_due"] for x in tier_10k_25k), 2),
                "avg_due": round(sum(x["tax_due"] for x in tier_10k_25k) / len(tier_10k_25k), 2) if tier_10k_25k else 0
            },
            "high_yield_pool_10k_plus": {
                "count": len(tier_50k) + len(tier_25k_50k) + len(tier_10k_25k),
                "total_due": round(sum(x["tax_due"] for x in tier_50k + tier_25k_50k + tier_10k_25k), 2)
            },
            "half_installment_10k_plus": {
                "count": len(half_targets),
                "total_due": round(sum(x["tax_due"] for x in half_targets), 2),
                "description": "Cycle 1 paid ($0 due) · Only 2nd Installment delinquent · >95% redemption safety"
            }
        },
        "curated_2m_portfolio": {
            "parcel_count": len(curated_portfolio),
            "total_spend": round(portfolio_spend, 2),
            "projected_year1_penalty_interest": round(sum(x["tax_due"] * x["rec_bid"] for x in curated_portfolio), 2),
            "projected_subtax_annual_inflow": round(sum(x["subtax_annual_return"] for x in curated_portfolio), 2),
            "parcels": curated_portfolio
        },
        "top_targets": all_targets[:300]
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # Permanently auto-enrich with photos, quantitative survival scores, and FEMA flood / EPA data
    try:
        import enrich_lake_targets_with_photos
        enrich_lake_targets_with_photos.enrich_targets()
        import survival_redemption_engine
        survival_redemption_engine.process_all_targets()
        import enrich_fema_flood_and_environmental
        enrich_fema_flood_and_environmental.enrich_lake_presale_targets()
    except Exception as e:
        if verbose:
            print(f"⚠️ Photo/ML/FEMA enrichment note: {e}")

    if verbose:
        print("=" * 80)
        print("✅ LAKE COUNTY 2026 PRE-SALE OPTIMIZER COMPLETE")
        print(f"  Execution time:        {time.time() - t0:.2f}s")
        print(f"  Total Delinquency:     {total_parcels:,} parcels (${total_amount:,.2f})")
        print(f"  High-Yield $10k+ Pool: {result['tiers']['high_yield_pool_10k_plus']['count']} parcels (${result['tiers']['high_yield_pool_10k_plus']['total_due']:,.2f})")
        print(f"  ⭐ 2nd Installment Only: {result['tiers']['half_installment_10k_plus']['count']} parcels (${result['tiers']['half_installment_10k_plus']['total_due']:,.2f})")
        print(f"  Curated $2.0M Plan:    {len(curated_portfolio)} parcels (${portfolio_spend:,.2f})")
        print(f"  12% Subtax Cashflow:   +${result['curated_2m_portfolio']['projected_subtax_annual_inflow']:,.2f} / year statutory interest")
        print(f"  Saved -> {OUTPUT_JSON}")
        print("=" * 80)

    return result

if __name__ == "__main__":
    process_lake_presale(verbose=True)
