from django.contrib import admin
from django.contrib.admin.views import main
from danowski.apps.geo.models import Location
from danowski.apps.journals.models import Journal, IssueItem, PlaceName
from danowski.apps.admin.models import LinkedInline


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
