from django.contrib import admin
from django.utils.html import format_html

from ajax_select.admin import AjaxSelectAdmin

from danowski.apps.journals.models import Item
from danowski.apps.people.forms import PersonForm, SchoolForm
from danowski.apps.people.models import School, Person, Name, PenName


class SchoolAdmin(AjaxSelectAdmin):
    form = SchoolForm
    list_display = ['name', 'categorizer', 'location_names']
    search_fields = ['name', 'categorizer', 'notes']
    filter_horizontal = ('locations', )
admin.site.register(School, SchoolAdmin)


class AltNamesInline(admin.TabularInline):
    model = Name
    verbose_name_plural = 'Alternate Names'
    extra = 1

class PenNamesInline(admin.TabularInline):
    model = PenName
    verbose_name_plural = 'Pen Names'
    extra = 1

class ItemInline(admin.TabularInline):
    model = Item.persons_mentioned.through
    extra = 0
    verbose_name = 'Mentioned In Items'
    verbose_name_plural = verbose_name
    exclude = ('item', )
    readonly_fields = ('edit_item', )

    can_delete = False

    def edit_item(self, obj):
        # creator name is edited on issue item
        return format_html(u'<a href="{}">{}</a>',
            obj.item.edit_url, obj.item.title)

    edit_item.short_description = "Item"

    def has_add_permission(self, args):
        # disallow adding mentions from the Person edit form
        return False


class ItemCreatorsInline(admin.TabularInline):
    model = Item.creators.through
    extra = 0
    verbose_name = 'Assigned Creator for Items'
    verbose_name_plural = verbose_name
    exclude = ('issue_item', )
    readonly_fields = ('edit_item', 'name_used')
    can_delete = False

    def edit_item(self, obj):
        # creator name is edited on issue item
        return format_html(u'<a href="{}">{}</a>',
            obj.item.edit_url, obj.item.title)

    edit_item.short_description = "Item"

    def has_add_permission(self, args):
        # disallow adding creator names from the Person edit form
        return False


class PersonAdmin(AjaxSelectAdmin):
    class Media:
        js = ('js/admin/collapseTabularInlines.js',)
        css = { 'all' : ('css/admin/admin_styles.css',) }
    list_display = ['first_name', 'last_name', 'race_label', 'gender', 'uri']
    search_fields = ['first_name', 'last_name', 'race', 'gender', 'notes', 'uri', 'racial_self_description']
    list_display_links = ['first_name', 'last_name']
    filter_horizontal = ('schools', )
    inlines = [
        AltNamesInline,
        PenNamesInline,
        ItemInline,
        ItemCreatorsInline,
    ]
    form = PersonForm

admin.site.register(Person, PersonAdmin)
