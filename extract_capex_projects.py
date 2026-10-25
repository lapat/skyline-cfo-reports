#!/usr/bin/env python3
"""
extract_capex_projects.py -- Pillar 3: RV Resort Capex & Expansion ROI Tracker

Tracks:
  1. The Bluffs 50-Site Expansion ($2.4M Budget | $842k Spent | 35% Complete)
  2. Madison Clubhouse & Golf Modernization ($1.25M Budget | $465k Spent | 37% Complete)
  3. Bay Bayou Phase II Proven Expansion ($3.1M Spent | $358k/yr Rev | 11.5% Cash-on-Cash Yield)

Outputs:
  capex_summary.json
"""

import os
import sys
import json
import time

OUTPUT_JSON = os.path.abspath("capex_summary.json")

def generate_capex_summary(verbose=True):
    t0 = time.time()

    projects = [
        {
            "id": "the_bluffs_expansion",
            "name": "The Bluffs MH & RV Resort — 50-Site Expansion",
            "folder": "147",
            "status": "Active Civil Work (Phase 1 Complete)",
            "budget": 2400000.0,
            "spent_to_date": 842500.0,
            "pct_complete": 35.1,
            "remaining_budget": 1557500.0,
            "target_completion": "Q1 2027 (Prior to Peak)",
            "projected_annual_noi": 385000.0,
            "projected_yield": "16.0% Cash-on-Cash",
            "trades": [
                {"trade": "Civil Site Grading & Pad Compaction", "budget": 250000.0, "spent": 245000.0, "status": "Completed ✅"},
                {"trade": "TECO Primary Underground Electrical Loop", "budget": 320000.0, "spent": 310000.0, "status": "Completed ✅"},
                {"trade": "Sewer Lift Station & Water Main Ties", "budget": 300000.0, "spent": 287500.0, "status": "Under Inspection"},
                {"trade": "Concrete Pads & 50-Amp Pedestals", "budget": 680000.0, "spent": 0.0, "status": "Contracted / Pending"},
                {"trade": "Asphalt Paving & Site Landscaping", "budget": 850000.0, "spent": 0.0, "status": "Pending"}
            ]
        },
        {
            "id": "madison_clubhouse_golf",
            "name": "Madison Resort Clubhouse & Golf Modernization",
            "folder": "143, JETB",
            "status": "Active Interior Framing & Irrigation",
            "budget": 1250000.0,
            "spent_to_date": 465200.0,
            "pct_complete": 37.2,
            "remaining_budget": 784800.0,
            "target_completion": "December 2026 (Winter Season)",
            "projected_annual_noi": 145000.0,
            "projected_yield": "11.6% Return on Capex",
            "trades": [
                {"trade": "Championship Fairway Irrigation Pump Station", "budget": 220000.0, "spent": 215000.0, "status": "Completed ✅"},
                {"trade": "Clubhouse Event Center Framing & Roof", "budget": 190000.0, "spent": 180200.0, "status": "Framed ✅"},
                {"trade": "Pro Shop & Restaurant HVAC Replacement", "budget": 80000.0, "spent": 70000.0, "status": "In Progress"},
                {"trade": "Banquet Bar, Kitchen Equipment & FF&E", "budget": 760000.0, "spent": 0.0, "status": "Pending Delivery"}
            ]
        },
        {
            "id": "bay_bayou_expansion",
            "name": "Bay Bayou Flagship Expansion Phase II (Operational)",
            "folder": "135",
            "status": "100% Operational (Proven Cash Generator)",
            "budget": 3100000.0,
            "spent_to_date": 3125369.0,
            "pct_complete": 100.0,
            "remaining_budget": 0.0,
            "target_completion": "Fully Operating",
            "projected_annual_noi": 358395.0,
            "projected_yield": "11.5% Realized Cash-on-Cash",
            "trades": [
                {"trade": "Completed Waterfront RV Sites & Utilities", "budget": 1850000.0, "spent": 1865369.0, "status": "Generating Revenue ✅"},
                {"trade": "Pool Pavilion & Dock Expansion", "budget": 1250000.0, "spent": 1260000.0, "status": "Operational ✅"}
            ]
        }
    ]

    total_capex_budget = sum(p["budget"] for p in projects)
    total_capex_spent = sum(p["spent_to_date"] for p in projects)
    active_capex_remaining = sum(p["remaining_budget"] for p in projects)

    result = {
        "as_of_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_capex_budget": total_capex_budget,
        "total_capex_spent": total_capex_spent,
        "active_capex_remaining": active_capex_remaining,
        "projects": projects
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(result, f, indent=2)

    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] 🏗️ RV Resort Capex & Expansion Tracker generated in {time.time() - t0:.2f}s")
        print(f"  Total Capex Program:    ${total_capex_budget:,.2f}")
        print(f"  Capital Deployed to Date: ${total_capex_spent:,.2f}")
        print(f"  Remaining to Fund:      ${active_capex_remaining:,.2f}")
        print(f"  Saved -> {OUTPUT_JSON}")

    return result

if __name__ == "__main__":
    generate_capex_summary()
