from django.contrib import admin
from django.contrib.admin.views import main
from django.conf import settings
from django.utils.safestring import mark_safe
from danowski.apps.geo.models import GeonamesCountry, GeonamesContinent, StateCode, Location
from danowski.apps.people.models import School, Person
from danowski.apps.journals.models import Journal, IssueItem, PlaceName
from danowski.apps.admin.models import LinkedInline, get_admin_url

# admin.site.register(GeonamesContinent)
# admin.site.register(GeonamesCountry)
# admin.site.register(StateCode)

# override django default display value for null values in change list
main.EMPTY_CHANGELIST_VALUE = '-'


class IssueItemInline(LinkedInline):
    model = PlaceName
    extra = 0
    admin_model_parent = "journals"
    admin_model_path = "issueitem"


class LocationAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/admin/collapseTabularInlines.js',)
        css = { 'all' : ('css/admin/admin_styles.css',) }

    list_display = ['street_address', 'city', 'state', 'zipcode', 'country']
    list_display_links = ['street_address', 'city', 'state', 'zipcode', 'country']
    search_fields = ['street_address', 'city', 'state', 'zipcode', 'country']
    inlines = [
        IssueItemInline,
    ]

admin.site.register(Location, LocationAdmin)
