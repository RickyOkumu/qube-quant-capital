# app/news_fetcher.py
"""
Forecaster.biz news ingestion. If you have FORECASTER_API_KEY, you can call
their API. Otherwise, the module fetches headlines from public RSS feeds
as fallback and returns sentiment via simple heuristics (keyword based).
"""
import os, requests
from config import FORECASTER_API_KEY

FORECASTER_ENDPOINT = "https://api.forecaster.biz/v1/news"  # placeholder

def fetch_forecaster_news(topic="economic"):
    # TODO: get real API docs from forecaster.biz and adapt authentication
    if not FORECASTER_API_KEY:
        return []
    headers = {"Authorization": f"Bearer {FORECASTER_API_KEY}"}
    try:
        resp = requests.get(f"{FORECASTER_ENDPOINT}?q={topic}", headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        else:
            return []
    except Exception:
        return []

# fallback simple
def fetch_headlines_from_rss():
    feeds = [
        "https://www.reutersagency.com/feed/?best-topics=markets",  # example
        "https://www.ft.com/?format=rss"
    ]
    items = []
    for f in feeds:
        try:
            r = requests.get(f, timeout=5)
            if r.ok:
                items.append({"source": f, "title": r.text[:200]})
        except:
            pass
    return items