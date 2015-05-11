from django.contrib import admin
from django.contrib.admin.views import main
from django.utils.html import format_html

from danowski.apps.geo.models import Location
from danowski.apps.journals.models import PlaceName


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

    def edit_issue_item(self, obj):
        # creator name is edited on issue item
        return format_html(u'<a href="{}">{}</a>',
            obj.issueItem.edit_url, obj.issueItem.title)

    edit_issue_item.short_description = "Issue Item"


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
    change_form_template = 'geo/admin/location_change_form.html'

admin.site.register(Location, LocationAdmin)
