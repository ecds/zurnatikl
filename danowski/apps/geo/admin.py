from django.contrib import admin
from danowski.apps.geo.models import GeonamesCountry, GeonamesContinent, StateCode, Location

# admin.site.register(GeonamesContinent)
# admin.site.register(GeonamesCountry)
# admin.site.register(StateCode)

class LocationAdmin(admin.ModelAdmin):
    list_display = ['street_address', 'city', 'state', 'zipcode', 'country']
    search_fields = ['street_address', 'city', 'state', 'zipcode', 'country']
admin.site.register(Location, LocationAdmin)