import requests
import re
import json
import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_single_pin_photo(pin, taxpayer):
    pin_clean = pin.replace("-", "")
    out_path = f"data/assessor_photos/{pin_clean}.jpg"
    
    # If already downloaded, skip
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        return {"pin": pin, "status": "cached", "path": out_path}

    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    try:
        r_get = session.get("https://tax.lakecountyil.gov/search/commonsearch.aspx?mode=realprop", timeout=12)
        if r_get.status_code != 200:
            return {"pin": pin, "status": "failed", "reason": f"HTTP {r_get.status_code}"}

        viewstate = re.search(r'id="__VIEWSTATE" value="([^"]+)"', r_get.text).group(1)
        eventval = re.search(r'id="__EVENTVALIDATION" value="([^"]+)"', r_get.text).group(1)

        data = {
            "__VIEWSTATE": viewstate,
            "__EVENTVALIDATION": eventval,
            "ctl00$ContentPlaceHolder1$txtPin": pin_clean,
            "ctl00$ContentPlaceHolder1$btnSearch": "Search"
        }
        session.post("https://tax.lakecountyil.gov/search/commonsearch.aspx?mode=realprop", data=data, timeout=12)
        r_photo = session.get("https://tax.lakecountyil.gov/idoc2/photoview.aspx?sIndex=0&idx=1&LMparent=20", timeout=12)

        token = None
        jur = None
        for line in r_photo.text.split("\n"):
            if "var token" in line:
                m = re.search(r"var token\s*=\s*['\"]([^'\"]+)['\"]", line)
                if m: token = m.group(1)
            if "var jur" in line:
                m = re.search(r"var jur\s*=\s*['\"]([^'\"]+)['\"]", line)
                if m: jur = m.group(1)

        if token and jur:
            api_url = f"https://tax.lakecountyil.gov/api/documents/Parcel%20Photo/{jur}/{pin_clean}?token={token}"
            r_api = session.get(api_url, timeout=12)
            docs = r_api.json() if r_api.status_code == 200 else []
            if docs:
                doc_id = docs[0].get("Id")
                doc_enc = urllib.parse.quote(doc_id)
                img_url = f"https://tax.lakecountyil.gov/api/document/{doc_enc}/standard?token={token}"
                r_img = session.get(img_url, timeout=15)
                if r_img.status_code == 200 and len(r_img.content) > 10000:
                    with open(out_path, "wb") as fp:
                        fp.write(r_img.content)
                    return {"pin": pin, "status": "downloaded", "path": out_path, "bytes": len(r_img.content)}

        return {"pin": pin, "status": "no_photo"}
    except Exception as e:
        return {"pin": pin, "status": "error", "error": str(e)}

def batch_scrape_assessor_photos(limit=60):
    os.makedirs("data/assessor_photos", exist_ok=True)
    with open("lake_presale_targets.json") as f:
        lake_data = json.load(f)

    targets = lake_data.get("top_targets", [])[:limit]
    print(f"🚀 Starting parallel assessor photo scraper for {len(targets)} priority Lake parcels (4 worker threads)...")

    results_map = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_pin = {
            executor.submit(fetch_single_pin_photo, t["pin"], t.get("taxpayer", "")): t["pin"]
            for t in targets
        }
        for future in as_completed(future_to_pin):
            res = future.result()
            pin = res["pin"]
            if res["status"] in ["downloaded", "cached"]:
                results_map[pin] = res["path"]
                print(f"  ✅ [FOUND PHOTO] {pin}: {res.get('bytes', 0):,} bytes")
            elif res["status"] == "no_photo":
                print(f"  ℹ️ [NO PHOTO ON FILE] {pin}")
            else:
                print(f"  ⚠️ [FAILED] {pin}: {res.get('error', res.get('reason'))}")

    # Update lake_presale_targets.json with assessor_photo_path
    for t in lake_data.get("top_targets", []):
        pin = t["pin"]
        pin_clean = pin.replace("-", "")
        local_path = f"data/assessor_photos/{pin_clean}.jpg"
        if os.path.exists(local_path) and os.path.getsize(local_path) > 10000:
            t["assessor_photo"] = local_path
        else:
            t["assessor_photo"] = ""

    with open("lake_presale_targets.json", "w") as f:
        json.dump(lake_data, f, indent=2)

    found_count = len([t for t in lake_data.get("top_targets", []) if t.get("assessor_photo")])
    print(f"\n🎉 Successfully linked {found_count} actual assessor drive-by photos to Lake targets!")

if __name__ == '__main__':
    batch_scrape_assessor_photos(limit=30)
