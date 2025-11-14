import re
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

TABDEAL_URL = "https://tabdeal.org/"


def _create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _parse_number(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"[0-9]{1,3}(?:,[0-9]{3})+", text)
    if not m:
        return None
    cleaned = m.group(0).replace(",", "")
    try:
        return float(cleaned)
    except:
        return None


def _parse_percent(text: str) -> Optional[float]:
    m = re.search(r"([-+]?\d+(?:\.\d+)?)\s*%", text)
    if not m:
        return None
    try:
        return float(m.group(1))
    except:
        return None


def fetch_tabdeal_prices(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    driver = _create_driver()
    try:
        driver.get(TABDEAL_URL)
        time.sleep(6)

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        rows = soup.select("table tbody tr")
        result = {}
        wanted = set(symbols)

        for tr in rows:
            text = tr.get_text(" ", strip=True)

            # BTC تومانی
            if "BTC" in text or "بیت کوین" in text:
                price = _parse_number(text)
                change = _parse_percent(text)
                if "BTCIRT" in wanted and price:
                    result["BTCIRT"] = {
                        "price": price,
                        "change_24h": change if change is not None else 0.0,
                    }
                    continue

            # ETH تومانی
            if "ETH" in text or "اتریوم" in text:
                price = _parse_number(text)
                change = _parse_percent(text)
                if "ETHIRT" in wanted and price:
                    result["ETHIRT"] = {
                        "price": price,
                        "change_24h": change if change is not None else 0.0,
                    }
                    continue

        return result

    finally:
        driver.quit()
