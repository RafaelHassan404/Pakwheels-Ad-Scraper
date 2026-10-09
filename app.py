from flask import Flask, render_template, request, abort
import sqlite3
from math import ceil
import json

PER_PAGE = 50

app = Flask(__name__)

def get_conn():
    conn = sqlite3.connect("file:pakwheels.db?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

@app.template_filter("money")
def money(value):
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return ""

@app.template_filter("fromjson")
def fromjson(value):
    try:
        return json.loads(value) if value else []
    except (TypeError, ValueError):
        return []

@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    year_min = request.args.get("year_min", "").strip()
    year_max = request.args.get("year_max", "").strip()
    price_max = request.args.get("price_max", "").strip()
    status = request.args.get("status", "active").strip()
    page = request.args.get("page", "1").strip()
    page = int(page) if page.isdigit() else 1

    sql = """
        SELECT ad_id, brand, model, year, current_price, mileage,
               location, deal_score, link
        FROM listings
        WHERE 1=1
    """
    params = []

    if q:
        sql += " AND (brand LIKE ? OR model LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if year_min.isdigit():
        sql += " AND year >= ?"
        params.append(int(year_min))
    if year_max.isdigit():
        sql += " AND year <= ?"
        params.append(int(year_max))
    if price_max.isdigit():
        sql += " AND current_price <= ?"
        params.append(int(price_max))
    if status in ("active", "sold"):
        sql += " AND status = ?"
        params.append(status)

    conn = get_conn()

    # how many rows match the filters in total (before paging)
    total = conn.execute(f"SELECT COUNT(*) FROM ({sql})", params).fetchone()[0]
    pages = max(1, ceil(total / PER_PAGE))
    page = max(1, min(page, pages))

    sql += " ORDER BY deal_score DESC, ad_id LIMIT ? OFFSET ?"
    params += [PER_PAGE, (page - 1) * PER_PAGE]
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    # filters to carry over into the Prev/Next links
    args = {"q": q, "year_min": year_min, "year_max": year_max,
            "price_max": price_max, "status": status}

    return render_template("listings.html", rows=rows, total=total,
                           page=page, pages=pages, args=args,
                           q=q, year_min=year_min, year_max=year_max,
                           price_max=price_max, status=status)

@app.route("/listing/<int:ad_id>")
def listing(ad_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM listings WHERE ad_id = ?", [ad_id]).fetchone()
    history = conn.execute(
        "SELECT price, recorded_date FROM price_history "
        "WHERE ad_id = ? ORDER BY recorded_date DESC, id DESC",
        [ad_id]
    ).fetchall()
    conn.close()
    if row is None:
        abort(404)
    return render_template("detail.html", r=row, history=history)

if __name__ == "__main__":
    app.run(debug=True)