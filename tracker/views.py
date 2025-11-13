from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Asset

def asset_list(request):
    assets = Asset.objects.order_by('type', 'symbol')
    return render(request, 'tracker/asset_list.html', {'assets': assets})
