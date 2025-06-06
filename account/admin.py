from django.contrib import admin

from .models import Shipment, LiveUpdate, CountryLocation

admin.site.register(Shipment)
admin.site.register(LiveUpdate)
admin.site.register(CountryLocation)
