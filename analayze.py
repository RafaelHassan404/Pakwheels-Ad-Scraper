import json
import time
from google import genai
from database import get_listings_needing_analysis, update_pros_cons

client = genai.Client()  # reads GEMINI_API_KEY automatically

def extract_pros_cons(description, retries=3):
    prompt = f"""Read this bike listing description and extract pros and cons as short bullet phrases.
Return ONLY valid JSON, no markdown, no explanation, in this exact format:
{{"pros": ["...", "..."], "cons": ["...", "..."]}}
If there's nothing notable for pros or cons, return an empty list for that key.

Description: {description}"""

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            raw = response.text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)
            pros = json.dumps(data.get("pros", []))
            cons = json.dumps(data.get("cons", []))
            return pros, cons
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))  # 5s, then 10s
    return None, None

def main():
    rows = get_listings_needing_analysis()
    print(f"Found {len(rows)} listings needing analysis.")

    for ad_id, description in rows:
        pros, cons = extract_pros_cons(description)
        if pros is not None:
            update_pros_cons(ad_id, pros, cons)
            print(f"ad_id {ad_id}: done")
        time.sleep(4)  # free tier is ~15 requests/min, stay comfortably under that

    print("Analysis complete.")

if __name__ == "__main__":
    main()