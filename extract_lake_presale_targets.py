#!/usr/bin/env python3
"""
extract_lake_presale_targets.py -- Lake County 2026 Tax Sale Bidding Screener & Optimizer.

Analyzes the 2026 Lake County Tax Sale list (Sale Date: Friday, November 13, 2026):
1. Ingests all 6,078 parcels ($38.56M total delinquent volume).
2. Filters for the High-Yield $10k+ pool (988 parcels / $21.43M volume).
3. Analyzes Building-to-Land ratios to identify bank-protected commercial and improved residential assets.
4. Assigns strategic recommended bid rates (4% on $25k+ to beat Bridge, 5% on $10k-$25k).
5. Models projected 12% statutory subtax carrying returns.
6. Curates an optimal $2,000,000 bidding portfolio for Stan Engelsen and Jay Lapat.
"""

import os
import sys
import csv
import json
import time

SOURCE_CSV = os.path.abspath("data/lake_2026_sale/2026 Lake List 2025 Taxes.csv")
OUTPUT_JSON = os.path.abspath("lake_presale_targets.json")

def process_lake_presale(verbose=True):
    if not os.path.exists(SOURCE_CSV):
        if verbose:
            print(f"❌ Error: {SOURCE_CSV} not found.")
        return {}

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

    for r in rows:
        amt_str = (r.get("Judgment Amount") or "0").replace("$", "").replace(",", "").strip()
        try:
            amt = float(amt_str)
        except Exception:
            amt = 0.0
        total_amount += amt

        bldg = float((r.get("Asmt Bldg") or "0").replace(",", "").strip() or 0)
        land = float((r.get("Asmt Land") or "0").replace(",", "").strip() or 0)
        pin = r.get("Parcel Number") or ""
        msg = r.get("MSG") or "Unknown"
        name = (r.get("Taxpayer Name") or "").strip()
        city = (r.get("Property City") or "").strip()
        addr = (r.get("Property Address 1") or "").strip()
        twp = (r.get("Township") or "").strip()
        if " - " in twp:
            twp = twp.split(" - ")[-1].strip()

        ratio = (bldg / land) if land > 0 else 0.0

        # Classification & Priority
        is_improved = ("Improvement" in msg) or (bldg > 0)
        is_commercial = ("Commercial" in msg) or ("Industrial" in msg)

        # Strategic Recommended Bid %:
        # If >= $25k, bid 4% (beats Bridge at 5% to capture large ticket where 12% subtax makes the money)
        # If $10k - $25k, bid 5% (matches Bridge)
        # If < $10k, bid 6% - 9% (or Do Not Bid)
        if amt >= 25000:
            rec_bid = 0.04
            rec_bid_label = "4% (Outbid Bridge)"
        elif amt >= 10000:
            rec_bid = 0.05
            rec_bid_label = "5% (Standard Selective)"
        else:
            rec_bid = 0.06
            rec_bid_label = "6%+"

        # Projected Subtax Annual Return (12% statutory interest on tax due)
        subtax_annual = amt * 0.12

        # Risk Rating
        if is_commercial and ratio >= 2.0:
            risk = "A+ Prime (Bank Guaranteed)"
            score = 95
        elif ratio >= 2.5:
            risk = "A Prime Residential"
            score = 90
        elif is_improved:
            risk = "B Standard Improved"
            score = 75
        else:
            risk = "C Land / Speculative"
            score = 50

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

    # Sort high-yield targets by Quality Score desc, then Tax Due desc
    all_targets.sort(key=lambda x: (x["quality_score"], x["tax_due"]), reverse=True)

    # Curate optimal $2.0M portfolio
    curated_portfolio = []
    portfolio_spend = 0.0
    for t in all_targets:
        if portfolio_spend + t["tax_due"] <= 2050000:
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
            }
        },
        "curated_2m_portfolio": {
            "parcel_count": len(curated_portfolio),
            "total_spend": round(portfolio_spend, 2),
            "projected_year1_penalty_interest": round(sum(x["tax_due"] * x["rec_bid"] for x in curated_portfolio), 2),
            "projected_subtax_annual_inflow": round(sum(x["subtax_annual_return"] for x in curated_portfolio), 2),
            "parcels": curated_portfolio
        },
        "top_targets": all_targets[:250]
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if verbose:
        print("=" * 80)
        print("✅ LAKE COUNTY 2026 PRE-SALE TARGET SCREENER COMPLETE")
        print(f"  Total List:           {total_parcels:,} parcels (${total_amount:,.2f})")
        print(f"  High-Yield $10k+ Pool: {result['tiers']['high_yield_pool_10k_plus']['count']} parcels (${result['tiers']['high_yield_pool_10k_plus']['total_due']:,.2f})")
        print(f"  Curated $2.0M Plan:   {len(curated_portfolio)} parcels (${portfolio_spend:,.2f})")
        print(f"  Subtax Annual Yield:  +${result['curated_2m_portfolio']['projected_subtax_annual_inflow']:,.2f} / year (12% statutory)")
        print(f"  Saved -> {OUTPUT_JSON}")
        print("=" * 80)

    return result

if __name__ == "__main__":
    process_lake_presale(verbose=True)
