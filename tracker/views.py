from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Asset, PriceHistory
from django.utils import timezone
from datetime import timedelta
from .services.updater import update_all_prices
def asset_list(request):

    last_asset = Asset.objects.order_by('-last_updated').first()
    now = timezone.now()

    if (last_asset is None) or (now - last_asset.last_updated > timedelta(seconds=30)):
        update_all_prices()

    nobitex_assets = list(Asset.objects.filter(exchange='nobitex').order_by('symbol'))
    tabdeal_assets = list(Asset.objects.filter(exchange='tabdeal').order_by('symbol'))


    symbols = sorted(
        set(a.symbol for a in nobitex_assets) | set(a.symbol for a in tabdeal_assets)
    )

    comparisons = []
    for sym in symbols:
        nobitex = next((a for a in nobitex_assets if a.symbol == sym), None)
        tabdeal = next((a for a in tabdeal_assets if a.symbol == sym), None)

        if not nobitex and not tabdeal:
            continue

        nobitex_price = nobitex.price_usd if nobitex else None
        tabdeal_price = tabdeal.price_usd if tabdeal else None

        cheaper = None
        diff_abs = None
        diff_pct = None

        if nobitex_price is not None and tabdeal_price is not None:
            if nobitex_price < tabdeal_price:
                cheaper = "nobitex"
            elif tabdeal_price < nobitex_price:
                cheaper = "tabdeal"
            else:
                cheaper = "equal"

            diff_abs = abs(nobitex_price - tabdeal_price)
            if min(nobitex_price, tabdeal_price) > 0:
                diff_pct = (diff_abs / min(nobitex_price, tabdeal_price)) * 100

        comparisons.append({
            "symbol": sym,
            "nobitex": nobitex,
            "tabdeal": tabdeal,
            "nobitex_price": nobitex_price,
            "tabdeal_price": tabdeal_price,
            "cheaper": cheaper,
            "diff_abs": diff_abs,
            "diff_pct": diff_pct,
        })

    context = {
        'nobitex_assets': nobitex_assets,
        'tabdeal_assets': tabdeal_assets,
        'comparisons': comparisons,
    }
    return render(request, 'tracker/asset_list.html', context)
def asset_history(request, symbol):
    symbol = symbol.upper()

    last_asset = Asset.objects.order_by('-last_updated').first()
    now = timezone.now()
    if (last_asset is None) or (now - last_asset.last_updated > timedelta(seconds=30)):
        update_all_prices()

    assets_qs = Asset.objects.filter(symbol=symbol)
    if not assets_qs.exists():
        raise Http404("هیچ دارایی‌ای با این نماد پیدا نشد.")

    asset = assets_qs.first()


    history_qs = PriceHistory.objects.filter(asset__symbol=symbol).order_by("timestamp")

    labels = [h.timestamp.strftime("%H:%M:%S") for h in history_qs]
    nobitex_prices = []
    tabdeal_prices = []

    for h in history_qs:
        if h.exchange == "nobitex":
            nobitex_prices.append(h.price)
            tabdeal_prices.append(None)
        elif h.exchange == "tabdeal":
            nobitex_prices.append(None)
            tabdeal_prices.append(h.price)
        else:
            nobitex_prices.append(None)
            tabdeal_prices.append(None)

    context = {
        "asset": asset,
        "symbol": symbol,
        "labels": labels,
        "nobitex_prices": nobitex_prices,
        "tabdeal_prices": tabdeal_prices,
    }
    return render(request, "tracker/asset_history.html", context)