import re
import time
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

NOBITEX_URL = "https://nobitex.ir/"


def _create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def _parse_number(text: str) -> Optional[float]:
    cleaned = re.sub(r"[^0-9,\.]", "", text or "")
    cleaned = cleaned.replace(",", "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_change_percent(row_text: str) -> Optional[float]:

    m = re.search(r"([-+]?\d+(?:\.\d+)?)\s*%", row_text)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def fetch_nobitex_prices(symbols: List[str]) -> Dict[str, Dict[str, float]]:

    driver = _create_driver()
    try:
        driver.get(NOBITEX_URL)
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        result: Dict[str, Dict[str, float]] = {}
        wanted = {s.upper() for s in symbols}

        symbol_keywords = {
            "BTCIRT": ["BTC", "بیت کوین", "بیت‌کوین"],
            "ETHIRT": ["ETH", "اتریوم"],
        }

        for tr in soup.select("table tbody tr"):
            row_text = tr.get_text(" ", strip=True)

            for symbol, keywords in symbol_keywords.items():
                if symbol not in wanted or symbol in result:
                    continue

                if any(kw in row_text for kw in keywords):
                    print(f"[NOBITEX] {symbol} row text: {row_text!r}")


                    numbers = re.findall(r"[0-9]{1,3}(?:,[0-9]{3})*(?:\.\d+)?", row_text)
                    if not numbers:
                        print(f"[NOBITEX] no numeric pattern found in row for {symbol}.")
                        continue

                    price_val = _parse_number(numbers[0])
                    change_val = _parse_change_percent(row_text)

                    if price_val is None:
                        print(f"[NOBITEX] could not parse price for {symbol}.")
                        continue

                    result[symbol] = {
                        "price": price_val,
                        "change_24h": change_val if change_val is not None else 0.0,
                    }

        return result

    finally:
        driver.quit()
