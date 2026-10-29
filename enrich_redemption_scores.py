import json

def calculate_redemption_score(parcel):
    # Base score
    score = 70.0

    # 1. Building-to-land ratio (high equity in improvement = owner/lender never abandons)
    ratio = parcel.get('bldg_land_ratio', 0.0)
    if ratio >= 5.0:
        score += 15.0
    elif ratio >= 3.0:
        score += 12.0
    elif ratio >= 2.0:
        score += 8.0
    elif ratio >= 1.0:
        score += 4.0
    else:
        score -= 5.0

    # 2. Installment status (2nd installment only = 1st was already paid!)
    if parcel.get('is_half_installment'):
        score += 12.0

    # 3. Township historical wealth & redemption tier
    twp = parcel.get('township', '').lower()
    city = parcel.get('city', '').lower()
    
    tier1_twps = ['highland park', 'moraine', 'lake forest', 'shields', 'libertyville', 'vernon', 'buffalo grove', 'lincolnshire', 'fremont', 'mundelein', 'cuba', 'barrington', 'ela', 'lake zurich']
    tier2_twps = ['warren', 'gurnee', 'antioch', 'newport', 'lake villa', 'grant', 'fox lake', 'wauconda']
    
    if any(t in twp or t in city for t in tier1_twps):
        score += 10.0
    elif any(t in twp or t in city for t in tier2_twps):
        score += 5.0

    # 4. Assessed Building Value scale
    bldg = parcel.get('asmt_bldg', 0.0)
    if bldg >= 500000:
        score += 8.0
    elif bldg >= 200000:
        score += 5.0
    elif bldg >= 100000:
        score += 3.0

    # 5. Redline / Caution Penalty
    if parcel.get('waukegan_redline'):
        score -= 40.0
    if 'north chicago' in city or 'north chicago' in twp:
        score -= 35.0

    # Cap score between 40.0% and 99.4%
    final_score = max(40.0, min(99.4, score))
    return round(final_score, 1)

def enrich_targets():
    with open('lake_presale_targets.json') as f:
        data = json.load(f)

    targets = data.get('top_targets', [])
    for t in targets:
        t['redemption_score'] = calculate_redemption_score(t)

    if 'curated_2m_portfolio' in data and 'parcels' in data['curated_2m_portfolio']:
        for t in data['curated_2m_portfolio']['parcels']:
            t['redemption_score'] = calculate_redemption_score(t)

    with open('lake_presale_targets.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Enriched {len(targets)} parcels with quantitative Redemption Certainty Scores!")
    
    # Print sample distribution
    scores = [t['redemption_score'] for t in targets]
    avg_score = sum(scores) / len(scores)
    over_95 = sum(1 for s in scores if s >= 95.0)
    print(f"   Average Redemption Score: {avg_score:.1f}%")
    print(f"   Parcels with >=95.0% Ultra-Certainty: {over_95} / {len(scores)} parcels")

if __name__ == '__main__':
    enrich_targets()
