# tracker/management/commands/scrape_prices.py
from django.core.management.base import BaseCommand
from tracker.services.updater import update_all_prices


class Command(BaseCommand):
    help = "Fetch prices from exchanges and store them."

    def handle(self, *args, **options):
        update_all_prices()
        self.stdout.write(self.style.SUCCESS("Prices updated."))
