import json
import urllib.request
import urllib.parse
import time

def enrich_targets():
    with open('lake_presale_targets.json') as f:
        lake_data = json.load(f)

    with open('lake_parcel_geocodes.json') as f:
        geos = json.load(f)

    # 1. Update top_targets
    targets = lake_data.get('top_targets', [])
    updated_count = 0

    for t in targets:
        p_clean = t['pin'].replace('-', '')
        coord = geos.get(p_clean)
        if coord:
            lat = coord['lat']
            lng = coord['lng']
            delta = 0.00055
            min_lng = lng - delta
            max_lng = lng + delta
            min_lat = lat - delta * 0.72
            max_lat = lat + delta * 0.72
            img_url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox={min_lng:.6f},{min_lat:.6f},{max_lng:.6f},{max_lat:.6f}&bboxSR=4326&size=180,120&imageSR=4326&format=jpg&f=image"
            t['lat'] = lat
            t['lng'] = lng
            t['photo_url'] = img_url
            updated_count += 1
        else:
            t['photo_url'] = ""

    print(f"✅ Enriched {updated_count} / {len(targets)} targets with high-resolution satellite house photos!")

    # 2. Also enrich curated_2m_portfolio if present
    if 'curated_2m_portfolio' in lake_data and 'parcels' in lake_data['curated_2m_portfolio']:
        for t in lake_data['curated_2m_portfolio']['parcels']:
            p_clean = t['pin'].replace('-', '')
            coord = geos.get(p_clean)
            if coord:
                lat = coord['lat']
                lng = coord['lng']
                delta = 0.00055
                min_lng = lng - delta
                max_lng = lng + delta
                min_lat = lat - delta * 0.72
                max_lat = lat + delta * 0.72
                img_url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox={min_lng:.6f},{min_lat:.6f},{max_lng:.6f},{max_lat:.6f}&bboxSR=4326&size=180,120&imageSR=4326&format=jpg&f=image"
                t['lat'] = lat
                t['lng'] = lng
                t['photo_url'] = img_url

    with open('lake_presale_targets.json', 'w') as f:
        json.dump(lake_data, f, indent=2)

    print("✅ Saved enriched lake_presale_targets.json successfully!")

if __name__ == '__main__':
    enrich_targets()
