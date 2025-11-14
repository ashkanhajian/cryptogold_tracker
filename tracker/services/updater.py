from tracker.models import Asset
from tracker.services.iranian_scraper import fetch_nobitex_prices
from tracker.services.tabdeal_scraper import fetch_tabdeal_prices
from tracker.services.fetchers import timestamp


def update_all_prices():
    # Nobitex ...
    nobitex_symbols = ["BTCIRT", "ETHIRT"]
    nobitex_data = fetch_nobitex_prices(nobitex_symbols)
    # ... (همون قبلی)

    # ✅ Tabdeal
    tabdeal_symbols = ["BTCIRT", "ETHIRT"]
    tabdeal_data = fetch_tabdeal_prices(tabdeal_symbols)

    for symbol, info in tabdeal_data.items():
        Asset.objects.update_or_create(
            symbol=symbol,
            exchange="tabdeal",
            defaults={
                "name": symbol,
                "type": "crypto",
                "currency": "IRT",
                "price_usd": info["price"],
                "change_24h": info["change_24h"],
                "last_updated": timestamp(),
            },
        )

    print("[UPDATER] prices updated from Nobitex + Tabdeal.")
