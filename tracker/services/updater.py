from typing import Dict

from tracker.models import Asset, PriceHistory
from tracker.services.iranian_scraper import fetch_nobitex_prices
from tracker.services.tabdeal_scraper import fetch_tabdeal_prices
from tracker.services.fetchers import timestamp


def update_all_prices() -> None:

    nobitex_symbols = ["BTCIRT", "ETHIRT"]
    nobitex_data: Dict[str, Dict] = fetch_nobitex_prices(nobitex_symbols)

    if not nobitex_data:
        print("[UPDATER] Nobitex data empty.")
    else:
        print(f"[UPDATER] Nobitex data: {nobitex_data}")

    for symbol, info in nobitex_data.items():
        price = info.get("price")
        change_24h = info.get("change_24h")

        if price is None:
            continue

        asset, _ = Asset.objects.update_or_create(
            symbol=symbol,
            exchange="nobitex",
            defaults={
                "name": symbol,
                "type": "crypto",
                "price_usd": price,      # قیمت تومانی
                "currency": "IRT",
                "change_24h": change_24h,
                "last_updated": timestamp(),
            },
        )

        PriceHistory.objects.create(
            asset=asset,
            exchange="nobitex",
            price=price,
            change_24h=change_24h,
        )


    tabdeal_symbols = ["BTCIRT", "ETHIRT"]
    tabdeal_data: Dict[str, Dict] = fetch_tabdeal_prices(tabdeal_symbols)

    if not tabdeal_data:
        print("[UPDATER] Tabdeal data empty.")
    else:
        print(f"[UPDATER] Tabdeal data: {tabdeal_data}")

    for symbol, info in tabdeal_data.items():
        price = info.get("price")
        change_24h = info.get("change_24h")

        if price is None:
            continue

        asset, _ = Asset.objects.update_or_create(
            symbol=symbol,
            exchange="tabdeal",
            defaults={
                "name": symbol,
                "type": "crypto",
                "price_usd": price,      # قیمت تومانی
                "currency": "IRT",
                "change_24h": change_24h,  # فعلاً معمولاً None است
                "last_updated": timestamp(),
            },
        )

        PriceHistory.objects.create(
            asset=asset,
            exchange="tabdeal",
            price=price,
            change_24h=change_24h,
        )

    print("[UPDATER] prices updated from Nobitex + Tabdeal.")
