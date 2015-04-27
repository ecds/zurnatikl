from django.contrib import admin
from django.utils.html import format_html

from danowski.apps.journals.models import IssueItem
from danowski.apps.people.forms import PersonForm, SchoolForm
from danowski.apps.people.models import School, Person, Name, PenName


class SchoolAdmin(admin.ModelAdmin):
    form = SchoolForm
    list_display = ['name', 'categorizer', 'location']
    search_fields = ['name', 'categorizer', 'notes']
admin.site.register(School, SchoolAdmin)


class AltNamesInline(admin.TabularInline):
    model = Name
    verbose_name_plural = 'Alternate Names'
    extra = 1

class PenNamesInline(admin.TabularInline):
    model = PenName
    verbose_name_plural = 'Pen Names'
    extra = 1

class IssueItemInline(admin.TabularInline):
    model = IssueItem.persons_mentioned.through
    extra = 0
    verbose_name = 'Mentioned In Issue Items'
    verbose_name_plural = verbose_name
    exclude = ('issueitem', )
    readonly_fields = ('edit_issue_item', )

    can_delete = False

    def edit_issue_item(self, obj):
        # creator name is edited on issue item
        return format_html(u'<a href="{}">{}</a>',
            obj.issueitem.edit_url, obj.issueitem.title)

    edit_issue_item.short_description = "Issue Item"

    def has_add_permission(self, args):
        # disallow adding mentions from the Person edit form
        return False


class IssueItemCreatorsInline(admin.TabularInline):
    model = IssueItem.creators.through
    extra = 0
    verbose_name = 'Assigned Creator for Issue Items'
    verbose_name_plural = verbose_name
    exclude = ('issue_item', )
    readonly_fields = ('edit_issue_item', 'name_used')
    can_delete = False

    def edit_issue_item(self, obj):
        # creator name is edited on issue item
        return format_html(u'<a href="{}">{}</a>',
            obj.issue_item.edit_url, obj.issue_item.title)

    edit_issue_item.short_description = "Issue Item"

    def has_add_permission(self, args):
        # disallow adding creator names from the Person edit form
        return False


class PersonAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/admin/collapseTabularInlines.js',)
        css = { 'all' : ('css/admin/admin_styles.css',) }
    list_display = ['first_name', 'last_name', 'race', 'gender', 'uri']
    search_fields = ['first_name', 'last_name', 'race', 'gender', 'notes', 'uri', 'racial_self_description']
    list_display_links = ['first_name', 'last_name']
    inlines = [
        AltNamesInline,
        PenNamesInline,
        IssueItemInline,
        IssueItemCreatorsInline,
    ]
    form = PersonForm

admin.site.register(Person, PersonAdmin)
