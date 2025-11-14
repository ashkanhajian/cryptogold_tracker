from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from .models import Asset
from .services.updater import update_all_prices


def asset_list(request):

    last_asset = Asset.objects.order_by('-last_updated').first()
    now = timezone.now()

    if (last_asset is None) or (now - last_asset.last_updated > timedelta(seconds=30)):
        update_all_prices()

    nobitex_assets = Asset.objects.filter(exchange='nobitex').order_by('symbol')
    tabdeal_assets = Asset.objects.filter(exchange='tabdeal').order_by('symbol')

    context = {
        'nobitex_assets': nobitex_assets,
        'tabdeal_assets': tabdeal_assets,
    }
    return render(request, 'tracker/asset_list.html', context)
