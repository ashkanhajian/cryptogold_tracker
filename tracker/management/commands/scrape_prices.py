from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from tracker.models import Asset
from tracker.services.fetchers import fetch_crypto_prices, fetch_gold_price_usd, timestamp

class Command(BaseCommand):
    help = "Fetch latest prices for gold and selected cryptocurrencies, then upsert into DB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--cryptos",
            type=str,
            default="btc,eth",
            help="Comma-separated crypto symbols, e.g. 'btc,eth,sol'",
        )
        parser.add_argument(
            "--with-gold",
            action="store_true",
            help="Also fetch gold price (XAUUSD) via web scraping.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        cryptos = [s.strip() for s in options["cryptos"].split(",") if s.strip()]
        with_gold = options["with_gold"]

        updated = 0

        # 1) Crypto
        if cryptos:
            self.stdout.write(self.style.NOTICE(f"Fetching crypto prices for: {', '.join(cryptos)}"))
            try:
                prices = fetch_crypto_prices(cryptos)
                for sym, price in prices.items():
                    Asset.objects.update_or_create(
                        symbol=sym.upper(),
                        defaults={
                            "name": sym.upper(),
                            "type": "crypto",
                            "price_usd": price,
                            "last_updated": timestamp(),
                        },
                    )
                    updated += 1
            except Exception as e:
                raise CommandError(f"Crypto fetch failed: {e}")

        # 2) Gold
        if with_gold:
            self.stdout.write(self.style.NOTICE("Fetching gold price (XAUUSD)..."))
            try:
                gp = fetch_gold_price_usd()
                if gp is None:
                    self.stdout.write(self.style.WARNING("Gold price not found (selector may need update)."))
                else:
                    Asset.objects.update_or_create(
                        symbol="XAU",
                        defaults={
                            "name": "Gold",
                            "type": "gold",
                            "price_usd": gp,
                            "last_updated": timestamp(),
                        },
                    )
                    updated += 1
            except Exception as e:
                raise CommandError(f"Gold fetch failed: {e}")

        self.stdout.write(self.style.SUCCESS(f"Done. Updated: {updated} record(s)."))
