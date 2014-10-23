from django.contrib import admin
from django.conf import settings
from danowski.apps.geo.models import GeonamesCountry, GeonamesContinent, StateCode, Location
from danowski.apps.people.models import School

# admin.site.register(GeonamesContinent)
# admin.site.register(GeonamesCountry)
# admin.site.register(StateCode)

class SchoolInline(admin.TabularInline):
    model = School
    extra = 0

class LocationAdmin(admin.ModelAdmin):
    class Media:
      js = (settings.STATIC_URL + 'js/admin/collapseTabularInlines.js',)
     
    list_display = ['street_address', 'city', 'state', 'zipcode', 'country']
    search_fields = ['street_address', 'city', 'state', 'zipcode', 'country']
    inlines = [SchoolInline]
    
admin.site.register(Location, LocationAdmin)
