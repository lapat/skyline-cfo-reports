import requests
import re
import json
import os
import urllib.parse

def test_batch():
    with open("lake_presale_targets.json") as f:
        lake_data = json.load(f)

    targets = lake_data.get("top_targets", [])[:8]
    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

    os.makedirs("data/assessor_photos", exist_ok=True)
    results = {}

    for idx, t in enumerate(targets):
        pin = t["pin"]
        tp = t.get("taxpayer", "")
        pin_clean = pin.replace("-", "")
        print(f"[{idx+1}/8] Checking PIN: {pin} ({tp})...")
        
        session = requests.Session()
        session.headers.update({"User-Agent": UA})
        
        try:
            r_get = session.get("https://tax.lakecountyil.gov/search/commonsearch.aspx?mode=realprop", timeout=10)
            viewstate = re.search(r'id="__VIEWSTATE" value="([^"]+)"', r_get.text).group(1)
            eventval = re.search(r'id="__EVENTVALIDATION" value="([^"]+)"', r_get.text).group(1)
            
            data = {
                "__VIEWSTATE": viewstate,
                "__EVENTVALIDATION": eventval,
                "ctl00$ContentPlaceHolder1$txtPin": pin_clean,
                "ctl00$ContentPlaceHolder1$btnSearch": "Search"
            }
            r_search = session.post("https://tax.lakecountyil.gov/search/commonsearch.aspx?mode=realprop", data=data, timeout=10)
            
            r_photo = session.get("https://tax.lakecountyil.gov/idoc2/photoview.aspx?sIndex=0&idx=1&LMparent=20", timeout=10)
            
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
                r_api = session.get(api_url, timeout=10)
                
                docs = r_api.json() if r_api.status_code == 200 else []
                if docs:
                    doc_id = docs[0].get("Id")
                    doc_enc = urllib.parse.quote(doc_id)
                    img_url = f"https://tax.lakecountyil.gov/api/document/{doc_enc}/standard?token={token}"
                    r_img = session.get(img_url, timeout=15)
                    if r_img.status_code == 200 and len(r_img.content) > 10000:
                        out_path = f"data/assessor_photos/{pin_clean}.jpg"
                        with open(out_path, "wb") as fp:
                            fp.write(r_img.content)
                        print(f"  ✅ Found Assessor Street Photo: {len(r_img.content):,} bytes -> {out_path}")
                        results[pin] = out_path
                    else:
                        print("  ⚠️ Photo endpoint returned error")
                else:
                    print("  ℹ️ No assessor street photo on file for this PIN")
            else:
                print("  ⚠️ Could not parse token/jur")
        except Exception as e:
            print("  ❌ Error:", e)

    print(f"\nFinished test batch: {len(results)} / 8 had actual assessor drive-by photos!")

if __name__ == '__main__':
    test_batch()
