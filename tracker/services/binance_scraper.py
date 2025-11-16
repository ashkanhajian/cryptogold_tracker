import requests
from typing import Dict, List
from requests.exceptions import RequestException

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"


def fetch_binance_prices(pairs: List[str]) -> Dict[str, float]:

    try:
        resp = requests.get(BINANCE_API_URL, timeout=15)
        resp.raise_for_status()
    except RequestException as e:
        print(f"[BINANCE] network error: {e}")
        return {}

    data = resp.json()
    wanted = set(pairs)
    result: Dict[str, float] = {}

    for item in data:
        sym = item.get("symbol")
        if sym in wanted:
            try:
                result[sym] = float(item["price"])
            except (KeyError, ValueError, TypeError):
                continue

    return result
