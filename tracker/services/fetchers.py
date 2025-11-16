import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from django.utils import timezone

COINGECKO_SIMPLE_URL = "https://api.coingecko.com/api/v3/simple/price"

def fetch_crypto_prices(symbols: List[str]) -> Dict[str, float]:


    symbol_to_id = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "bnb": "binancecoin",
        "xrp": "ripple",
        "ada": "cardano",
        "sol": "solana",
        "doge": "dogecoin",
        "ton": "the-open-network",

    }
    ids = []
    for s in symbols:
        sid = symbol_to_id.get(s.lower())
        if sid:
            ids.append(sid)

    if not ids:
        return {}

    params = {"ids": ",".join(ids), "vs_currencies": "usd"}
    r = requests.get(COINGECKO_SIMPLE_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    out = {}
    for sym, sid in symbol_to_id.items():
        if sid in data and "usd" in data[sid]:
            out[sym] = float(data[sid]["usd"])
    return {k: v for k, v in out.items() if k.lower() in [s.lower() for s in symbols]}


def fetch_gold_price_usd() -> Optional[float]:


    url = "https://goldprice.org/"  # صفحه‌ای که قیمت لحظه‌ای نمایش می‌دهد
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")


    candidates = []
    for sel in ["#current-price", ".current-price", ".gold-price", "[data-key='gold-price']"]:
        found = soup.select_one(sel)
        if found and found.get_text(strip=True):
            candidates.append(found.get_text(" ", strip=True))

    text_blob = " ".join(candidates) if candidates else soup.get_text(" ", strip=True)


    m = re.search(r"\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|\d+(?:\.\d+)?)\s*(USD)?", text_blob)
    if not m:
        return None

    raw = m.group(1)
    try:
        return float(raw.replace(",", ""))
    except:
        return None


def timestamp():
    return timezone.now()
