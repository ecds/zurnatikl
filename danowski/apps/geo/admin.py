from django.contrib import admin
from django.contrib.admin.views import main
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from danowski.apps.geo.models import Location
from danowski.apps.journals.models import Journal, IssueItem, PlaceName
from danowski.apps.admin.models import LinkedInline


# override django default display value for null values in change list
main.EMPTY_CHANGELIST_VALUE = '-'


class IssueItemInline(admin.TabularInline):
    model = PlaceName
    extra = 0
    exclude = ('issueItem', )  # hide since title is repeated in edit_issue_item
    readonly_fields = ('name', 'edit_issue_item',)
    can_delete = False

    def has_add_permission(self, args):
        # disallow adding placenames from the Location edit form
        return False


class LocationAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/admin/collapseTabularInlines.js',)
        css = { 'all' : ('css/admin/admin_styles.css',) }

    list_display = ['street_address', 'city', 'state', 'zipcode', 'country']
    list_display_links = ['street_address', 'city', 'state', 'zipcode', 'country']
    search_fields = ['street_address', 'city', 'state__name', 'state__code',
                     'zipcode', 'country__name', 'country__code',
                     'placename__name', 'placename__issueItem__title']
    inlines = [
        IssueItemInline,
    ]

admin.site.register(Location, LocationAdmin)
