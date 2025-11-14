import re
import time
from typing import Dict, List, Optional

from bs4 import BeautifulSoup  # فعلاً لازم نیست، ولی می‌گذاریم اگر بعداً خواستیم توسعه بدیم
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TABDEAL_URL = "https://tabdeal.org/"

# 👇 این همون مسیریه که گفتی قیمت ریالی BTC توشه:
BTC_IRT_XPATH = '/html/body/div[1]/div/div/div[2]/div/div/div/div/div[1]/section/div/div[2]/div/div[1]/table/tbody/tr[1]/td[2]/div/div[2]/span[2]'


def _create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")  # کمک می‌کند DOM شبیه دسکتاپ شود

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


def fetch_tabdeal_prices(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    """
    گرفتن قیمت تومانی BTC از تبدیل.

    خروجی:
    {
      'BTCIRT': {'price': 11345394301.0, 'change_24h': None},
    }
    """
    driver = _create_driver()
    try:
        driver.get(TABDEAL_URL)

        # منتظر می‌مانیم تا عنصر مربوط به قیمت ریالی BTC ظاهر شود
        wait = WebDriverWait(driver, 15)
        elem = wait.until(EC.presence_of_element_located((By.XPATH, BTC_IRT_XPATH)))

        raw_text = elem.text.strip()
        print(f"[TABDEAL] BTCIRT raw text: {raw_text!r}")

        price_val = _parse_number(raw_text)
        if price_val is None:
            print("[TABDEAL] could not parse BTCIRT price.")
            return {}

        result: Dict[str, Dict[str, float]] = {}
        wanted = {s.upper() for s in symbols}

        if "BTCIRT" in wanted:
            result["BTCIRT"] = {
                "price": price_val,
                "change_24h": None,  # فعلاً درصد تغییر از تبدیل نداریم
            }

        return result

    finally:
        driver.quit()
