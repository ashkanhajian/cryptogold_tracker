from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

class Asset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('crypto', 'Cryptocurrency'),
        ('gold', 'Gold'),
    ]

    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    type = models.CharField(max_length=10, choices=ASSET_TYPE_CHOICES)
    price_usd = models.FloatField()
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.symbol}) - ${self.price_usd}"
