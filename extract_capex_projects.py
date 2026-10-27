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
            "name": "The Bluffs MH & RV Resort — 160-Site Expansion (90% MH / 10% RV)",
            "folder": "147",
            "status": "Active Civil Work (Phase 1 Complete)",
            "current_operating_sites": 95,
            "planned_expansion_sites": 160,
            "post_expansion_sites": 255,
            "product_mix": "90% Mobile Home (~144 lots) / 10% RV (~16 pads)",
            "phasing_strategy": "2 to 3 Phases (Phases 2-3 gated by 1st-year home sales velocity to avoid sinking capital into concrete pads)",
            "plan_review_pdf": "source_documents/development_plans/Bluffs Development Plan Review (Oct 6 2026).pdf",
            "engineering_program": {
                "new_sites": 155,
                "single_wide_mh": 81,
                "double_wide_mh": 63,
                "rv_super_sites": 11,
                "gross_acres": 30.0
            },
            "budget": 3800000.0,
            "spent_to_date": 842500.0,
            "pct_complete": 22.2,
            "remaining_budget": 2957500.0,
            "target_completion": "Phase 1: Q1 2027 | Phases 2-3: Sales Velocity Paced",
            "projected_annual_noi": 585000.0,
            "projected_yield": "15.4% Cash-on-Cash",
            "trades": [
                {"trade": "Civil Site Grading & Pad Compaction (Phase 1)", "budget": 250000.0, "spent": 245000.0, "status": "Completed ✅"},
                {"trade": "Primary Underground Electrical Loop", "budget": 320000.0, "spent": 310000.0, "status": "Completed ✅"},
                {"trade": "Sewer Lift Station & Water Main Ties", "budget": 300000.0, "spent": 287500.0, "status": "Under Inspection"},
                {"trade": "Concrete Pads & Infrastructure (Gated by Sales Velocity)", "budget": 1450000.0, "spent": 0.0, "status": "Pending Home Sales"},
                {"trade": "Asphalt Paving & Site Landscaping", "budget": 1480000.0, "spent": 0.0, "status": "Phased"}
            ]
        },
        {
            "id": "madison_rv_expansion",
            "name": "Madison RV Resort — 220-Site RV Expansion (2 Phases)",
            "folder": "143 (RV Resort)",
            "status": "Engineering & Permitting (Mobilization 2027)",
            "current_operating_sites": 95,
            "planned_expansion_sites": 220,
            "post_expansion_sites": 315,
            "product_mix": "100% RV Expansion Pads",
            "phasing_strategy": "2 Distinct Construction Phases",
            "plan_review_pdf": "source_documents/development_plans/Madison Development Plan Review (Oct 6 2026).pdf",
            "engineering_program": {
                "new_sites": 215,
                "phase_1_rv": 88,
                "phase_2_rv": 127,
                "gross_acres": 140.0
            },
            "budget": 3200000.0,
            "spent_to_date": 125000.0,
            "pct_complete": 3.9,
            "remaining_budget": 3075000.0,
            "target_completion": "Phase 1: Late 2027 | Phase 2: 2028",
            "projected_annual_noi": 490000.0,
            "projected_yield": "15.3% Return on Capex",
            "trades": [
                {"trade": "Civil Site Engineering & Environmental Surveying", "budget": 150000.0, "spent": 125000.0, "status": "In Progress"},
                {"trade": "Phase 1 Water/Sewer Utility Extensions (110 Sites)", "budget": 1200000.0, "spent": 0.0, "status": "Pending Mobilization"},
                {"trade": "Phase 2 Electric Loops, Roads & 50-Amp Pedestals (110 Sites)", "budget": 1850000.0, "spent": 0.0, "status": "Phase 2"}
            ]
        },
        {
            "id": "madison_clubhouse_golf",
            "name": "Madison Golf Course & Clubhouse Modernization (Jet Sites B)",
            "folder": "143 (Golf / Jet B)",
            "status": "Separate Financial Statement Entity (Active Interior Framing)",
            "current_operating_sites": "18 Championship Holes",
            "product_mix": "Golf, Pro Shop & Food/Beverage (Separate Profit Centers)",
            "plan_review_pdf": "source_documents/development_plans/Madison Clubhouse Development Plan Review (Oct 7 2026).pdf",
            "engineering_program": {
                "architectural_sheets": 43,
                "existing_rv_sites": 91,
                "golf_holes": 18
            },
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
            "current_operating_sites": 308,
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
