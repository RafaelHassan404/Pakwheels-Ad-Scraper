from database import export_to_excel, init_db, save_listings, mark_sold_listings, init_market_values, refresh_market_values, refresh_deal_scores, get_existing_ad_ids

import requests
import json
import time
from bs4 import BeautifulSoup


with open("cookie.txt", "r") as f:
    COOKIE_STRING = f.read().strip()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Cookie": COOKIE_STRING,
}

session = requests.Session()
session.headers.update(HEADERS)

def parse_card(card):
    data = {}
    script_tag = card.select_one('script[type="application/ld+json"]')
    if script_tag:
        try:
            ld = json.loads(script_tag.string)
            data["Brand"] = ld.get("brand", {}).get("name")
            data["Model"] = ld.get("model")
            data["Year"] = ld.get("modelDate")
            data["Mileage"] = ld.get("mileageFromOdometer")
            data["Engine_Type"] = ld.get("vehicleEngine", {}).get("engineType")
            data["Price_PKR"] = ld.get("offers", {}).get("price")
            data["Link"] = ld.get("offers", {}).get("url")
            data["Image_URL"] = ld.get("image")
        except (json.JSONDecodeError, AttributeError):
            pass

    location_el = card.select_one("ul.search-vehicle-info li")
    data["Location"] = location_el.get_text(strip=True) if location_el else None

    updated_el = card.select_one(".dated")
    data["Last_Updated"] = updated_el.get_text(strip=True) if updated_el else None

    return data

def get_description(link):
    try:
        resp = session.get(link, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        heading = soup.find("h2", id="scroll_seller_comments")
        if heading:
            desc_div = heading.find_next_sibling("div")
            if desc_div:
                text = desc_div.get_text(strip=True, separator=" ")
                return text.replace("Mention PakWheels.com when calling Seller to get a good deal", "").strip()
        return ""
    except Exception as e:
        print(f"Failed to get description for {link}: {e}")
        return ""

def get_all_listings():
    all_listings = []
    page = 1
    existing_ids = get_existing_ad_ids()
    new_count = 0
    skipped_count = 0

    # max_pages = 1  #used for testing, comment out for full scrape
    reached_end = False

    while True: #change True to page < maxpages for testing
        url = f"https://www.pakwheels.com/users/saved-ads?page={page}"
        resp = session.get(url, timeout=15)
        
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.select("li.classified-listing")
        if not cards:
            reached_end = True
            break

        print(f"Page {page}: found {len(cards)} listings")
        for card in cards:
            item = parse_card(card)
            ad_id = None
            if item.get("Link"):
                try:
                    ad_id = int(item["Link"].rstrip("/").split("-")[-1])
                except ValueError:
                    ad_id = None

            if ad_id is not None and ad_id in existing_ids:
                skipped_count += 1
                item["Description"] = None  # keep old description untouched in save_listings
            elif item.get("Link"):
                item["Description"] = get_description(item["Link"])
                new_count += 1
                time.sleep(0.5)

            all_listings.append(item)

        page += 1
        time.sleep(0.5)

    print(f"New descriptions fetched: {new_count}, skipped (already saved): {skipped_count}")
    return all_listings, reached_end


listings,reached_end = get_all_listings()
init_db()
init_market_values()
seen_ids = save_listings(listings)
if reached_end and listings:
    mark_sold_listings(seen_ids)
else:
    print("Did not reach the end of listings, not marking any as sold.")
refresh_market_values()
refresh_deal_scores()
export_to_excel()