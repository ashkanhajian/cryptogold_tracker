import re
import time
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TABDEAL_URL = "https://tabdeal.org/"

# 👇 قیمت ریالی بیت‌کوین
BTC_IRT_XPATH = '/html/body/div[1]/div/div/div[2]/div/div/div/div/div[1]/section/div/div[2]/div/div[1]/table/tbody/tr[1]/td[2]/div/div[2]/span[2]'

# 👇 قیمت ریالی اتریوم (مسیر جدیدی که دادی)
ETH_IRT_XPATH = '/html/body/div[1]/div/div/div[2]/div/div/div/div/div[1]/section/div/div[2]/div/div[1]/table/tbody/tr[2]/td[2]/div/div[2]'


def _create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def _parse_number(text: str) -> Optional[float]:
    """
    متن مثل '11,345,394,301' یا '11,345,394,301 تومان' را به float تبدیل می‌کند.
    """
    if not text:
        return None
    m = re.search(r"[0-9]{1,3}(?:,[0-9]{3})+", text)
    if not m:
        return None
    cleaned = m.group(0).replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _get_price(driver: webdriver.Chrome, xpath: str, label: str) -> Optional[float]:
    try:
        wait = WebDriverWait(driver, 15)
        elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        raw_text = elem.text.strip()
        print(f"[TABDEAL] {label} raw text: {raw_text!r}")
        return _parse_number(raw_text)
    except Exception as e:
        print(f"[TABDEAL] error reading {label}: {e}")
        return None


def fetch_tabdeal_prices(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    """
    فقط قیمت تومانی BTC و ETH را از تبدیل می‌گیرد.

    خروجی:
    {
      'BTCIRT': {'price': ..., 'change_24h': None},
      'ETHIRT': {'price': ..., 'change_24h': None},
    }
    """
    driver = _create_driver()
    try:
        driver.get(TABDEAL_URL)

        wanted = {s.upper() for s in symbols}
        result: Dict[str, Dict[str, float]] = {}

        if "BTCIRT" in wanted:
            btc_price = _get_price(driver, BTC_IRT_XPATH, "BTCIRT")
            if btc_price is not None:
                result["BTCIRT"] = {
                    "price": btc_price,
                    "change_24h": None,
                }

        if "ETHIRT" in wanted:
            eth_price = _get_price(driver, ETH_IRT_XPATH, "ETHIRT")
            if eth_price is not None:
                result["ETHIRT"] = {
                    "price": eth_price,
                    "change_24h": None,
                }

        return result

    finally:
        driver.quit()
