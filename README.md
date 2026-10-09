# PakWheels Ad Scraper

A personal tool that scrapes the ads you have saved on PakWheels, stores them in a local SQLite database, scores each listing against the market median, and lets you browse everything in a local web app.

> **Heads up:** scraping may be against PakWheels' terms of service. Use this for personal, low-volume purposes only. Your session cookie is private: never commit it or paste it anywhere public.

## Features

- Scrapes your saved ads on PakWheels (sequential requests, descriptions fetched only for new ads)
- SQLite storage with price history and sold-listing detection
- Deal score: how far each price is below the median for the same brand, model and year (needs at least 3 comparable listings)
- Optional Gemini analysis that extracts pros and cons from each description
- Excel export with color-coded rows
- Local web app: search, filters, pagination and a detail page per listing

## Setup

```powershell
git clone https://github.com/RafaelHassan404/Pakwheels-Ad-Scraper.git
cd Pakwheels-Ad-Scraper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 1. Add your own session cookie

Log in to PakWheels in your browser, copy your session cookie, and save it as a single line in a file named `cookie.txt` in the project folder. This file is git-ignored. The scraper reads the saved ads of whichever account the cookie belongs to.

### 2. (Optional) Add a Gemini API key

Only needed for `analyze.py`. Get a key from Google AI Studio and set it as an environment variable:

```powershell
$env:GEMINI_API_KEY = "your-key-here"
```

## Usage

```powershell
python Scraper.py     # scrape saved ads, update the database, export Excel
python analyze.py     # optional: add pros/cons with Gemini
python query.py       # command-line listing queries
python app.py         # web app at http://127.0.0.1:5000
```

Run `Scraper.py` at least once before `app.py`, because the web app reads `pakwheels.db`, which the scraper creates.

In `Scraper.py`, `max_pages` controls how many pages are scraped. Use `float("inf")` for a full run. Sold-listing detection only runs when the scraper reaches the end of your saved ads, so partial test runs never mark listings as sold.

## Project files

| File | Purpose |
| --- | --- |
| `Scraper.py` | Main scraping workflow |
| `database.py` | SQLite operations, market values, deal scores, Excel export |
| `query.py` | Command-line listing queries |
| `analyze.py` | Gemini pros/cons analysis (separate from the scraper) |
| `app.py` | Local Flask web app (read-only access to the database) |
| `templates/` | HTML templates for the web app |

## Privacy

`cookie.txt`, `pakwheels.db`, `pakwheels_report.xlsx` and `.env` are git-ignored. Keep it that way, and never share your cookie or API key.