import sqlite3
from database import DB_FILE, get_sold_listings


def find_best_deals(brand=None, max_price=None, min_deal_score=None, limit=20):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    query = """
        SELECT ad_id, brand, model, year, mileage, current_price, deal_score, location, link
        FROM listings
        WHERE status = 'active'
    """
    params = []

    if brand:
        query += " AND brand LIKE ?"
        params.append(f"%{brand}%")
    if max_price:
        query += " AND current_price <= ?"
        params.append(max_price)
    if min_deal_score is not None:
        query += " AND deal_score >= ?"
        params.append(min_deal_score)

    query += " ORDER BY deal_score DESC NULLS LAST LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def find_by_brand_model(brand, model=None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    query = "SELECT ad_id, brand, model, year, mileage, current_price, deal_score, link FROM listings WHERE status = 'active' AND brand LIKE ?"
    params = [f"%{brand}%"]

    if model:
        query += " AND model LIKE ?"
        params.append(f"%{model}%")

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_price_history(ad_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT price, recorded_date FROM price_history WHERE ad_id = ? ORDER BY recorded_date", (ad_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def print_table(rows, headers):
    if not rows:
        print("No results found.")
        return

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)) if val is not None else 4)

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))

    for row in rows:
        line = " | ".join(str(val if val is not None else "-").ljust(col_widths[i]) for i, val in enumerate(row))
        print(line)

if __name__ == "__main__":
    print("=== Best deals (all bikes) ===")
    deals = find_best_deals()
    print_table(deals, ["ad_id", "brand", "model", "year", "mileage", "price", "deal_score", "location", "link"])

    print("\n=== Example: search by brand ===")
    honda_bikes = find_by_brand_model("Honda")
    print_table(honda_bikes, ["ad_id", "brand", "model", "year", "mileage", "price", "deal_score", "link"])

    print("\n=== Sold listings ===")
    sold = get_sold_listings()
    print_table(sold, ["ad_id", "brand", "model", "year", "price", "sold_date"])