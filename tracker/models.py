from django.db import models
from django.utils import timezone


class Asset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('crypto', 'Cryptocurrency'),
        ('gold', 'Gold'),
    ]

    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    type = models.CharField(max_length=10, choices=ASSET_TYPE_CHOICES)


    price_usd = models.FloatField()

    change_24h = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')

    last_updated = models.DateTimeField(default=timezone.now)
    exchange = models.CharField(max_length=50, default='global')

    class Meta:
        unique_together = ('symbol', 'exchange')

    def __str__(self):
        return f"{self.exchange} - {self.name} ({self.symbol}) {self.price_usd} {self.currency}"
