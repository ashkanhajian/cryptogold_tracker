from tracker.models import Asset
from tracker.services.iranian_scraper import fetch_nobitex_prices
from tracker.services.tabdeal_scraper import fetch_tabdeal_prices
from tracker.services.fetchers import timestamp


def update_all_prices():
    # ✅ Nobitex (همچنان BTCIRT و ETHIRT)
    nobitex_symbols = ["BTCIRT", "ETHIRT"]
    nobitex_data = fetch_nobitex_prices(nobitex_symbols)

    if not nobitex_data:
        print("[UPDATER] Nobitex data empty.")

    for symbol, info in nobitex_data.items():
        Asset.objects.update_or_create(
            symbol=symbol,
            exchange="nobitex",
            defaults={
                "name": symbol,
                "type": "crypto",
                "price_usd": info["price"],
                "currency": "IRT",
                "change_24h": info.get("change_24h"),
                "last_updated": timestamp(),
            },
        )

    # ✅ Tabdeal – فقط قیمت تومانی BTC
    tabdeal_symbols = ["BTCIRT"]
    tabdeal_data = fetch_tabdeal_prices(tabdeal_symbols)

    if not tabdeal_data:
        print("[UPDATER] Tabdeal data empty.")

    for symbol, info in tabdeal_data.items():
        Asset.objects.update_or_create(
            symbol=symbol,
            exchange="tabdeal",
            defaults={
                "name": symbol,
                "type": "crypto",
                "price_usd": info["price"],   # تومانی
                "currency": "IRT",
                "change_24h": info.get("change_24h"),
                "last_updated": timestamp(),
            },
        )

    print("[UPDATER] prices updated from Nobitex + Tabdeal.")
