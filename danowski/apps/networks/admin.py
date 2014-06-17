from django.contrib import admin
from danowski.apps.networks.models import Location, School


class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'street_address', 'city', 'state', 'zipcode', 'country']
    search_fields = ['street_address', 'city', 'state', 'zipcode', 'country']
    list_display_linksf = ['id']
admin.site.register(Location, LocationAdmin)


class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'categorizer', 'location', 'notes']
    search_fields = ['name', 'categorizer', 'notes']
admin.site.register(School, SchoolAdmin)
